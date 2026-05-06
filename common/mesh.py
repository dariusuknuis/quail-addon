import bpy, bmesh
from math import pi
from .s3dobject import get_collision_volume_material

def get_vertex_normal_nodegroup():

    name="VERTEX_NORMALS"

    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]

    mat = get_collision_volume_material()

    group = bpy.data.node_groups.new(name, "GeometryNodeTree")
    nodes = group.nodes
    links = group.links
    nodes.clear()

    # ------------------------------------------------
    # INTERFACE
    # ------------------------------------------------
    group.interface.new_socket(
        name="Geometry",
        in_out='INPUT',
        socket_type='NodeSocketGeometry'
    )

    group.interface.new_socket(
        name="Show Normals",
        in_out='INPUT',
        socket_type='NodeSocketBool'
    )

    group.interface.new_socket(
        name="Geometry",
        in_out='OUTPUT',
        socket_type='NodeSocketGeometry'
    )

    # ------------------------------------------------
    # INPUT / OUTPUT
    # ------------------------------------------------
    group_in = nodes.new("NodeGroupInput")
    group_in.location = (-1200, 0)

    group_out = nodes.new("NodeGroupOutput")
    group_out.location = (600, 0)

    # ------------------------------------------------
    # Named Attribute (vertex_normals)
    # ------------------------------------------------
    n_attr = nodes.new("GeometryNodeInputNamedAttribute")
    n_attr.location = (-1000, -200)
    n_attr.data_type = 'FLOAT_VECTOR'
    n_attr.inputs["Name"].default_value = "vertex_normals"

    # ------------------------------------------------
    # Set Mesh Normal (ALWAYS ACTIVE)
    # ------------------------------------------------
    n_set_normal = nodes.new("GeometryNodeSetMeshNormal")
    n_set_normal.location = (-700, 0)
    n_set_normal.mode = 'FREE'
    n_set_normal.domain = 'POINT'

    links.new(group_in.outputs["Geometry"], n_set_normal.inputs["Mesh"])
    links.new(n_attr.outputs["Attribute"], n_set_normal.inputs["Custom Normal"])

    # ------------------------------------------------
    # MESH → POINTS (for rods)
    # ------------------------------------------------
    n_mesh2pts = nodes.new("GeometryNodeMeshToPoints")
    n_mesh2pts.location = (-700, 200)
    n_mesh2pts.mode = 'VERTICES'

    links.new(n_set_normal.outputs["Mesh"], n_mesh2pts.inputs["Mesh"])

    # ------------------------------------------------
    # ALIGN ROTATION TO NORMAL
    # ------------------------------------------------
    n_align = nodes.new("FunctionNodeAlignRotationToVector")
    n_align.location = (-500, 0)
    n_align.axis = 'Z'

    links.new(n_attr.outputs["Attribute"], n_align.inputs["Vector"])

    # ------------------------------------------------
    # LINE (normal rod)
    # ------------------------------------------------
    n_line = nodes.new("GeometryNodeCurvePrimitiveLine")
    n_line.location = (-500, 300)
    n_line.mode = 'POINTS'

    # ------------------------------------------------
    # INSTANCE ON POINTS
    # ------------------------------------------------
    n_inst = nodes.new("GeometryNodeInstanceOnPoints")
    n_inst.location = (-200, 200)

    links.new(n_mesh2pts.outputs["Points"], n_inst.inputs["Points"])
    links.new(n_line.outputs["Curve"], n_inst.inputs["Instance"])
    links.new(n_align.outputs["Rotation"], n_inst.inputs["Rotation"])

    # scale of rods
    n_inst.inputs["Scale"].default_value = (0.25, 0.25, 0.25)

    # ------------------------------------------------
    # PROFILE (make rods visible)
    # ------------------------------------------------
    n_circle = nodes.new("GeometryNodeCurvePrimitiveCircle")
    n_circle.location = (-200, 0)
    n_circle.inputs["Radius"].default_value = 0.003
    n_circle.inputs["Resolution"].default_value = 4

    # ------------------------------------------------
    # CURVE → MESH
    # ------------------------------------------------
    n_curve2mesh = nodes.new("GeometryNodeCurveToMesh")
    n_curve2mesh.location = (0, 150)

    links.new(n_inst.outputs["Instances"], n_curve2mesh.inputs["Curve"])
    links.new(n_circle.outputs["Curve"], n_curve2mesh.inputs["Profile Curve"])

    # ------------------------------------------------
    # SET MATERIAL (reuse collider material)
    # ------------------------------------------------
    n_setmat = nodes.new("GeometryNodeSetMaterial")
    n_setmat.location = (200, 150)

    if mat:
        n_setmat.inputs["Material"].default_value = mat

    links.new(n_curve2mesh.outputs["Mesh"], n_setmat.inputs["Geometry"])

    # ------------------------------------------------
    # JOIN (base mesh + rods)
    # ------------------------------------------------
    n_join = nodes.new("GeometryNodeJoinGeometry")
    n_join.location = (350, 50)

    links.new(n_set_normal.outputs["Mesh"], n_join.inputs["Geometry"])
    links.new(n_setmat.outputs["Geometry"], n_join.inputs["Geometry"])

    # ------------------------------------------------
    # SWITCH (toggle rods)
    # ------------------------------------------------
    n_switch = nodes.new("GeometryNodeSwitch")
    n_switch.location = (500, 50)
    n_switch.input_type = 'GEOMETRY'

    # FALSE → base mesh only
    links.new(n_set_normal.outputs["Mesh"], n_switch.inputs[1])

    # TRUE → mesh + rods
    links.new(n_join.outputs["Geometry"], n_switch.inputs[2])

    links.new(group_in.outputs["Show Normals"], n_switch.inputs["Switch"])

    # ------------------------------------------------
    # OUTPUT
    # ------------------------------------------------
    links.new(n_switch.outputs["Output"], group_out.inputs["Geometry"])

    return group

def cleanup_mesh_geometry(bm, area_threshold=1e-10, dissolve_dist=1e-4, max_passes=8):
    """
    Iteratively deletes loose verts/edges, degenerate faces,
    and performs dissolve_degenerate until no more geometry can be removed.
    Operates in-place on the given mesh.
    """
    for _ in range(max_passes):
        changed = False

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        # 1. Delete loose verts/edges and degenerate faces
        loose_verts = [v for v in bm.verts if not v.link_edges]
        loose_edges = [e for e in bm.edges if not e.link_faces]
        degenerate_faces = [f for f in bm.faces if f.calc_area() < area_threshold]

        geom_to_delete = loose_verts + loose_edges + degenerate_faces

        if geom_to_delete:
            if loose_edges or (loose_verts and degenerate_faces):
                context = 'EDGES'
            elif degenerate_faces:
                context = 'FACES'
            else:
                context = 'VERTS'
            bmesh.ops.delete(bm, geom=geom_to_delete, context=context)
            changed = True

        # 2. Dissolve degenerate geometry
        res = bmesh.ops.dissolve_degenerate(bm, dist=dissolve_dist, edges=list(bm.edges))
        if res and any(res.get(k) for k in ('edges', 'verts', 'faces')):
            changed = True

        if not changed:
            break

def mesh_boundary_cleanup(bm, thin_thresh=0.001, angle_tol=1e-3):
    """
    In-place on `bm`:
      1) Dissolve vertices on any face whose thinness ratio ≤ thin_thresh,
         but only those vertices that have exactly 2 incident edges.
      2) Rebuild lookup tables.
      3) Dissolve any boundary-vert with exactly 2 boundary edges that are nearly colinear
         (dot(d1,d2) ≈ -1 within angle_tol).
    Returns the modified bm.
    """
    # ——— Pass 1: thin-face vertices ———
    bm.faces.ensure_lookup_table()
    thin_verts = set()
    for f in bm.faces:
        # area & perimeter
        area = f.calc_area()
        peri = 0.0
        verts = f.verts
        n = len(verts)
        for i in range(n):
            peri += (verts[i].co - verts[(i+1)%n].co).length
        tr = (4.0*pi*area)/(peri*peri) if peri > 0 else 0.0
        if tr <= thin_thresh:
            for v in verts:
                if len(v.link_edges) == 2:
                    thin_verts.add(v)

    if thin_verts:
        bmesh.ops.dissolve_verts(bm,
                                 verts=list(thin_verts),
                                 use_face_split=False)

    # ——— Refresh normals & tables ———
    # bm.normal_update()
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    # ——— Pass 2: colinear boundary vertices ———
    col_verts = []
    eps = angle_tol
    for v in bm.verts:
        if len(v.link_edges) != 2:
            continue
        # pick out the two boundary edges
        b_edges = [e for e in v.link_edges if len(e.link_faces) == 1]
        if len(b_edges) != 2:
            continue

        v1 = b_edges[0].other_vert(v)
        v2 = b_edges[1].other_vert(v)
        d1 = (v1.co - v.co)
        d2 = (v2.co - v.co)
        if d1.length == 0 or d2.length == 0:
            continue
        if abs(d1.normalized().dot(d2.normalized()) + 1.0) < eps:
            col_verts.append(v)

    if col_verts:
        bmesh.ops.dissolve_verts(bm,
                                 verts=col_verts,
                                 use_face_split=False)

    return bm