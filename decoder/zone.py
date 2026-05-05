import bpy, bmesh
from mathutils import Vector


def create_convex_from_planes(planes, size=10000.0):

    bm = bmesh.new()

    bmesh.ops.create_cube(bm, size=1.0)

    bmesh.ops.scale(
        bm,
        vec=(size, size, size),
        verts=bm.verts
    )

    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]

    for n, d in planes:

        plane_co = n * d
        plane_no = n.normalized()

        bmesh.ops.bisect_plane(
            bm,
            geom=geom,
            plane_co=plane_co,
            plane_no=plane_no,
            clear_outer=True,
            clear_inner=False,
            use_snap_center=False,
        )

        boundary_edges = [e for e in bm.edges if len(e.link_faces) == 1]
        if boundary_edges:
            bmesh.ops.holes_fill(bm, edges=boundary_edges)

        geom = bm.verts[:] + bm.edges[:] + bm.faces[:]

        if not bm.verts:
            break

    bm.normal_update()
    return bm


def flip_plane(plane):
    n, d = plane
    return (-n, -d)


def get_region_planes(parser, region_tag):

    node = parser.region_to_leaf.get(region_tag)
    if not node:
        print("NO NODE FOR REGION:", region_tag)
        return []

    planes = []

    while node.parent:

        parent = node.parent

        n = parent.normal
        d = parent.d

        if parent.front is node:
            planes.append((n, d))
        else:
            planes.append((-n, -d))

        node = parent

    return planes


def build_zone_mesh_from_bsp(obj, zone, ctx):

    bm = bmesh.new()

    for region_index in zone.regionlist:

        region_tag = f"R{int(region_index):06d}"

        planes = get_region_planes(ctx.parser, region_tag)

        if not planes:
            continue

        region_bm = create_convex_from_planes(planes)

        temp_mesh = bpy.data.meshes.new("temp_zone_part")
        region_bm.to_mesh(temp_mesh)

        bm.from_mesh(temp_mesh)

        bpy.data.meshes.remove(temp_mesh)
        region_bm.free()

    mesh = obj.data
    bm.to_mesh(mesh)
    bm.free()


def decode_zone(ctx, z):
    obj = bpy.data.objects.new(z.tag, bpy.data.meshes.new(z.tag))
    ctx.collection.objects.link(obj)

    obj['quaildef'] = 'zone'
    obj.parent = ctx.parent

    obj["REGIONLIST"] = list(z.regionlist)
    obj["USERDATA"] = z.userdata

    build_zone_mesh_from_bsp(obj, z, ctx)

    return ""