import bpy
import mathutils
from ..wce.dmspritedef2 import dmspritedef2

def encode_dmspritedef2(parser, obj) -> str:

    if obj.get("quaildef") != "dmspritedef2":
        return ""

    mesh = obj.data
    props = obj.quail_dmspritedef2

    wce_sprite = dmspritedef2()

    # ----------------------------------------
    # Detect if we need to unbake
    # ----------------------------------------
    unbake = False
    bone_matrices = {}

    if obj.parent and obj.parent.get("quaildef") == "hierarchicalspritedef":

        has_child_of = False
        for c in obj.constraints:
            if c.type == 'CHILD_OF' and c.target == obj.parent:
                has_child_of = True
                break

        if not has_child_of:
            unbake = True

            arm = obj.parent

            for bone in arm.data.bones:
                bone_matrices[bone.name] = arm.matrix_world @ bone.matrix_local

    # ----------------------------------------
    # Tag
    # ----------------------------------------
    wce_sprite.tag = obj.name

    # ----------------------------------------
    # Center Offset
    # ----------------------------------------
    wce_sprite.usecenteroffset = 1 if props.usecenteroffset else 0
    wce_sprite.centeroffset = (
        float(props.center_x),
        float(props.center_y),
        float(props.center_z),
    )

    # ----------------------------------------
    # Vertices
    # ----------------------------------------
    wce_sprite.vertices = []
    for v in mesh.vertices:

        v_co = v.co.copy()

        if unbake:
            for g in v.groups:
                vg = obj.vertex_groups[g.group]
                bone_name = vg.name

                if bone_name in bone_matrices:
                    inv = bone_matrices[bone_name].inverted()
                    v_co = inv @ v_co
                    break

        vobj = dmspritedef2.vxyz()
        vobj.vxyz = (float(v_co.x), float(v_co.y), float(v_co.z))
        wce_sprite.vertices.append(vobj)

    # ----------------------------------------
    # UVs (POINT domain fallback)
    # ----------------------------------------
    wce_sprite.uvs = []
    if mesh.uv_layers:
        uv_layer = mesh.uv_layers.active

        uv_map = {}

        for poly in mesh.polygons:
            for li, vi in zip(poly.loop_indices, poly.vertices):
                uv_map[vi] = uv_layer.data[li].uv

        for i in range(len(mesh.vertices)):
            uvi = dmspritedef2.uv()
            uv = uv_map.get(i, (0.0, 0.0))
            uvi.uv = (float(uv[0]), float(uv[1]))
            wce_sprite.uvs.append(uvi)

    # ----------------------------------------
    # Vertex Normals (attribute)
    # ----------------------------------------
    wce_sprite.vertexnormals = []
    attr = mesh.attributes.get("vertex_normals")

    if attr:
        for i, v in enumerate(mesh.vertices):

            n = mathutils.Vector(attr.data[i].vector)

            if unbake:
                for g in v.groups:
                    vg = obj.vertex_groups[g.group]
                    bone_name = vg.name

                    if bone_name in bone_matrices:
                        rot = bone_matrices[bone_name].to_3x3()
                        n = rot.inverted() @ n
                        break

            nobj = dmspritedef2.nxyz()
            nobj.nxyz = (float(n.x), float(n.y), float(n.z))
            wce_sprite.vertexnormals.append(nobj)

    # ----------------------------------------
    # Vertex Colors
    # ----------------------------------------
    wce_sprite.vertexcolors = []
    color_attr = mesh.color_attributes.get("vertex_colors")

    if color_attr:
        for i in range(len(mesh.vertices)):
            c = color_attr.data[i].color
            robj = dmspritedef2.rgba()
            robj.rgba = (
                int(c[0] * 255),
                int(c[1] * 255),
                int(c[2] * 255),
                int(c[3] * 255),
            )
            wce_sprite.vertexcolors.append(robj)

    # ----------------------------------------
    # Skin Assignment Groups
    # ----------------------------------------
    wce_sprite.skinassignmentgroups = []

    if obj.vertex_groups:
        counts = []
        last_group = None
        count = 0

        for v in mesh.vertices:
            group_index = -1
            for g in v.groups:
                group_index = g.group
                break

            if group_index != last_group:
                if last_group is not None:
                    counts.append((count, last_group))
                count = 0
                last_group = group_index

            count += 1

        if last_group is not None:
            counts.append((count, last_group))

        wce_sprite.skinassignmentgroups = [str(len(counts))]
        for c, g in counts:
            wce_sprite.skinassignmentgroups.append(str(c))
            wce_sprite.skinassignmentgroups.append(str(g))

    # ----------------------------------------
    # Material palette
    # ----------------------------------------
    wce_sprite.materialpalette = (
        props.materialpalette.name if props.materialpalette else ""
    )

    wce_sprite.dmtrackinst = props.dmtrack
    wce_sprite.dmrgbtrack = props.dmrgbtrack

    # ----------------------------------------
    # Polyhedron (collision)
    # ----------------------------------------
    wce_sprite.sprite = props.polyhedron.name if props.polyhedron else ""

    # ----------------------------------------
    # Faces
    # ----------------------------------------
    wce_sprite.face2s = []

    for poly in mesh.polygons:
        f = dmspritedef2.dmface2()

        f.passable = 0
        v = poly.vertices
        f.triangle = (int(v[2]), int(v[1]), int(v[0]))

        wce_sprite.face2s.append(f)

    # ----------------------------------------
    # MeshOps
    # ----------------------------------------
    wce_sprite.meshops = []

    # ----------------------------------------
    # Face Material Groups
    # ----------------------------------------
    groups = []
    if mesh.materials:
        current = None
        count = 0
        packed = []

        for poly in mesh.polygons:
            mi = poly.material_index

            if mi != current:
                if current is not None:
                    packed.append((count, current))
                current = mi
                count = 0
            count += 1

        if current is not None:
            packed.append((count, current))

        groups = [str(len(packed))]
        for c, m in packed:
            groups.append(str(c))
            groups.append(str(m))

    wce_sprite.facematerialgroups = groups

    # ----------------------------------------
    # Vertex Material Groups
    # ----------------------------------------
    attr = mesh.attributes.get("Vertex_Material_Index")
    groups = []

    if attr:
        packed = []
        current = None
        count = 0

        for i in range(len(mesh.vertices)):
            val = attr.data[i].value

            if val != current:
                if current is not None:
                    packed.append((count, current))
                current = val
                count = 0
            count += 1

        if current is not None:
            packed.append((count, current))

        groups = [str(len(packed))]
        for c, m in packed:
            groups.append(str(c))
            groups.append(str(m))

    wce_sprite.vertexmaterialgroups = groups

    # ----------------------------------------
    # Params2
    # ----------------------------------------
    wce_sprite.useparams2 = 1 if props.useparams2 else 0
    wce_sprite.params2 = (
        float(props.params2_x),
        float(props.params2_y),
        float(props.params2_z),
    )

    # ----------------------------------------
    # Bounding Box
    # ----------------------------------------
    wce_sprite.useboundingbox = 1 if props.useboundingbox else 0
    wce_sprite.boundingboxmin = (
        props.b_box_min_x,
        props.b_box_min_y,
        props.b_box_min_z,
    )
    wce_sprite.boundingboxmax = (
        props.b_box_max_x,
        props.b_box_max_y,
        props.b_box_max_z,
    )

    # ----------------------------------------
    # Bounding Radius
    # ----------------------------------------
    wce_sprite.useboundingradius = 1 if props.useboundingradius else 0
    wce_sprite.boundingradius = float(props.boundingradius)

    # ----------------------------------------
    # Misc flags
    # ----------------------------------------
    wce_sprite.fpscale = props.fpscale
    wce_sprite.usevertexcoloralpha = 1 if props.usevertexcoloralpha else 0
    wce_sprite.spritedefpolyhedron = 1 if props.spritedefpolyhedron else 0

    # ----------------------------------------
    # Store
    # ----------------------------------------
    parser.dmspritedef2s[wce_sprite.tag] = wce_sprite

    return ""