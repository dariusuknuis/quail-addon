import bpy, bmesh
import mathutils
from ..wce.dmspritedefinition import dmspritedefinition

def encode_dmspritedefinition(parser, obj) -> str:

    if obj.get("quaildef") != "dmspritedefinition":
        return ""

    mesh = obj.data
    props = obj.quail_dmspritedefinition

    bm = bmesh.new()
    bm.from_mesh(mesh)

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    material_layer = bm.verts.layers.int.get(
        "Vertex_Material_Index"
    )

    if not material_layer:
        material_layer = bm.verts.layers.int.new(
            "Vertex_Material_Index"
        )

    for vert in bm.verts:
        if not vert.link_faces:
            continue

        vert[material_layer] = (
            vert.link_faces[0].material_index
        )

    bm.to_mesh(mesh)
    bm.free()

    mesh.update()

    bm = bmesh.new()
    bm.from_mesh(mesh)

    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    material_layer = bm.verts.layers.int.get(
        "Vertex_Material_Index"
    )

    vert_sort_data = []
    for vert in bm.verts:
        vg_index = -1
        dvert = mesh.vertices[vert.index]
        if dvert.groups:
            vg_index = dvert.groups[0].group

        mat_index = 0
        if material_layer:
            mat_index = vert[material_layer]

        vert_sort_data.append((vert.index, vg_index, mat_index))
    vert_sort_data.sort(key=lambda x: (x[1], x[2], x[0]))
    old_to_new_vert = {}
    for new_index, (old_index, _, _) in enumerate(
        vert_sort_data
    ):
        old_to_new_vert[old_index] = new_index

    # Save geometry
    verts = [
        mesh.vertices[old].co.copy()
        for old, _, _ in vert_sort_data
    ]

    faces = []
    face_materials = []
    face_flags = []
    face_data = []
    flag_attr = mesh.attributes.get("FLAG")
    data_attr = mesh.color_attributes.get("DATA")
    for poly_index, poly in enumerate(mesh.polygons):
        remapped = [old_to_new_vert[v] for v in poly.vertices]
        faces.append(remapped)
        face_materials.append(poly.material_index)
        if flag_attr:
            face_flags.append(
                int(flag_attr.data[poly_index].value)
            )

        else:
            face_flags.append(75)

        if data_attr:
            c = data_attr.data[poly_index].color
            face_data.append((c[0], c[1], c[2], c[3]))

        else:
            face_data.append((0, 0, 0, 0,))

    saved_uvs = []
    if mesh.uv_layers:
        uv_layer = mesh.uv_layers.active
        for poly in mesh.polygons:
            poly_uvs = []
            for li in poly.loop_indices:
                poly_uvs.append(
                    uv_layer.data[li].uv.copy()
                )

            saved_uvs.append(poly_uvs)

    saved_normals = []
    normal_attr = mesh.attributes.get("vertex_normals")
    if normal_attr:
        for old_index, _, _ in vert_sort_data:
            saved_normals.append(
                normal_attr.data[old_index].vector.copy()
            )

    saved_colors = []
    color_attr = mesh.color_attributes.get("vertex_colors")
    if color_attr:
        for old_index, _, _ in vert_sort_data:
            saved_colors.append(
                color_attr.data[old_index].color[:]
            )

    saved_vertex_materials = []
    if material_layer:
        for old_index, _, _ in vert_sort_data:
            bm_vert = bm.verts[old_index]
            saved_vertex_materials.append(bm_vert[material_layer])

    saved_vertex_groups = {}
    for old_index, _, _ in vert_sort_data:
        dvert = mesh.vertices[old_index]
        saved_vertex_groups[old_index] = []
        for g in dvert.groups:
            vg_name = obj.vertex_groups[g.group].name
            saved_vertex_groups[old_index].append((vg_name, g.weight))

    saved_group_names = [
        vg.name
        for vg in obj.vertex_groups
    ]

    bm.free()

    sorted_face_data = sorted(
        zip(faces, face_materials, face_flags, face_data, saved_uvs),
        key=lambda x: x[1]
    )

    faces = [x[0] for x in sorted_face_data]
    face_materials = [x[1] for x in sorted_face_data]
    face_flags = [x[2] for x in sorted_face_data]
    face_data = [x[3] for x in sorted_face_data]
    saved_uvs = [x[4] for x in sorted_face_data]

    # Rebuild geometry
    materials = list(mesh.materials)
    mesh.clear_geometry()
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    mesh.materials.clear()
    for mat in materials:
        mesh.materials.append(mat)

    if saved_uvs:
        uv_layer = mesh.uv_layers.new()
        for poly_index, poly in enumerate(mesh.polygons):
            for j, li in enumerate(poly.loop_indices):
                uv_layer.data[li].uv = (saved_uvs[poly_index][j])

    for i, poly in enumerate(mesh.polygons):
        poly.material_index = (face_materials[i])
        poly.use_smooth = True

    flag_attr = mesh.attributes.get("FLAG")
    if not flag_attr:
        flag_attr = mesh.attributes.new(name="FLAG", type='INT', domain='FACE')

    for i in range(len(mesh.polygons)):
        flag_attr.data[i].value = (face_flags[i])

    data_attr = mesh.color_attributes.get("DATA")
    if not data_attr:
        data_attr = mesh.color_attributes.new(
            name="DATA",
            type='FLOAT_COLOR',
            domain='FACE'
        )

    for i in range(len(mesh.polygons)):
        data_attr.data[i].color = (face_data[i])

    if saved_normals:
        attr = mesh.attributes.get("vertex_normals")
        if not attr:
            attr = mesh.attributes.new(
                name="vertex_normals",
                type='FLOAT_VECTOR',
                domain='POINT'
            )

        for i in range(len(saved_normals)):
            attr.data[i].vector = (saved_normals[i])

    if saved_colors:
        attr = mesh.color_attributes.get("vertex_colors")
        if not attr:
            attr = mesh.color_attributes.new(
                name="vertex_colors",
                type='FLOAT_COLOR',
                domain='POINT'
            )

        for i in range(len(saved_colors)):
            attr.data[i].color = (saved_colors[i])

    attr = mesh.attributes.get("Vertex_Material_Index")
    if not attr:
        attr = mesh.attributes.new(
            name="Vertex_Material_Index",
            type='INT',
            domain='POINT'
        )

    for i in range(len(saved_vertex_materials)):
        attr.data[i].value = (saved_vertex_materials[i])

    obj.vertex_groups.clear()
    for group_name in saved_group_names:
        obj.vertex_groups.new(name=group_name)

    for new_index, (old_index, _, _) in enumerate(vert_sort_data):
        groups = saved_vertex_groups.get(old_index,[])
        for vg_name, weight in groups:
            vg = obj.vertex_groups.get(vg_name)
            if not vg:
                continue

            vg.add([new_index],weight,'ADD')

    mesh.update()

    wce_sprite = dmspritedefinition()

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
    # Basic properties
    # ----------------------------------------
    wce_sprite.tag = obj.name

    wce_sprite.fragment1 = props.fragment1

    wce_sprite.materialpalette = (
        props.materialpalette.name if props.materialpalette else ""
    )

    wce_sprite.fragment3 = props.fragment3

    # ----------------------------------------
    # CENTER
    # ----------------------------------------
    if props.hascenter:
        loc = obj.location
        wce_sprite.center = (
            float(loc.x),
            float(loc.y),
            float(loc.z),
        )
    else:
        wce_sprite.center = None

    # ----------------------------------------
    # PARAMS1
    # ----------------------------------------
    if props.hasparams1:
        wce_sprite.params1 = (
            float(props.params1_x),
            float(props.params1_y),
            float(props.params1_z),
        )
    else:
        wce_sprite.params1 = None

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

        vobj = dmspritedefinition.vxyz()
        vobj.vxyz = (
            float(v_co.x),
            float(v_co.y),
            float(v_co.z),
        )

        wce_sprite.vertices.append(vobj)

    # ----------------------------------------
    # UVs (POINT domain fallback for loose verts ONLY)
    # ----------------------------------------
    wce_sprite.texcoords = []

    point_uv_attr = mesh.attributes.get("vertex_uvs")

    used_verts = set()
    for poly in mesh.polygons:
        used_verts.update(poly.vertices)

    uv_map = {}

    if mesh.uv_layers:
        uv_layer = mesh.uv_layers.active

        for poly in mesh.polygons:
            for li, vi in zip(poly.loop_indices, poly.vertices):
                uv_map[vi] = uv_layer.data[li].uv

    for i in range(len(mesh.vertices)):

        if i in used_verts:
            uv = uv_map.get(i, (0.0, 0.0))

        elif point_uv_attr:
            uv = point_uv_attr.data[i].vector

        else:
            uv = (0.0, 0.0)

        uvi = dmspritedefinition.uv()
        uvi.uv = (
            float(uv[0]),
            float(uv[1]),
        )

        wce_sprite.texcoords.append(uvi)

    # ----------------------------------------
    # Vertex normals
    # ----------------------------------------
    wce_sprite.normals = []

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

            nobj = dmspritedefinition.nxyz()
            nobj.nxyz = (
                float(n.x),
                float(n.y),
                float(n.z),
            )

            wce_sprite.normals.append(nobj)

    # ----------------------------------------
    # Vertex colors
    # ----------------------------------------
    wce_sprite.colors = []

    color_attr = mesh.color_attributes.get("vertex_colors")

    if color_attr:

        for i in range(len(mesh.vertices)):

            c = color_attr.data[i].color

            robj = dmspritedefinition.rgba()
            robj.rgba = (
                int(c[0] * 255),
                int(c[1] * 255),
                int(c[2] * 255),
                int(c[3] * 255),
            )

            wce_sprite.colors.append(robj)

    # ----------------------------------------
    # Faces
    # ----------------------------------------

    wce_sprite.faces = []

    flag_attr = mesh.attributes.get("FLAG")
    data_attr = mesh.color_attributes.get("DATA")

    for poly in mesh.polygons:

        f = dmspritedefinition.dmface()

        # ----------------------------------------
        # FLAG
        # ----------------------------------------

        if flag_attr:
            f.flag = int(flag_attr.data[poly.index].value)
        else:
            f.flag = 75

        # ----------------------------------------
        # DATA
        # ----------------------------------------

        if data_attr:

            c = data_attr.data[poly.index].color

            f.data = (
                int(c[0]),
                int(c[1]),
                int(c[2]),
                int(c[3]),
            )

        else:
            f.data = (0, 0, 0, 0)

        # ----------------------------------------
        # Triangle indices
        # ----------------------------------------

        v = poly.vertices

        f.triangle = (
            int(v[2]),
            int(v[1]),
            int(v[0]),
        )

        wce_sprite.faces.append(f)

    # ----------------------------------------
    # MeshOps
    # ----------------------------------------
    wce_sprite.meshops = []

    # ----------------------------------------
    # Skin Assignment Groups
    # ----------------------------------------
    wce_sprite.skinassignmentgroups = ["0"]

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
    # DATA8
    # ----------------------------------------
    wce_sprite.data8 = props.data8

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
    # PARAMS2
    # ----------------------------------------
    if props.hasparams2:

        wce_sprite.params2 = (
            float(props.params2_x),
            float(props.params2_y),
            float(props.params2_z),
        )

    else:
        wce_sprite.params2 = None

    # ----------------------------------------
    # Store
    # ----------------------------------------
    parser.dmspritedefinitions[wce_sprite.tag] = wce_sprite

    return ""