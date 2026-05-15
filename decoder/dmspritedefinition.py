# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from bpy.types import Object, Collection
from ..common.mesh import get_vertex_normal_nodegroup
from ..common.region import is_region_mesh, is_zone_collection
from ..wce.wce import wce
from ..wce.dmspritedefinition import dmspritedefinition
from .context import Context

def find_hsprite_for_mesh(parser, mesh_name):

    for hs in parser.hierarchicalspritedefs.values():

        for skin in hs.attachedskins:

            tag = skin.dmsprite

            # exact match
            if tag == mesh_name:
                return hs, skin

            # prefix match (BAM -> BAM01 etc)
            if mesh_name.startswith(tag.replace("_DMSPRITEDEF","")):
                return hs, skin

    return None, None

def decode_dmspritedefinition(ctx:Context, sprite:dmspritedefinition) -> str:
    mesh = bpy.data.meshes.new(sprite.tag)
    obj = bpy.data.objects.new(sprite.tag, mesh)
    # Decide target collection
    target_collection = ctx.collection

    if is_region_mesh(sprite.tag) and is_zone_collection(ctx.collection):
        region_mesh_collection = getattr(ctx, "region_mesh_collection", None)

        if region_mesh_collection:
            target_collection = region_mesh_collection

    target_collection.objects.link(obj)
    obj['quaildef'] = 'dmspritedefinition'

    obj.parent = ctx.parent

    # ------------------------------------------------
    # Populate properties for panel
    # ------------------------------------------------

    props = obj.quail_dmspritedefinition

    props.fragment1 = sprite.fragment1
    props.fragment3 = sprite.fragment3

    props.materialpalette = bpy.data.objects.get(sprite.materialpalette)

    # CENTER
    if sprite.center:
        props.hascenter = True
    else:
        props.hascenter = False

    # PARAMS1
    if sprite.params1:
        props.hasparams1 = True
        props.params1_x, props.params1_y, props.params1_z = sprite.params1
    else:
        props.hasparams1 = False

    # PARAMS2
    if sprite.params2:
        props.hasparams2 = True
        props.params2_x, props.params2_y, props.params2_z = sprite.params2
    else:
        props.hasparams2 = False

    props.data8 = sprite.data8

    # ------------------------------------------------
    # Build mesh
    # ------------------------------------------------

    hsprite, skin = find_hsprite_for_mesh(ctx.parser, sprite.tag)
    if hsprite:
        obj["hsprite"] = hsprite.tag
        print(obj.name, "->", obj.get("hsprite"))

    center = sprite.center or (0.0, 0.0, 0.0)
    obj.location = mathutils.Vector(center)

    if sprite.materialpalette != "":
        materialpalette = ctx.parser.materialpalettes.get(sprite.materialpalette)

        if materialpalette:
            for src_mp_mat in materialpalette.materials:
                mat_name = src_mp_mat.material

                # Try to find existing material
                mat = bpy.data.materials.get(mat_name)

                # If not found, create simple default material
                if mat is None:
                    mat = bpy.data.materials.new(mat_name)
                    mat.use_nodes = True

                    nodes = mat.node_tree.nodes
                    links = mat.node_tree.links

                    nodes.clear()

                    principled = nodes.new("ShaderNodeBsdfPrincipled")
                    principled.location = (0, 0)

                    output = nodes.new("ShaderNodeOutputMaterial")
                    output.location = (300, 0)

                    links.new(principled.outputs["BSDF"], output.inputs["Surface"])

                # Add to object if not already
                if obj.data.materials.find(mat_name) == -1:
                    obj.data.materials.append(mat)

    faces = []
    for face in sprite.faces:
        i0, i1, i2 = face.triangle
        faces.append((i2, i1, i0))

    vertices = []
    for _, vertex in enumerate(sprite.vertices):
        vertices.append(mathutils.Vector(vertex.vxyz))
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    # ----------------------------------------
    # DMFACE FLAG + DATA
    # ----------------------------------------

    flag_attr = mesh.attributes.new(
        name="FLAG",
        type='INT',
        domain='FACE'
    )

    data_attr = mesh.color_attributes.new(
        name="DATA",
        type='BYTE_COLOR',
        domain='FACE'
    )

    for i, face in enumerate(sprite.faces):

        if i >= len(mesh.polygons):
            break

        flag_attr.data[i].value = face.flag

        data_attr.data[i].color = (
            face.data[0],
            face.data[1],
            face.data[2],
            face.data[3],
        )

    if len(sprite.texcoords) > 0:
        uvlayer = mesh.uv_layers.new()
        for triangle in mesh.polygons:
            vertices = list(triangle.vertices)
            for j, vertex in enumerate(vertices):
                uvlayer.data[triangle.loop_indices[j]].uv = (
                    sprite.texcoords[vertex].uv[0],
                    sprite.texcoords[vertex].uv[1]
                )

    # ----------------------------------------
    # Vertex UVs (POINT domain) for loose verts
    # ----------------------------------------
    if len(sprite.texcoords) > 0:
        uv_attr = mesh.attributes.new(
            name="vertex_uvs",
            type='FLOAT2',
            domain='POINT'
        )

        for i, uv in enumerate(sprite.texcoords):
            if i >= len(uv_attr.data):
                break
            uv_attr.data[i].vector = (
                uv.uv[0],
                uv.uv[1]
            )

    if len(sprite.normals) > 0:
        normal_attr = mesh.attributes.new(
            name="vertex_normals",
            type='FLOAT_VECTOR',
            domain='POINT'
        )

        for i in range(len(sprite.normals)):
            normal_attr.data[i].vector = (
                sprite.normals[i].nxyz[0],
                sprite.normals[i].nxyz[1],
                sprite.normals[i].nxyz[2]
            )

        nodegroup = get_vertex_normal_nodegroup()

        mod = obj.modifiers.new("VertexNormals", 'NODES')
        mod.node_group = nodegroup

    if len(sprite.colors) > 0:
        color_attribute = mesh.color_attributes.new(name="vertex_colors", domain="POINT", type='FLOAT_COLOR')
        for i, color in enumerate(sprite.colors):
            if i >= len(color_attribute.data):
                break

            color_attribute.data[i].color = (
                color.rgba[0] / 255.0,
                color.rgba[1] / 255.0,
                color.rgba[2] / 255.0,
                color.rgba[3] / 255.0
            )

    if len(sprite.vertexmaterialgroups) > 0:
        vertex_material_attribute = mesh.attributes.new(name="Vertex_Material_Index", type='INT', domain='POINT')
        vertex_index = 0
        count = 0
        for i, vmg in enumerate(sprite.vertexmaterialgroups):
            if i % 2 == 0:
                count = int(vmg)
                continue
            mat_index = int(vmg)
            for _ in range(count):
                if vertex_index >= len(vertex_material_attribute.data):
                    break
                vertex_material_attribute.data[vertex_index].value = mat_index  # type: ignore
                vertex_index += 1

    if len(sprite.facematerialgroups) > 0:

        groups = sprite.facematerialgroups

        group_count = int(groups[0])
        expected_len = 1 + group_count * 2

        if len(groups) != expected_len:
            return f"FACEMATERIALGROUPS length mismatch: expected {expected_len}, got {len(groups)}"

        face_index = 0

        for g in range(group_count):
            count = int(groups[1 + g*2])
            mat_index = int(groups[1 + g*2 + 1])

            if mat_index < 0 or mat_index >= len(materialpalette.materials):
                return f"material index {mat_index+1} out of range (1-{len(materialpalette.materials)})"

            materialName = materialpalette.materials[mat_index].material

            obj_mat_index = obj.data.materials.find(materialName)
            if obj_mat_index == -1:
                return f"material {materialName} not found in object {obj.name}"

            for _ in range(count):
                if face_index >= len(mesh.polygons):
                    return f"fmg assign: face index {face_index} out of range (0-{len(mesh.polygons)-1})"

                mesh.polygons[face_index].material_index = obj_mat_index
                face_index += 1

    if hsprite and skin:
        for dag in hsprite.dags:
            obj.vertex_groups.new(name=dag.tag)

    groups = sprite.skinassignmentgroups

    group_count = int(groups[0])
    expected_len = 1 + group_count * 2

    if len(groups) != expected_len:
        return f"SKINASSIGNMENTGROUPS length mismatch: expected {expected_len}, got {len(groups)}"

    vertex_index = 0

    for g in range(group_count):

        count = int(groups[1 + g*2])
        dag_index = int(groups[1 + g*2 + 1])

        if dag_index >= len(hsprite.dags):
            vertex_index += count
            continue

        group_name = hsprite.dags[dag_index].tag
        vg = obj.vertex_groups.get(group_name)

        for _ in range(count):

            if vertex_index >= len(mesh.vertices):
                break

            if vg:
                vg.add([vertex_index], 1.0, 'REPLACE')

            vertex_index += 1

    return ""