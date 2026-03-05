# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from bpy.types import Object, Collection
from ..wce.wce import wce
from ..wce.dmspritedef2 import dmspritedef2
from ..wce.materialdefinition import materialdefinition
from .context import Context

def decode_dmspritedef2(ctx:Context, sprite:dmspritedef2) -> str:
    mesh = bpy.data.meshes.new(sprite.tag)
    obj = bpy.data.objects.new(sprite.tag, mesh)
    ctx.collection.objects.link(obj)


    obj.parent = ctx.parent

    obj.location = mathutils.Vector(sprite.centeroffset)

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
    for face in sprite.face2s:
        i0, i1, i2 = face.triangle
        faces.append((i2, i1, i0))

    vertices = []
    for _, vertex in enumerate(sprite.vertices):
        vertices.append(mathutils.Vector(vertex.vxyz))
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    if len(sprite.uvs) > 0:
        uvlayer = mesh.uv_layers.new()
        for triangle in mesh.polygons:
            vertices = list(triangle.vertices)
            for j, vertex in enumerate(vertices):
                uvlayer.data[triangle.loop_indices[j]].uv = (
                    sprite.uvs[vertex].uv[0],
                    sprite.uvs[vertex].uv[1]
                )

    if len(sprite.vertexnormals) == 0:
        return f"{sprite.tag} has no normals assigned"

    normal_attr = mesh.attributes.new(
        name="vertex_normals",
        type='FLOAT_VECTOR',
        domain='POINT'
    )

    for i in range(len(sprite.vertexnormals)):
        normal_attr.data[i].vector = (
            sprite.vertexnormals[i].nxyz[0],
            sprite.vertexnormals[i].nxyz[1],
            sprite.vertexnormals[i].nxyz[2]
        )

    if len(sprite.vertexcolors) > 0:
        color_attribute = mesh.color_attributes.new(name="vertex_colors", domain="POINT", type='FLOAT_COLOR')
        for i, color in enumerate(sprite.vertexcolors):
            if i >= len(color_attribute.data):
                break

            color_attribute.data[i].color = (
                color.rgba[0] / 255.0,
                color.rgba[1] / 255.0,
                color.rgba[2] / 255.0,
                color.rgba[3] / 255.0
            )

    if len(sprite.vertexmaterialgroups) == 0:
        return f"{sprite.tag} has no vertex material groups"

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

    return ""