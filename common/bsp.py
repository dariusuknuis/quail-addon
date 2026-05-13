import bpy, bmesh, math, mathutils
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from .math_helpers import point_inside_convex, point_in_face_polygon, compute_bmesh_volume_centroid
from .math_helpers import aabb_bmesh_local, aabb_mesh_world, aabb_intersects
from .mesh import cleanup_mesh_geometry, mesh_from_bmesh
from dataclasses import dataclass
from bpy.types import Object, Collection
from ..wce.wce import wce
from ..wce.worldtree import worldtree
from ..wce.region import region

@dataclass
class BSPContext:
    # WCE / decode compatibility
    parser: wce
    collection: Collection
    parent: Object | None

    # World collections
    worlddef_collection: Collection
    region_collection: Collection
    region_mesh_collection: Collection
    worldtree_collection: Collection
    zone_collection: Collection

    # Source geometry
    source_object: Object
    zone_volumes: list

    # Runtime BSP state
    region_counter: list[int]
    worldnode_counter: list[int]
    region_centroids: dict

    # Pending Blender objects
    pending_region_meshes: list
class BSPNode:
    def __init__(self):
        self.normal = None
        self.d = None

        self.front = None
        self.back = None
        self.parent = None

        self.region_tag = None


def build_bsp(parser):

    if getattr(parser, "bsp_root", None):
        return

    tree = next(iter(parser.worldtrees.values()), None)
    if not tree:
        return

    nodes = {}

    # create nodes (1-based)
    for i, raw in enumerate(tree.worldnodes, start=1):

        n = BSPNode()

        nx, ny, nz, d = raw.normalabcd
        n.normal = Vector((nx, ny, nz))
        n.d = d

        if raw.worldregiontag and raw.worldregiontag != "NULL":
            n.region_tag = raw.worldregiontag

        nodes[i] = n

    # link
    for i, raw in enumerate(tree.worldnodes, start=1):

        node = nodes[i]

        ft = raw.fronttree
        bt = raw.backtree

        if ft > 0:
            node.front = nodes[ft]
            node.front.parent = node

        if bt > 0:
            node.back = nodes[bt]
            node.back.parent = node

    # map leaves
    parser.region_to_leaf = {}

    for node in nodes.values():
        if node.region_tag and node.front is None and node.back is None:
            parser.region_to_leaf[node.region_tag] = node

    parser.bsp_root = nodes[1]

def create_zone_bounds_intersect_geometry_node():

    gn_tree = bpy.data.node_groups.get("ZoneBoundsIntersect")
    if gn_tree:
        bounds_obj = bpy.data.objects.get("WORLD_BOUNDS")
        if bounds_obj:
            for node in gn_tree.nodes:
                if node.name != "WORLD_BOUNDS_INFO":
                    continue
                try:
                    existing_obj = node.inputs["Object"].default_value
                except:
                    existing_obj = None

                # Reassign if missing / invalid / different
                needs_update = False
                if existing_obj is None:
                    needs_update = True
                else:
                    try:
                        _ = existing_obj.name
                    except:
                        needs_update = True
                    if not needs_update and existing_obj.name != bounds_obj.name:
                        needs_update = True
                if needs_update:
                    print("Refreshing WORLD_BOUNDS reference")
                    node.inputs["Object"].default_value = bounds_obj

        return gn_tree

    gn_tree = bpy.data.node_groups.new("ZoneBoundsIntersect", 'GeometryNodeTree')

    nodes = gn_tree.nodes
    links = gn_tree.links

    # ----------------------------------------
    # Group I/O
    # ----------------------------------------
    group_input = nodes.new("NodeGroupInput")
    group_input.location = (-1000, 0)

    group_output = nodes.new("NodeGroupOutput")
    group_output.location = (600, 0)

    gn_tree.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    gn_tree.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    # ----------------------------------------
    # Camera + Self distance
    # ----------------------------------------

    act_cam_node = nodes.new("GeometryNodeInputActiveCamera")
    act_cam_node.location = (-1100, 300)

    cam_node = nodes.new("GeometryNodeObjectInfo")
    cam_node.location = (-1000, 300)
    links.new(act_cam_node.outputs[0], cam_node.inputs["Object"])

    self_node = nodes.new("GeometryNodeSelfObject")
    self_node.location = (-1100, 100)

    obj_info_node = nodes.new("GeometryNodeObjectInfo")
    obj_info_node.location = (-1000, 100)
    links.new(self_node.outputs[0], obj_info_node.inputs["Object"])

    distance = nodes.new("ShaderNodeVectorMath")
    distance.operation = 'DISTANCE'
    distance.location = (-800, 200)

    links.new(cam_node.outputs["Location"], distance.inputs[0])
    links.new(obj_info_node.outputs["Location"], distance.inputs[1])

    # ----------------------------------------
    # Extrude + / -
    # ----------------------------------------
    extrude1 = nodes.new("GeometryNodeExtrudeMesh")
    extrude1.mode = 'FACES'
    extrude1.location = (-200, 300)
    extrude1.inputs["Offset Scale"].default_value = 0.005


    extrude2 = nodes.new("GeometryNodeExtrudeMesh")
    extrude2.mode = 'FACES'
    extrude2.location = (-200, 100)
    extrude2.inputs["Offset Scale"].default_value = -0.005

    links.new(group_input.outputs[0], extrude1.inputs["Mesh"])
    links.new(distance.outputs["Value"], extrude1.inputs[2])

    links.new(group_input.outputs[0], extrude2.inputs["Mesh"])
    links.new(distance.outputs["Value"], extrude2.inputs[2])

    join_node = nodes.new("GeometryNodeJoinGeometry")
    join_node.location = (0, 200)
    links.new(extrude1.outputs[0], join_node.inputs[0])
    links.new(extrude2.outputs[0], join_node.inputs[0])

    # ----------------------------------------
    # WORLD_BOUNDS cube
    # ----------------------------------------
    obj_info = nodes.new("GeometryNodeObjectInfo")
    obj_info.location = (-800, -200)
    obj_info.transform_space = 'RELATIVE'
    obj_info.name = "WORLD_BOUNDS_INFO"

    bounds_obj = bpy.data.objects.get("WORLD_BOUNDS")
    if bounds_obj:
        obj_info.inputs["Object"].default_value = bounds_obj

    cube = nodes.new("GeometryNodeMeshCube")
    cube.location = (-600, -200)
    cube.inputs["Size"].default_value = (2.0, 2.0, 2.0)

    transform = nodes.new("GeometryNodeTransform")
    transform.location = (-400, -200)

    links.new(cube.outputs["Mesh"], transform.inputs["Geometry"])
    links.new(obj_info.outputs["Location"], transform.inputs["Translation"])
    links.new(obj_info.outputs["Rotation"], transform.inputs["Rotation"])
    links.new(obj_info.outputs["Scale"], transform.inputs["Scale"])

    # ----------------------------------------
    # Boolean INTERSECT
    # ----------------------------------------
    boolean = nodes.new("GeometryNodeMeshBoolean")
    boolean.operation = 'INTERSECT'
    boolean.location = (200, 0)

    links.new(join_node.outputs[0], boolean.inputs[1])  # plane slab
    links.new(transform.outputs["Geometry"], boolean.inputs[1])  # bounds

    # ----------------------------------------
    # Output
    # ----------------------------------------
    links.new(boolean.outputs["Mesh"], group_output.inputs[0])

    return gn_tree

def create_bsp_plane_mesh(name="BSPPlaneMesh", size=10000.0):
    half = size / 2.0

    verts = [
        (-half, -half, 0),
        ( half, -half, 0),
        ( half,  half, 0),
        (-half,  half, 0)
    ]
    faces = [(0, 1, 2, 3)]

    rot = mathutils.Euler((-math.pi/2, 0, 0), 'XYZ').to_matrix().to_4x4()
    verts_rot = [rot @ mathutils.Vector(v) for v in verts]

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts_rot, [], faces)
    mesh.update()
    return mesh


def create_leaf_mesh(name="LeafMesh"):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(0, 0, 0)], [], [])
    mesh.update()
    return mesh


def rotation_from_normal(normal):
    default_dir = mathutils.Vector((0, 1, 0))
    target_dir = mathutils.Vector(normal).normalized()
    quat = default_dir.rotation_difference(target_dir)
    return quat.to_euler()


def calculate_point_on_plane(normal, d):
    n = mathutils.Vector(normal).normalized()
    return -d * n

def normalize_bounds(min_bound, max_bound, target_size):
    """Expand the bounds so that each side is an integer multiple of target_size."""
    center = (min_bound + max_bound) * 0.5
    extents = max_bound - min_bound
    adjusted_size = Vector((
        math.ceil(extents.x / target_size) * target_size,
        math.ceil(extents.y / target_size) * target_size,
        math.ceil(extents.z / target_size) * target_size
    ))
    new_min = center - adjusted_size * 0.5
    new_max = center + adjusted_size * 0.5
    return new_min, new_max

def create_world_volume(vol_min, vol_max):
    """
    Create a new mesh object named `name` whose geometry is
    the rectangular prism spanning vol_min→vol_max.
    Returns the new Object (already linked to the active collection).
    """

    bm = bmesh.new()

    # 8 corners
    v0 = Vector((vol_min.x, vol_min.y, vol_min.z))
    v1 = Vector((vol_max.x, vol_min.y, vol_min.z))
    v2 = Vector((vol_max.x, vol_max.y, vol_min.z))
    v3 = Vector((vol_min.x, vol_max.y, vol_min.z))
    v4 = Vector((vol_min.x, vol_min.y, vol_max.z))
    v5 = Vector((vol_max.x, vol_min.y, vol_max.z))
    v6 = Vector((vol_max.x, vol_max.y, vol_max.z))
    v7 = Vector((vol_min.x, vol_max.y, vol_max.z))

    bm_verts = [
        bm.verts.new(v0),
        bm.verts.new(v1),
        bm.verts.new(v2),
        bm.verts.new(v3),
        bm.verts.new(v4),
        bm.verts.new(v5),
        bm.verts.new(v6),
        bm.verts.new(v7),
    ]
    bm.verts.index_update()
    bm.verts.ensure_lookup_table()

    # each face as a quad of those verts
    faces = [
        (0, 1, 2, 3),  # bottom
        (4, 5, 6, 7),  # top
        (0, 4, 5, 1),  # front
        (1, 5, 6, 2),  # right
        (2, 6, 7, 3),  # back
        (3, 7, 4, 0),  # left
    ]

    for idx_tuple in faces:
        vA, vB, vC, vD = (bm_verts[i] for i in idx_tuple)
        try:
            bm.faces.new((vA, vB, vC, vD))
        except ValueError:
            # face might already exist if you run this twice; ignore
            pass

    # 4) Finalize: ensure lookup tables and normals are valid
    bm.faces.index_update()
    bm.faces.ensure_lookup_table()
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.normal_update()

    return bm

def terrain_split(bm_geo, plane_co, plane_no, tol=1e-6):

    def signed_dist(co):
        return plane_no.dot(Vector(co) - Vector(plane_co))

    def face_classification(face):
        dists = [signed_dist(v.co) for v in face.verts]
        if all(d >= -tol for d in dists) and all(d <= tol for d in dists):
            return 'coplanar'
        if all(d >= -tol for d in dists):
            return 'front'
        if all(d <= tol for d in dists):
            return 'back'
        return 'split'

    bm_lower = bm_geo.copy()
    geom_l = list(bm_lower.verts) + list(bm_lower.edges) + list(bm_lower.faces)
    bmesh.ops.bisect_plane(
        bm_lower,
        geom=geom_l,
        plane_co=plane_co,
        plane_no=plane_no,
        dist=tol,
        use_snap_center=False,
        clear_inner=False,
        clear_outer=True,
    )
    # Remove coplanar faces from lower — they belong to upper
    coplanar_lower = [
        f for f in bm_lower.faces
        if face_classification(f) == 'coplanar'
    ]
    bmesh.ops.delete(bm_lower, geom=coplanar_lower, context='FACES')
    cleanup_mesh_geometry(bm_lower)

    bm_upper = bm_geo.copy()
    geom_u = list(bm_upper.verts) + list(bm_upper.edges) + list(bm_upper.faces)
    bmesh.ops.bisect_plane(
        bm_upper,
        geom=geom_u,
        plane_co=plane_co,
        plane_no=plane_no,
        dist=tol,
        use_snap_center=False,
        clear_inner=True,
        clear_outer=False,
    )
    # Coplanar faces stay in upper — no removal needed
    cleanup_mesh_geometry(bm_upper)

    return bm_lower, bm_upper

def volume_split(bm_vol, plane_co, plane_no, tol=1e-6):
    """
    Splits the convex BMesh `bm_vol` by the plane (plane_co, plane_no) into
    two capped halves, and returns (bm_lower, bm_upper).

      - the “lower” half keeps the inside side (n·X + d <= 0)
      - the “upper” half keeps the outside side (n·X + d >= 0)

    Both outputs are new BMesh instances with their open boundaries filled.
    """
    # copy for lower half
    bm_lower = bm_vol.copy()
    geom_l   = list(bm_lower.verts) + list(bm_lower.edges) + list(bm_lower.faces)
    bmesh.ops.bisect_plane(
        bm_lower,
        geom       = geom_l,
        plane_co   = plane_co,
        plane_no   = plane_no,
        dist       = tol,
        clear_inner=False,   # keep the “inside” half
        clear_outer=True     # discard the outside
    )
    # cap the cut
    boundary = [e for e in bm_lower.edges if len(e.link_faces)==1]
    if boundary:
        bmesh.ops.holes_fill(bm_lower, edges=boundary, sides=0)
    # fix normals
    bmesh.ops.recalc_face_normals(bm_lower, faces=bm_lower.faces)
    bm_lower.normal_update()

    # copy for upper half
    bm_upper = bm_vol.copy()
    geom_u   = list(bm_upper.verts) + list(bm_upper.edges) + list(bm_upper.faces)
    bmesh.ops.bisect_plane(
        bm_upper,
        geom       = geom_u,
        plane_co   = plane_co,
        plane_no   = plane_no,
        dist       = tol,
        clear_inner=True,    # discard the inside
        clear_outer=False    # keep the outside half
    )
    boundary = [e for e in bm_upper.edges if len(e.link_faces)==1]
    if boundary:
        bmesh.ops.holes_fill(bm_upper, edges=boundary, sides=0)
    bmesh.ops.recalc_face_normals(bm_upper, faces=bm_upper.faces)
    bm_upper.normal_update()

    return bm_lower, bm_upper

def create_mesh_object_from_bmesh(bm, name, ctx: BSPContext):
    """
    Create a new mesh object from bm:
     1) copy original materials & custom props
     2) apply world transform into the mesh data
     3) compute world-space AABB → center & radius
     4) recenter geometry so that AABB-center is at origin
     5) set object.matrix_world to put it back at that center
     6) call create_bounding_sphere() with the computed radius
    """

    cleanup_mesh_geometry(bm)

    # --- build the mesh & object ---
    me = bpy.data.meshes.new(name)
    new_obj = bpy.data.objects.new(name, me)
    original_obj = ctx.source_object

    # copy materials
    for mat in original_obj.data.materials:
        new_obj.data.materials.append(mat)

    # copy custom props
    for key in original_obj.keys():
        if key != "_RNA_UI":
            new_obj[key] = original_obj[key]

    quaildef = original_obj.get("quaildef")
    propgroup_name = None

    if quaildef == "dmspritedef2":
        propgroup_name = "quail_dmspritedef2"

    elif quaildef == "dmspritedefinition":
        propgroup_name = "quail_dmspritedefinition"

    if propgroup_name:
        src_props = getattr(original_obj, propgroup_name, None)
        dst_props = getattr(new_obj, propgroup_name, None)
        if src_props and dst_props:
            for prop in src_props.bl_rna.properties:
                if prop.identifier == "rna_type":
                    continue
                try:
                    setattr(
                        dst_props,
                        prop.identifier,
                        getattr(src_props, prop.identifier)
                    )
                except:
                    pass

    mesh_from_bmesh(bm, new_obj)

    # --- Set vertex color layer as active (or it doesn't display automatically) ---
    col_attr = me.color_attributes.get("vertex_colors")
    if col_attr:
        me.color_attributes.active_color = col_attr

    # --- bake original_obj's world matrix into the mesh data ---
    me.transform(original_obj.matrix_world)

    # --- compute world-space AABB of the baked vertices ---
    verts = [v.co for v in me.vertices]
    if verts:
        minv = Vector((min(v.x for v in verts),
                       min(v.y for v in verts),
                       min(v.z for v in verts)))
        maxv = Vector((max(v.x for v in verts),
                       max(v.y for v in verts),
                       max(v.z for v in verts)))
    else:
        minv = maxv = Vector((0,0,0))

    # center of that box in world-space
    center_world = (minv + maxv) * 0.5

    # round to nearest integer
    center_int = Vector((
        round(center_world.x),
        round(center_world.y),
        round(center_world.z),
    ))

    # --- recenter the mesh geometry so box-center moves to origin ---
    me.transform(Matrix.Translation(-center_int))

    # place the new object back at the box-center
    new_obj.matrix_world = Matrix.Translation(center_int)

    return new_obj

# ------------------------------------------------------------
# --- Zone BVH and Point–in–Mesh Test (Using closest_point_on_mesh)
# ------------------------------------------------------------

AABB_EPS  = 1e-6

def build_volume_planes(source, source_obj=None):
    """
    Given either:
      - a bmesh.types.BMesh (optionally with source_obj to reproject it),
      - a bpy.types.Object (type=='MESH'),
      - or a bpy.types.Mesh (must pass source_obj),
    returns a list of (world_normal, world_d) for each face of the convex mesh,
    with normals flipped so that n·X + d <= 0 is the “inside” half-space.

    If `source` is a BMesh and `source_obj` is None, it is assumed already in world space.
    """
    # — determine the BMesh we’ll work on —
    temp_bm = False
    if isinstance(source, bmesh.types.BMesh):
        bm = source
        # now optional: if no source_obj, we assume bm verts are already world‐space
    elif isinstance(source, bpy.types.Object) and source.type == 'MESH':
        source_obj = source
        bm = bmesh.new()
        bm.from_mesh(source.data)
        temp_bm = True
    elif isinstance(source, bpy.types.Mesh):
        if source_obj is None:
            raise ValueError("When passing a Mesh you must also pass source_obj for its transform")
        bm = bmesh.new()
        bm.from_mesh(source)
        temp_bm = True
    else:
        raise TypeError("`source` must be a BMesh, a MESH Object, or a Mesh datablock")

    # — grab transforms (or identity if none) —
    if source_obj is not None:
        wm3 = source_obj.matrix_world.to_3x3()
        wm4 = source_obj.matrix_world
    else:
        wm3 = Matrix.Identity(3)
        wm4 = Matrix.Identity(4)

    # — build raw planes —
    planes = []
    for f in bm.faces:
        n_world = (wm3 @ f.normal).normalized()
        p_world = wm4 @ f.calc_center_median()
        planes.append((n_world, -n_world.dot(p_world)))

    # — flip any plane whose outside‐half contains the mesh centroid —
    verts_ws = [wm4 @ v.co for v in bm.verts]
    if verts_ws:
        centroid = sum(verts_ws, Vector()) / len(verts_ws)
        for i, (n, d) in enumerate(planes):
            if n.dot(centroid) + d > 0:
                planes[i] = (-n, -d)

    # — clean up if we made a temporary BMesh —
    if temp_bm:
        bm.free()

    return planes

def zone_bsp_split(bm_geo, zone_obj, current_node, bm_vol, tol=1e-4, min_diag=0.1, used_planes=None):

    # Region AABB
    vol_verts = [v.co.copy() for v in bm_vol.verts]
    if not vol_verts:
        return None

    rmin = Vector((min(v.x for v in vol_verts),
                   min(v.y for v in vol_verts),
                   min(v.z for v in vol_verts),))

    rmax = Vector((max(v.x for v in vol_verts),
                   max(v.y for v in vol_verts),
                   max(v.z for v in vol_verts),))

    # Zone AABB
    zmin, zmax = aabb_mesh_world(zone_obj)
    if not aabb_intersects(rmin, rmax, zmin, zmax):
        return None

    # Build convex planes
    region_planes = build_volume_planes(bm_vol)
    zone_planes = build_volume_planes(zone_obj)

    zone_verts = [
        zone_obj.matrix_world @ v.co
        for v in zone_obj.data.vertices
    ]

    # Full convex overlap test
    def convex_overlap(planes_a, verts_a, planes_b, verts_b):

        # Is B fully outside any plane of A?
        for n, d in planes_a:
            outside = True
            for v in verts_b:
                if n.dot(v) + d <= -tol:
                    outside = False
                    break
            if outside:
                return False

        # Is A fully outside any plane of B?
        for n, d in planes_b:
            outside = True
            for v in verts_a:
                if n.dot(v) + d <= -tol:
                    outside = False
                    break
            if outside:
                return False

        return True

    if not convex_overlap(region_planes, vol_verts, zone_planes, zone_verts):
        return None

    # Zone BMesh
    bm_zon = bmesh.new()
    bm_zon.from_mesh(zone_obj.data)
    bm_zon.faces.ensure_lookup_table()

    zone_wm3 = zone_obj.matrix_world.to_3x3()
    zone_wm4 = zone_obj.matrix_world

    # Find splitting face
    splitter = None
    already_used = used_planes.get(current_node, [])
    for face in bm_zon.faces:

        # Build world-space plane
        n_ws = (zone_wm3 @ face.normal).normalized()
        p_ws = zone_wm4 @ face.calc_center_median()
        d_ws = -n_ws.dot(p_ws)

        # Dedupe against previously used planes
        too_similar = False
        for (n0, d0) in already_used:
            if (
                n0.dot(n_ws) > 1.0 - 1e-4 and
                abs(d0 - d_ws) < tol
            ):
                too_similar = True
                break
        if too_similar:
            continue

        # Plane divides region test
        front = False
        back = False
        for v in vol_verts:
            dist = n_ws.dot(v) + d_ws
            if dist > tol:
                front = True
            elif dist < -tol:
                back = True
            if front and back:
                break
        if not (front and back):
            continue
        splitter = face
        break

    if not splitter:
        bm_zon.free()
        return None

    # Build split plane
    plane_co_ws = zone_wm4 @ splitter.calc_center_median()
    plane_no_ws = (zone_wm3 @ splitter.normal).normalized()
    plane_d = -plane_no_ws.dot(plane_co_ws)
    plane_co_l = plane_co_ws.copy()
    plane_no_l = plane_no_ws.copy()
    bm_zon.free()

    # Perform split
    geo_in, geo_out = terrain_split( bm_geo, plane_co_l, plane_no_l)
    vol_in, vol_out = volume_split( bm_vol, plane_co_l, plane_no_l, tol)

    # Make sure split is not too small
    bi_min, bi_max = aabb_bmesh_local(vol_in)
    bo_min, bo_max = aabb_bmesh_local(vol_out)

    if (
        (bi_max - bi_min).length < min_diag or
        (bo_max - bo_min).length < min_diag
    ):
        return None

    # Mark plane as used
    used_planes.setdefault(current_node, []).append(
        (plane_no_ws.copy(), plane_d)
    )

    return (geo_in, geo_out, vol_in, vol_out, plane_no_ws.copy(), plane_d)

def recursive_bsp_split(ctx: BSPContext, bm_geo, bm_vol, target_size, used_planes=None, depth=0, depth_counters=None, backtree=False):
    """
    Recursively subdivide the normalized volume using axis–aligned splits.
    When a region is small enough, attempt to further split it using zone-based splits.
    """

    parser = ctx.parser
    src = ctx.source_object
    zone_volumes = ctx.zone_volumes

    wt = next(iter(parser.worldtrees.values()))

    if used_planes is None:
        used_planes = {}

    if depth_counters is None:
        depth_counters = {}

    for d in list(depth_counters.keys()):

        if d <= depth:
            depth_counters[d] += 1

    if depth not in depth_counters:
        depth_counters[depth] = 1

    # Create worldnode
    node = worldtree.worldnode()
    node.normalabcd = (0.0, 0.0, 0.0, 0.0)
    node.worldregiontag = ""
    node.fronttree = 0
    node.backtree = 0
    wt.worldnodes.append(node)
    current_node = ctx.worldnode_counter[0]
    ctx.worldnode_counter[0] += 1

    # Backtree hookup
    if backtree:
        parent_index = current_node - depth_counters[depth]
        if parent_index > 0:
            parent_node = wt.worldnodes[parent_index - 1]
            parent_node.backtree = current_node
        for d in list(depth_counters.keys()):
            if d >= depth:
                depth_counters[d] = 0

    # Region bounds
    vol_min, vol_max = aabb_bmesh_local(bm_vol)
    size = vol_max - vol_min

    # FPSCALE
    grid_step = None
    if src.get("quaildef") == "dmspritedef2":
        fpscale = int(src.quail_dmspritedef2.fpscale)
        grid_step = 1.0 / (2 ** fpscale)

    # BASE CASE
    if all(size[i] <= target_size + 1e-4 for i in range(3)):
        parent_idx = None
        for i, worldnode in enumerate(wt.worldnodes):
            if worldnode.fronttree == current_node or worldnode.backtree == current_node:
                parent_idx = i + 1
                break
        if parent_idx is None:
            used_planes[current_node] = []
        else:
            used_planes[current_node] = used_planes.get(parent_idx, []).copy()

        # Zone BSP split attempt
        for zone_obj in zone_volumes:
            split_result = zone_bsp_split(bm_geo, zone_obj, current_node, bm_vol, tol=1e-4, min_diag=0.1, used_planes=used_planes)
            if split_result is not None:
                bm_geo_in, bm_geo_out, bm_vol_in, bm_vol_out, plane_no, d = split_result
                node.normalabcd = (-plane_no.x, -plane_no.y, -plane_no.z, -float(d))
                node.fronttree = ctx.worldnode_counter[0]
                recursive_bsp_split(ctx, bm_geo_in, bm_vol_in, target_size, used_planes=used_planes, depth=depth + 1, depth_counters=depth_counters, backtree=False)
                recursive_bsp_split(ctx, bm_geo_out, bm_vol_out, target_size, used_planes=used_planes, depth=depth + 1, depth_counters=depth_counters, backtree=True)

                return

        # Finalize leaf region
        region_index = ctx.region_counter[0]
        ctx.region_counter[0] += 1
        center = (vol_min + vol_max) * 0.5
        mat = src.matrix_world
        ws_corners = [mat @ Vector((x, y, z)) for x in (vol_min.x, vol_max.x)
                                              for y in (vol_min.y, vol_max.y)
                                              for z in (vol_min.z, vol_max.z)]
        ws_min = Vector((min(c.x for c in ws_corners),
                         min(c.y for c in ws_corners),
                         min(c.z for c in ws_corners)))
        ws_max = Vector((max(c.x for c in ws_corners),
                         max(c.y for c in ws_corners),
                         max(c.z for c in ws_corners)))
        sphere_radius = (ws_max - ws_min).length / 2.0
        centroid = compute_bmesh_volume_centroid(bm_vol)
        ctx.region_centroids[region_index] = centroid

        # Create REGION definition
        reg = region()
        reg.tag = f"R{region_index:06d}"
        reg.sphere = (center.x, center.y, center.z, sphere_radius)
        if bm_geo.faces:
            reg.sprite = (f"R{region_index}_DMSPRITEDEF")
        parser.regions[reg.tag] = reg
        node.worldregiontag = reg.tag
        node.backtree = 0

        # Create region mesh
        if bm_geo.faces:
            mesh_obj = create_mesh_object_from_bmesh(bm_geo, f"R{region_index}_DMSPRITEDEF", ctx)
            ctx.pending_region_meshes.append(mesh_obj)

        return

    # EMPTY GEO CASE
    if not bm_geo.faces:
        axis, length = max(enumerate(size), key=lambda x: x[1])
        if length <= target_size:
            region_index = ctx.region_counter[0]
            ctx.region_counter[0] += 1
            center = (vol_min + vol_max) * 0.5
            sphere_radius = (size).length / 2.0
            centroid = compute_bmesh_volume_centroid(bm_vol)
            ctx.region_centroids[region_index] = centroid

            reg = region()
            reg.tag = f"R{region_index:06d}"
            reg.sphere = (center.x, center.y, center.z, sphere_radius)
            parser.regions[reg.tag] = reg
            node.worldregiontag = reg.tag
            node.backtree = 0

            return

        if grid_step:
            mid = vol_min[axis] + (length * 0.5)
            split_pos = round(mid / grid_step) * grid_step
        else:
            split_pos = vol_min[axis] + target_size * math.floor((length / target_size) * 0.5)
            if split_pos <= vol_min[axis] + 1e-6 or split_pos >= vol_max[axis] - 1e-6:
                split_pos = vol_min[axis] + (length * 0.5)
        plane_co = Vector((0, 0, 0))
        plane_no = Vector((0, 0, 0))
        plane_co[axis] = split_pos
        plane_no[axis] = 1.0
        d_value = -plane_no.dot(plane_co)

        node.normalabcd = (-plane_no.x, -plane_no.y, -plane_no.z, -float(d_value))
        node.fronttree = ctx.worldnode_counter[0]

        bm_vol_lower, bm_vol_upper = volume_split(bm_vol, plane_co, plane_no,tol=0.0)

        recursive_bsp_split(ctx, bm_geo, bm_vol_lower, target_size, depth=depth + 1, depth_counters=depth_counters, backtree=False)
        recursive_bsp_split(ctx, bm_geo, bm_vol_upper, target_size, depth=depth + 1, depth_counters=depth_counters, backtree=True)

        return

    # NORMAL TERRAIN SPLIT
    valid_axes = [(i, size[i]) for i in range(3) if size[i] > target_size + 1e-4]
    if not valid_axes:
        region_index = ctx.region_counter[0]
        ctx.region_counter[0] += 1
        center = (vol_min + vol_max) * 0.5
        sphere_radius = (size).length / 2.0
        centroid = compute_bmesh_volume_centroid(bm_vol)
        ctx.region_centroids[region_index] = centroid

        # Create REGION definition
        reg = region()
        reg.tag = f"R{region_index:06d}"
        reg.sphere = (center.x, center.y, center.z, sphere_radius)
        parser.regions[reg.tag] = reg
        node.worldregiontag = reg.tag
        node.backtree = 0
        if bm_geo.faces:
            reg.sprite = (f"R{region_index}_DMSPRITEDEF")
            mesh_obj = create_mesh_object_from_bmesh(bm_geo, f"R{region_index}_DMSPRITEDEF", ctx)
            ctx.pending_region_meshes.append(mesh_obj)
        return

    axis, _ = max(valid_axes, key=lambda x: x[1])
    length = size[axis]
    split_pos = vol_min[axis] + target_size * math.floor((length / target_size) * 0.5)
    if split_pos <= vol_min[axis] + 1e-6 or split_pos >= vol_max[axis] - 1e-6:
        split_pos = vol_min[axis] + (length * 0.5)

    plane_co = Vector((0, 0, 0))
    plane_no = Vector((0, 0, 0))
    plane_co[axis] = split_pos
    plane_no[axis] = 1.0
    d_value = -plane_no.dot(plane_co)

    node.normalabcd = (-plane_no.x, -plane_no.y, -plane_no.z, -float(d_value))
    node.fronttree = ctx.worldnode_counter[0]

    bm_geo_lower, bm_geo_upper = terrain_split(bm_geo, plane_co, plane_no)
    bm_vol_lower, bm_vol_upper = volume_split(bm_vol, plane_co, plane_no, tol=0.0)

    recursive_bsp_split(ctx, bm_geo_lower, bm_vol_lower, target_size, depth=depth + 1, depth_counters=depth_counters, backtree=False)
    recursive_bsp_split(ctx, bm_geo_upper, bm_vol_upper, target_size, depth=depth + 1, depth_counters=depth_counters, backtree=True)

DEBUG_WORLDNODES = {
    29,
}

def edges_match(e0, e1, tol):

    a0, b0 = [v.co for v in e0.verts]
    a1, b1 = [v.co for v in e1.verts]

    return (
        (
            (a0 - a1).length < tol and
            (b0 - b1).length < tol
        )
        or
        (
            (a0 - b1).length < tol and
            (b0 - a1).length < tol
        )
    )

def is_convex_region(
    bm,
    worldnode=None,
    epsilon=0.005,
    dist_tol=0.01,
):

    bm_test = bm.copy()

    # ---------------------------------------------------
    # Remove degenerate geometry
    # ---------------------------------------------------

    bmesh.ops.dissolve_degenerate(
        bm_test,
        dist=dist_tol,
        edges=list(bm_test.edges),
    )

    # Remove tiny faces
    tiny_faces = [
        f for f in bm_test.faces
        if f.calc_area() < 0.01
    ]

    if tiny_faces:
        bmesh.ops.delete(
            bm_test,
            geom=tiny_faces,
            context='FACES',
        )

    # Remove loose edges
    loose_edges = [
        e for e in bm_test.edges
        if not e.link_faces
    ]

    if loose_edges:
        bmesh.ops.delete(
            bm_test,
            geom=loose_edges,
            context='EDGES',
        )

    # Remove loose verts
    loose_verts = [
        v for v in bm_test.verts
        if not v.link_edges
    ]

    if loose_verts:
        bmesh.ops.delete(
            bm_test,
            geom=loose_verts,
            context='VERTS',
        )

    bm_test.normal_update()

    faces = list(bm_test.faces)

    # ---------------------------------------------------
    # Debug original geometry
    # ---------------------------------------------------

    if worldnode in DEBUG_WORLDNODES:

        print("\n====================")
        print(f"WORLDNODE {worldnode}")
        print("====================")

        print(
            f"Verts: {len(bm_test.verts)} | "
            f"Edges: {len(bm_test.edges)} | "
            f"Faces: {len(bm_test.faces)}"
        )

    # ---------------------------------------------------
    # Compare spatially matching face edges
    # ---------------------------------------------------

    for i, f0 in enumerate(faces):

        n0 = f0.normal.normalized()

        if n0.length_squared < 0.5:
            continue

        for f1 in faces[i + 1:]:

            n1 = f1.normal.normalized()

            if n1.length_squared < 0.5:
                continue

            dot = n0.dot(n1)

            # Ignore coplanar/opposite duplicate faces
            if dot > 0.999 or dot < -0.999:
                continue

            shared = False
            matched_edges = None

            for e0 in f0.edges:

                if e0.calc_length() < dist_tol:
                    continue

                for e1 in f1.edges:

                    if e1.calc_length() < dist_tol:
                        continue

                    if edges_match(
                        e0,
                        e1,
                        dist_tol,
                    ):
                        shared = True
                        matched_edges = (e0, e1)
                        break

                if shared:
                    break

            if not shared:
                continue

            orientation = (
                (
                    f1.calc_center_median()
                    - f0.calc_center_median()
                ).normalized().dot(n0)
            )

            if orientation < -epsilon:

                if worldnode in DEBUG_WORLDNODES:

                    e0, e1 = matched_edges

                    print("\nCONCAVE FACE PAIR")
                    print("====================")

                    print(
                        f"Faces: "
                        f"{f0.index} <-> {f1.index}"
                    )

                    print(
                        f"Orientation: "
                        f"{orientation}"
                    )

                    print(f"Normal0: {n0}")
                    print(f"Normal1: {n1}")

                    print(
                        f"Edge0 Length: "
                        f"{e0.calc_length()}"
                    )

                    print(
                        f"Edge1 Length: "
                        f"{e1.calc_length()}"
                    )

                    print(
                        f"Face Areas: "
                        f"{f0.calc_area()} | "
                        f"{f1.calc_area()}"
                    )

                bm_test.free()
                return False

    bm_test.free()
    return True

def choose_bsp_plane(bm, epsilon=0.001):

    if not bm.faces:
        return None

    best_face = None
    best_score = 1e20
    faces = list(bm.faces)
    used_planes = []

    for face in faces:
        plane_no = face.normal.normalized()
        plane_co = face.calc_center_median()
        plane_d = -plane_no.dot(
            plane_co
        )

        # ------------------------------------------------------------
        # Skip nearly identical coplanar planes
        # ------------------------------------------------------------

        skip = False
        for n0, d0 in used_planes:

            if (
                abs(n0.dot(plane_no)) > 0.999
                and abs(d0 - plane_d) < 0.1
            ):
                skip = True
                break

        if skip:
            continue

        used_planes.append((
            plane_no.copy(),
            plane_d,
        ))

        front = 0
        back = 0
        split = 0

        for test_face in faces:
            has_front = False
            has_back = False
            for v in test_face.verts:
                d = plane_no.dot(v.co - plane_co)
                if d > epsilon:
                    has_front = True
                elif d < -epsilon:
                    has_back = True
            if has_front and has_back:
                split += 1
            elif has_front:
                front += 1
            elif has_back:
                back += 1

        # ------------------------------------------------------------
        # Reject useless planes
        # ------------------------------------------------------------

        if front == 0 or back == 0:
            continue

        # Avoid tiny sliver partitions
        # if front < 2 or back < 2:
        #     continue

        balance = abs(front - back)

        # Strongly discourage excessive polygon splitting
        score = (
            split * 25
            + balance
        )

        # Prefer axial planes
        if abs(abs(plane_no.x) - 1.0) < 0.001:
            score -= 5

        if abs(abs(plane_no.y) - 1.0) < 0.001:
            score -= 5

        if abs(abs(plane_no.z) - 1.0) < 0.001:
            score -= 5

        if score < best_score:

            best_score = score
            best_face = face

    if best_face is None:
        return None

    return (
        best_face.calc_center_median().copy(),
        best_face.normal.normalized().copy(),
    )

def choose_balanced_convex_split(bm):

    vol_min, vol_max = aabb_bmesh_local(bm)

    size = vol_max - vol_min

    axis = max(
        range(3),
        key=lambda i: size[i]
    )

    split_pos = (
        vol_min[axis]
        + size[axis] * 0.5
    )

    plane_co = Vector((0, 0, 0))
    plane_no = Vector((0, 0, 0))

    plane_co[axis] = split_pos
    plane_no[axis] = 1.0

    return plane_co, plane_no

def recursive_indoor_bsp_split(
    ctx,
    bm_geo,
    bm_vol,
    max_faces_per_region=280,
    max_depth=64,
    depth=0,
    depth_counters=None,
    backtree=False,
):

    parser = ctx.parser
    src = ctx.source_object

    wt = next(iter(parser.worldtrees.values()))

    if depth_counters is None:
        depth_counters = {}

    for d in list(depth_counters.keys()):

        if d <= depth:
            depth_counters[d] += 1

    if depth not in depth_counters:
        depth_counters[depth] = 1

    # ------------------------------------------------------------
    # Create worldnode
    # ------------------------------------------------------------

    node = worldtree.worldnode()

    node.normalabcd = (0.0, 0.0, 0.0, 0.0)
    node.worldregiontag = ""
    node.fronttree = 0
    node.backtree = 0

    wt.worldnodes.append(node)

    current_node = ctx.worldnode_counter[0]
    ctx.worldnode_counter[0] += 1

    # ------------------------------------------------------------
    # Backtree hookup
    # ------------------------------------------------------------

    if backtree:

        parent_index = current_node - depth_counters[depth]

        if parent_index > 0:

            parent_node = wt.worldnodes[parent_index - 1]
            parent_node.backtree = current_node

        for d in list(depth_counters.keys()):

            if d >= depth:
                depth_counters[d] = 0

    # ------------------------------------------------------------
    # Empty leaf
    # ------------------------------------------------------------

    if not bm_geo.faces:

        region_index = ctx.region_counter[0]
        ctx.region_counter[0] += 1

        vol_min, vol_max = aabb_bmesh_local(bm_vol)

        center = (vol_min + vol_max) * 0.5
        sphere_radius = (vol_max - vol_min).length / 2.0

        centroid = compute_bmesh_volume_centroid(bm_vol)

        ctx.region_centroids[region_index] = centroid

        reg = region()

        reg.tag = f"R{region_index:06d}"

        reg.sphere = (
            center.x,
            center.y,
            center.z,
            sphere_radius,
        )

        parser.regions[reg.tag] = reg

        node.worldregiontag = reg.tag

        return

    # ------------------------------------------------------------
    # Convexity check
    # ------------------------------------------------------------

    convex = is_convex_region(
        bm_geo,
        worldnode=current_node,
    )

    if convex:

        # Convex and small enough -> leaf
        if (
            len(bm_geo.faces)
            <= max_faces_per_region
        ):
            region_index = ctx.region_counter[0]
            ctx.region_counter[0] += 1

            vol_min, vol_max = aabb_bmesh_local(
                bm_vol
            )

            center = (
                vol_min + vol_max
            ) * 0.5

            ws_corners = [
                src.matrix_world @ Vector((x, y, z))
                for x in (vol_min.x, vol_max.x)
                for y in (vol_min.y, vol_max.y)
                for z in (vol_min.z, vol_max.z)
            ]

            ws_min = Vector((
                min(v.x for v in ws_corners),
                min(v.y for v in ws_corners),
                min(v.z for v in ws_corners),
            ))

            ws_max = Vector((
                max(v.x for v in ws_corners),
                max(v.y for v in ws_corners),
                max(v.z for v in ws_corners),
            ))

            sphere_radius = (
                ws_max - ws_min
            ).length / 2.0

            centroid = compute_bmesh_volume_centroid(
                bm_vol
            )

            ctx.region_centroids[
                region_index
            ] = centroid

            reg = region()

            reg.tag = (
                f"R{region_index:06d}"
            )

            reg.sphere = (
                center.x,
                center.y,
                center.z,
                sphere_radius,
            )

            reg.sprite = (
                f"R{region_index}_DMSPRITEDEF"
            )

            parser.regions[
                reg.tag
            ] = reg

            node.worldregiontag = reg.tag

            mesh_obj = create_mesh_object_from_bmesh(
                bm_geo,
                f"R{region_index}_DMSPRITEDEF",
                ctx,
            )

            ctx.pending_region_meshes.append(
                mesh_obj
            )

            return

        # Convex but too large -> balanced spatial split
        else:
            split_result = choose_balanced_convex_split(
                bm_vol
            )

    else:
        # Concave -> traditional BSP split
        split_result = choose_bsp_plane(
            bm_geo
        )

    # ------------------------------------------------------------
    # Recursion safety limit
    # ------------------------------------------------------------

    if depth >= max_depth:

        region_index = ctx.region_counter[0]
        ctx.region_counter[0] += 1

        vol_min, vol_max = aabb_bmesh_local(
            bm_vol
        )

        center = (
            vol_min + vol_max
        ) * 0.5

        sphere_radius = (
            vol_max - vol_min
        ).length / 2.0

        centroid = compute_bmesh_volume_centroid(
            bm_vol
        )

        ctx.region_centroids[
            region_index
        ] = centroid

        reg = region()

        reg.tag = (
            f"R{region_index:06d}"
        )

        reg.sphere = (
            center.x,
            center.y,
            center.z,
            sphere_radius,
        )

        reg.sprite = (
            f"R{region_index}_DMSPRITEDEF"
        )

        parser.regions[
            reg.tag
        ] = reg

        node.worldregiontag = reg.tag

        mesh_obj = create_mesh_object_from_bmesh(
            bm_geo,
            f"R{region_index}_DMSPRITEDEF",
            ctx,
        )

        ctx.pending_region_meshes.append(
            mesh_obj
        )

        return

    if split_result is None:
        print(
            f"Worldnode_{current_node} | "
            f"Convex={convex} | "
            f"No valid split, leaf"
        )

        region_index = ctx.region_counter[0]
        ctx.region_counter[0] += 1

        vol_min, vol_max = aabb_bmesh_local(
            bm_vol
        )

        center = (
            vol_min + vol_max
        ) * 0.5

        sphere_radius = (
            vol_max - vol_min
        ).length / 2.0

        centroid = compute_bmesh_volume_centroid(
            bm_vol
        )

        ctx.region_centroids[
            region_index
        ] = centroid

        reg = region()

        reg.tag = (
            f"R{region_index:06d}"
        )

        reg.sphere = (
            center.x,
            center.y,
            center.z,
            sphere_radius,
        )

        reg.sprite = (
            f"R{region_index}_DMSPRITEDEF"
        )

        parser.regions[
            reg.tag
        ] = reg

        node.worldregiontag = reg.tag

        mesh_obj = create_mesh_object_from_bmesh(
            bm_geo,
            f"R{region_index}_DMSPRITEDEF",
            ctx,
        )

        ctx.pending_region_meshes.append(
            mesh_obj
        )

        return

    plane_co, plane_no = split_result

    d_value = -plane_no.dot(
        plane_co
    )

    node.normalabcd = (
        -plane_no.x,
        -plane_no.y,
        -plane_no.z,
        -float(d_value),
    )

    node.fronttree = (
        ctx.worldnode_counter[0]
    )

    # ------------------------------------------------------------
    # Split geometry
    # ------------------------------------------------------------

    bm_geo_front, bm_geo_back = terrain_split(
        bm_geo,
        plane_co,
        plane_no,
    )

    bm_vol_front, bm_vol_back = volume_split(
        bm_vol,
        plane_co,
        plane_no,
        tol=0.0,
    )

    # Avoid useless recursion
    if (
        not bm_geo_front.faces
        or not bm_geo_back.faces
    ):
        return

    # ------------------------------------------------------------
    # Recurse
    # ------------------------------------------------------------

    recursive_indoor_bsp_split(
        ctx,
        bm_geo_front,
        bm_vol_front,
        max_faces_per_region=max_faces_per_region,
        max_depth=max_depth,
        depth=depth + 1,
        depth_counters=depth_counters,
        backtree=False,
    )

    recursive_indoor_bsp_split(
        ctx,
        bm_geo_back,
        bm_vol_back,
        max_faces_per_region=max_faces_per_region,
        max_depth=max_depth,
        depth=depth + 1,
        depth_counters=depth_counters,
        backtree=True,
    )

# import bpy
# import bmesh
# from mathutils import Vector

# EPSILON = 0.005
# DIST_TOL = 0.01

# def edges_match(e0, e1, tol):

#     a0, b0 = [v.co for v in e0.verts]
#     a1, b1 = [v.co for v in e1.verts]

#     return (
#         (
#             (a0 - a1).length < tol and
#             (b0 - b1).length < tol
#         )
#         or
#         (
#             (a0 - b1).length < tol and
#             (b0 - a1).length < tol
#         )
#     )

# def is_convex_region(
#     bm,
#     epsilon=0.005,
#     dist_tol=0.01,
# ):

#     bm_test = bm.copy()
#     bm_test.normal_update()

#     faces = list(bm_test.faces)

#     # ---------------------------------------------------
#     # Compare spatially-overlapping edges
#     # ---------------------------------------------------

#     for i, f0 in enumerate(faces):

#         n0 = f0.normal.normalized()

#         if n0.length_squared < 0.5:
#             continue

#         for f1 in faces[i + 1:]:

#             n1 = f1.normal.normalized()

#             if n1.length_squared < 0.5:
#                 continue

#             dot = n0.dot(n1)

#             # Ignore coplanar/opposite duplicate faces
#             if dot > 0.999 or dot < -0.999:
#                 continue

#             shared = False

#             # ------------------------------------------------
#             # Spatial edge comparison
#             # ------------------------------------------------

#             for e0 in f0.edges:
#                 for e1 in f1.edges:

#                     if edges_match(
#                         e0,
#                         e1,
#                         dist_tol,
#                     ):
#                         shared = True
#                         break

#                 if shared:
#                     break

#             if not shared:
#                 continue

#             c0 = f0.calc_center_median()
#             c1 = f1.calc_center_median()

#             orientation = (
#                 (c1 - c0).normalized().dot(n0)
#             )

#             if orientation < -epsilon:

#                 print(
#                     f"CONCAVE FACE PAIR: "
#                     f"{f0.index} <-> {f1.index}"
#                 )

#                 bm_test.free()
#                 return False

#     bm_test.free()
#     return True

# # -------------------------------------------------------
# # Run on selected mesh
# # -------------------------------------------------------

# obj = bpy.context.object

# if not obj or obj.type != 'MESH':
#     raise Exception("Select a mesh object.")

# bm = bmesh.new()
# bm.from_mesh(obj.data)

# result = is_convex_region(
#     bm,
#     epsilon=EPSILON,
#     dist_tol=DIST_TOL,
# )

# bm.free()

# print("\n==============================")

# if result:
#     print(f"{obj.name} IS CONVEX")
# else:
#     print(f"{obj.name} IS NOT CONVEX")

# print("==============================")