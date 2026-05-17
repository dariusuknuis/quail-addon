import bpy, bmesh
import mathutils
from ..wce.dmspritedef2 import dmspritedef2
from .dmtrackdef2 import encode_dmtrackdef2

def encode_dmspritedef2(parser, obj) -> str:

    if obj.get("quaildef") != "dmspritedef2":
        return ""

    mesh = obj.data
    props = obj.quail_dmspritedef2

    # Rebuild Vertex_Material_Index
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

        vert_sort_data.append((
            vert.index,
            vg_index,
            mat_index,
        ))

    vert_sort_data.sort(
        key=lambda x: (x[1], x[2], x[0],)
    )

    old_to_new_vert = {}
    for new_index, (old_index, _, _) in enumerate(
        vert_sort_data
    ):
        old_to_new_vert[old_index] = new_index

    verts = [
        mesh.vertices[old].co.copy()
        for old, _, _ in vert_sort_data
    ]

    faces = []
    face_materials = []
    face_passable = []
    passable_attr = mesh.attributes.get(
        "PASSABLE"
    )

    for poly_index, poly in enumerate(mesh.polygons):
        remapped = [
            old_to_new_vert[v]
            for v in poly.vertices
        ]

        faces.append(remapped)
        face_materials.append(
            poly.material_index
        )

        if passable_attr:
            face_passable.append(
                int(passable_attr.data[poly_index].value)
            )
        else:
            face_passable.append(0)

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
            saved_vertex_materials.append(
                bm_vert[material_layer]
            )

    saved_vertex_groups = {}
    for old_index, _, _ in vert_sort_data:
        dvert = mesh.vertices[old_index]
        saved_vertex_groups[old_index] = []
        for g in dvert.groups:
            vg_name = obj.vertex_groups[g.group].name
            saved_vertex_groups[old_index].append((
                vg_name,
                g.weight,
            ))

    saved_group_names = [
        vg.name
        for vg in obj.vertex_groups
    ]

    bm.free()

    # Rebuild geometry
    materials = list(mesh.materials)
    mesh.clear_geometry()
    mesh.from_pydata(
        verts,
        [],
        faces
    )

    mesh.update()
    mesh.materials.clear()
    for mat in materials:
        mesh.materials.append(mat)

    if saved_uvs:
        uv_layer = mesh.uv_layers.new()
        for poly_index, poly in enumerate(
            mesh.polygons
        ):
            for j, li in enumerate(
                poly.loop_indices
            ):
                uv_layer.data[li].uv = (
                    saved_uvs[poly_index][j]
                )

    for i, poly in enumerate(mesh.polygons):
        poly.material_index = face_materials[i]

    passable_attr = mesh.attributes.get(
        "PASSABLE"
    )

    if not passable_attr:
        passable_attr = mesh.attributes.new(
            name="PASSABLE",
            type='INT',
            domain='FACE'
        )

    for i in range(len(mesh.polygons)):
        passable_attr.data[i].value = (
            face_passable[i]
        )

    if saved_normals:
        attr = mesh.attributes.get(
            "vertex_normals"
        )

        if not attr:
            attr = mesh.attributes.new(
                name="vertex_normals",
                type='FLOAT_VECTOR',
                domain='POINT'
            )

        for i in range(len(saved_normals)):
            attr.data[i].vector = (
                saved_normals[i]
            )

    if saved_colors:
        attr = mesh.color_attributes.get(
            "vertex_colors"
        )

        if not attr:
            attr = mesh.color_attributes.new(
                name="vertex_colors",
                type='FLOAT_COLOR',
                domain='POINT'
            )

        for i in range(len(saved_colors)):
            attr.data[i].color = (
                saved_colors[i]
            )

    attr = mesh.attributes.get(
        "Vertex_Material_Index"
    )

    if not attr:
        attr = mesh.attributes.new(
            name="Vertex_Material_Index",
            type='INT',
            domain='POINT'
        )

    for i in range(len(saved_vertex_materials)):
        attr.data[i].value = (
            saved_vertex_materials[i]
        )

    obj.vertex_groups.clear()
    for group_name in saved_group_names:
        obj.vertex_groups.new(name=group_name)

    for new_index, (old_index, _, _) in enumerate(
        vert_sort_data
    ):
        groups = saved_vertex_groups.get(
            old_index,
            []
        )

        for vg_name, weight in groups:
            vg = obj.vertex_groups.get(vg_name)
            if not vg:
                continue

            vg.add(
                [new_index],
                weight,
                'ADD'
            )

    mesh.update()

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

    wce_sprite.tag = obj.name

    loc = obj.location
    wce_sprite.usecenteroffset = 1 if props.usecenteroffset else 0
    wce_sprite.centeroffset = (loc.x, loc.y, loc.z)

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
    # UVs (POINT domain fallback for loose verts ONLY)
    # ----------------------------------------
    wce_sprite.uvs = []

    point_uv_attr = mesh.attributes.get("vertex_uvs")

    # ----------------------------------------
    # Build set of vertices actually used by faces
    # ----------------------------------------
    used_verts = set()
    for poly in mesh.polygons:
        used_verts.update(poly.vertices)

    # ----------------------------------------
    # Build loop-based UV map (only for used verts)
    # ----------------------------------------
    uv_map = {}
    if mesh.uv_layers:
        uv_layer = mesh.uv_layers.active

        for poly in mesh.polygons:
            for li, vi in zip(poly.loop_indices, poly.vertices):
                uv_map[vi] = uv_layer.data[li].uv

    # ----------------------------------------
    # Assign UVs
    # ----------------------------------------
    for i in range(len(mesh.vertices)):

        if i in used_verts:
            # Face vertex → use loop UV (same behavior as before)
            uv = uv_map.get(i, (0.0, 0.0))

        elif point_uv_attr:
            # Loose vertex → use POINT domain UV
            uv = point_uv_attr.data[i].vector

        else:
            uv = (0.0, 0.0)

        uvi = dmspritedef2.uv()
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

    wce_sprite.skinassignmentgroups = ["0"]

    if obj.vertex_groups:

        packed = []

        current_group = None
        current_count = 0

        for v in mesh.vertices:

            group_index = -1

            if v.groups:
                group_index = v.groups[0].group

            if current_group != group_index:

                if current_group is not None:

                    packed.append((
                        current_count,
                        current_group
                    ))

                current_group = group_index
                current_count = 0

            current_count += 1

        if current_group is not None:

            packed.append((
                current_count,
                current_group
            ))

        wce_sprite.skinassignmentgroups = [
            str(len(packed))
        ]

        for count, group in packed:

            wce_sprite.skinassignmentgroups.append(
                str(count)
            )

            wce_sprite.skinassignmentgroups.append(
                str(group)
            )

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

    passable_attr = mesh.attributes.get(
        "PASSABLE"
    )

    for poly_index, poly in enumerate(
        mesh.polygons
    ):

        f = dmspritedef2.dmface2()

        if passable_attr:
            f.passable = int(
                passable_attr.data[poly_index].value
            )
        else:
            f.passable = 0

        v = poly.vertices

        f.triangle = (
            int(v[2]),
            int(v[1]),
            int(v[0]),
        )

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
    # DMTRACKDEF2 shape key animation
    # ----------------------------------------
    if mesh.shape_keys and mesh.shape_keys.get("quaildef") == "dmtrackdef2":

        err = encode_dmtrackdef2(parser, obj)
        if err:
            return err

        key_props = mesh.shape_keys.quail_dmtrackdef2

        if key_props.tag:
            wce_sprite.dmtrackinst = key_props.tag

    # ----------------------------------------
    # Store
    # ----------------------------------------
    parser.dmspritedef2s[wce_sprite.tag] = wce_sprite

    return ""