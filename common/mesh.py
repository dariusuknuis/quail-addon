import bpy, bmesh
from mathutils import Vector
from math import pi
from collections import deque
from .s3dobject import get_collision_volume_material


def bmesh_from_mesh(obj):

    if not obj or obj.type != 'MESH':
            raise RuntimeError("limited_dissolve_by_vertex_color: Please pass a mesh object.")

    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)

    return bm

def mesh_from_bmesh(bm, mesh):
    me = mesh.data
    bm.to_mesh(me)
    me.update()

    bm.free()

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

def rearrange_uvs(bm, tol=1e-6):
    """
    Given a BMesh `bm`, flood‐fill vertex‐based UV chunks and integer‐tile‐align them.
    If no UV map is present, returns `bm` unmodified.
    """
    # 1) Grab active UV layer, bail early if none
    luv = bm.loops.layers.uv.active
    if not luv:
        print("No UV map found; skipping UV stitching.")
        return bm

    # 2) Helpers
    def loc_key(v):
        return (round(v.co.x,6), round(v.co.y,6), round(v.co.z,6))
    def raw_uv(v):
        l = next(iter(v.link_loops))
        u, vv = l[luv].uv
        return (round(u,3), round(vv,3))
    def frac_uv(raw):
        return (raw[0] % 1.0, raw[1] % 1.0)

    # 3) Precompute per-vertex lookups
    pos_groups = {}   # loc_key → [verts]
    vert_loc   = {}   # vert → loc_key
    vert_raw   = {}   # vert → raw_uv
    vert_mat   = {}   # vert → material_index
    for v in bm.verts:
        lk = loc_key(v)
        pos_groups.setdefault(lk, []).append(v)
        vert_loc[v] = lk
        vert_raw[v] = raw_uv(v)
        vert_mat[v] = v.link_loops[0].face.material_index

    # 4) Phase 1: vertex-seeded BFS chunks
    seen   = set()
    chunks = []
    for seed in bm.verts:
        if seed in seen:
            continue
        chunk_vs = {seed}
        queue    = deque([seed])
        while queue:
            v = queue.popleft()
            # face-adjacency
            for e in v.link_edges:
                v2 = e.other_vert(v)
                if v2 not in chunk_vs:
                    chunk_vs.add(v2)
                    queue.append(v2)
            # UV-adjacency at same loc + exact raw + same material
            u0, m0 = vert_raw[v], vert_mat[v]
            for v2 in pos_groups[vert_loc[v]]:
                if (v2 not in chunk_vs
                    and vert_mat[v2]==m0
                    and vert_raw[v2]==u0):
                    chunk_vs.add(v2)
                    queue.append(v2)
        # collect loops and loc maps for merging
        chunk_ls = {l for v in chunk_vs for l in v.link_loops}
        loc_map  = {vert_loc[v]: v for v in chunk_vs}
        locs     = set(loc_map)
        chunks.append({
            "verts":   chunk_vs,
            "loops":   chunk_ls,
            "loc_map": loc_map,
            "locs":    locs,
        })
        seen |= chunk_vs

    # 5) Phase 2: merge & integer-align pairwise
    i = 0
    while i < len(chunks):
        base = chunks[i]
        merged_any = True
        while merged_any:
            merged_any = False
            for j in range(i+1, len(chunks)):
                other = chunks[j]
                common = base["locs"] & other["locs"]
                if not common:
                    continue
                for loc in common:
                    vb = base["loc_map"][loc]
                    vo = other["loc_map"][loc]
                    if vert_mat[vb] != vert_mat[vo]:
                        continue
                    fa = frac_uv(vert_raw[vb])
                    fb = frac_uv(vert_raw[vo])
                    if abs(fa[0]-fb[0])>tol or abs(fa[1]-fb[1])>tol:
                        continue
                    # compute integer offset
                    ru, rv = vert_raw[vb], vert_raw[vo]
                    delta  = Vector((ru[0]-rv[0], ru[1]-rv[1]))
                    di     = Vector((round(delta.x), round(delta.y)))
                    if di.length_squared:
                        # shift other chunk UVs
                        for l in other["loops"]:
                            l[luv].uv += di
                        # update raw_uv
                        for v3 in other["verts"]:
                            u3, v3y = vert_raw[v3]
                            vert_raw[v3] = (u3 + di.x, v3y + di.y)
                    # merge other into base
                    base["verts"].update(other["verts"])
                    base["loops"].update(other["loops"])
                    base["loc_map"].update(other["loc_map"])
                    base["locs"].update(other["locs"])
                    del chunks[j]
                    merged_any = True
                    break
                if merged_any:
                    break
        i += 1

    return bm

def merge_verts_by_attrs(bm,
                         vcol_name=None,
                         float_vec_name="vertex_normals",
                         tol=1e-6):
    """
    Merge co-located verts in `bm` that share:
      • the same material on all loops,
      • the same UV on all loops (active UV map),
      • the same vertex-color on all loops (per-vertex or per-loop),
      • a float_vector layer whose quantized indices differ by at most 1.

    `tol` controls the positional snapping tolerance for merging.
    """
    # — quantizers —
    def quantize_255(c):
        i = int(round(c * 255.0))
        return max(0, min(255, i))

    def quantize_127(c):
        i = int(round(c * 127.0))
        return max(-127, min(127, i))

    # — get layers —
    luv = bm.loops.layers.uv.active
    if not luv:
        return bm  # no UV → nothing to do

    # point-domain vertex colors only
    vcol_layer = (
        bm.verts.layers.color.get(vcol_name)
        or bm.verts.layers.float_color.get(vcol_name)
        if vcol_name else
        next(iter(bm.verts.layers.color.values()), None)
        or next(iter(bm.verts.layers.float_color.values()), None)
    )

    if not vcol_layer:
        raise RuntimeError("No point-domain vertex color layer found")

    # float_vector (per-loop)
    vec_layer = bm.verts.layers.float_vector.get(float_vec_name)
    if not vec_layer:
        raise RuntimeError(f"No vertex float_vector layer found: {float_vec_name!r}")

    # — helpers to pull per-vert / per-loop values —
    def pos_key(v):
        return (round(v.co.x,6), round(v.co.y,6), round(v.co.z,6))

    def loop_uv(l):
        return (round(l[luv].uv.x,6), round(l[luv].uv.y,6))

    def vert_color(v):
        col = v[vcol_layer]
        return tuple(quantize_255(c) for c in col)

    def vert_vec_index(v):
        x, y, z = v[vec_layer]
        return (
            quantize_127(x),
            quantize_127(y),
            quantize_127(z),
        )

    # — 1) bucket by everything except the float‑vector —
    buckets = {}
    for v in bm.verts:
        p    = pos_key(v)
        mats = {l.face.material_index for l in v.link_loops}
        uvs  = {loop_uv(l)    for l in v.link_loops}
        cols = {vert_color(v)}

        if len(mats)!=1 or len(uvs)!=1 or len(cols)!=1:
            continue

        key = (p, mats.pop(), uvs.pop(), cols.pop())
        buckets.setdefault(key, []).append(v)

    # — 2) within each bucket, cluster by vec‐indices ±1 —
    for verts in buckets.values():
        if len(verts) <= 1:
            continue

        # gather (vert, its vec‐index triple)
        verts_idx = [(v, vert_vec_index(v)) for v in verts]

        # build adjacency: two verts connect if each component differs ≤1
        adj = {v: set() for v,_ in verts_idx}
        for i,(v1,idx1) in enumerate(verts_idx):
            for v2,idx2 in verts_idx[i+1:]:
                if all(abs(idx1[k] - idx2[k]) <= 1 for k in range(3)):
                    adj[v1].add(v2)
                    adj[v2].add(v1)

        # find connected‐components in this small graph
        seen = set()
        for v in adj:
            if v in seen:
                continue
            # BFS
            comp = {v}
            stack = [v]
            while stack:
                u = stack.pop()
                for w in adj[u]:
                    if w not in comp:
                        comp.add(w)
                        stack.append(w)
            seen |= comp
            if len(comp) > 1:
                # merge this component down to the first vertex
                target = next(iter(comp))
                co = target.co.copy()
                bmesh.ops.pointmerge(bm, verts=list(comp), merge_co=co)

    return bm

def merge_transparent_geometry(bm, obj):

    mesh = obj.data

    print("[Format World] Merging transparent geometry...")

    changed = True

    while changed:

        changed = False

        bm.faces.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.verts.ensure_lookup_table()

        transparent_faces = []

        for face in bm.faces:

            if face.material_index >= len(mesh.materials):
                continue

            mat = mesh.materials[face.material_index]

            if not mat:
                continue

            props = getattr(mat, "quail_materialdefinition", None)

            if not props or not props.transparent_override:
                continue

            transparent_faces.append(face)

        if not transparent_faces:
            break

        verts_before = len(bm.verts)
        edges_before = len(bm.edges)
        faces_before = len(bm.faces)

        verts = list({
            v
            for f in transparent_faces
            for v in f.verts
        })

        bmesh.ops.remove_doubles(
            bm,
            verts=verts,
            dist=0.001,
        )

        bm.faces.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.verts.ensure_lookup_table()

        transparent_faces = []

        for face in bm.faces:

            if face.material_index >= len(mesh.materials):
                continue

            mat = mesh.materials[face.material_index]

            if not mat:
                continue

            props = getattr(mat, "quail_materialdefinition", None)

            if not props or not props.transparent_override:
                continue

            transparent_faces.append(face)

        verts = list({
            v
            for f in transparent_faces
            for v in f.verts
        })

        edges = list({
            e
            for f in transparent_faces
            for e in f.edges
        })

        bmesh.ops.dissolve_limit(
            bm,
            angle_limit=0.01,
            verts=verts,
            edges=edges,
        )

        bm.faces.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.verts.ensure_lookup_table()

        transparent_faces = []

        for face in bm.faces:

            if face.material_index >= len(mesh.materials):
                continue

            mat = mesh.materials[face.material_index]

            if not mat:
                continue

            props = getattr(mat, "quail_materialdefinition", None)

            if not props or not props.transparent_override:
                continue

            transparent_faces.append(face)

        edges = list({
            e
            for f in transparent_faces
            for e in f.edges
        })

        bmesh.ops.dissolve_degenerate(
            bm,
            edges=edges,
            dist=0.0001,
        )

        loose_verts = [
            v for v in bm.verts
            if not v.link_faces
        ]

        if loose_verts:

            bmesh.ops.delete(
                bm,
                geom=loose_verts,
                context='VERTS',
            )

        loose_edges = [
            e for e in bm.edges
            if not e.link_faces
        ]

        if loose_edges:

            bmesh.ops.delete(
                bm,
                geom=loose_edges,
                context='EDGES',
            )

        if (
            len(bm.verts) != verts_before
            or len(bm.edges) != edges_before
            or len(bm.faces) != faces_before
        ):
            changed = True

    bm.faces.ensure_lookup_table()

    print("[Format World] Transparent geometry merge complete")