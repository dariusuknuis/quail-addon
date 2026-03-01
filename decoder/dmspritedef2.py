# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from bpy.types import Object, Collection
from ..wce.wce import wce
from ..wce.dmspritedef2 import dmspritedef2
from ..wce.materialdefinition import materialdefinition
from .context import Context
from .material import create_material

def decode_dmspritedef2(ctx:Context, sprite:dmspritedef2) -> str:
    mesh = bpy.data.meshes.new(sprite.tag)
    obj = bpy.data.objects.new(sprite.tag, mesh)
    ctx.collection.objects.link(obj)


    obj.parent = ctx.parent

    obj.location = mathutils.Vector(sprite.centeroffset)

    if sprite.materialpalette != "":
        materialpalette = ctx.parser.materialpalettes[sprite.materialpalette]
        if materialpalette is None:
            return f"materialpalette {sprite.materialpalette} not found"

        for src_mp_mat in materialpalette.materials:
            mat_name = src_mp_mat.material
            src_material = None # type: materialdefinition|None
            for key, mat in ctx.parser.materialdefinitions.items():
                if mat.tag == mat_name:
                    src_material = mat
                    break
            if src_material is None:
                return f"materialpalette refers to material {mat_name}, but not found in materials"
            err = create_material(ctx, src_material)
            if err != "":
                return f"create material {mat_name}: {err}"
            mat = bpy.data.materials.get(mat_name)
            if mat and obj.data.materials.find(mat_name) == -1:
                obj.data.materials.append(mat)

    faces = []
    for face in sprite.face2s:
        faces.append(face.triangle)

    vertices = []
    for _, vertex in enumerate(sprite.vertices):
        vertices.append(mathutils.Vector(vertex.vxyz))
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    if len(sprite.uvs) == 0:
        return f"{sprite.tag} has no uvs assigned"
    uvlayer = mesh.uv_layers.new(name=sprite.tag+"_uv")
    for _, triangle in enumerate(mesh.polygons):
        vertices = list(triangle.vertices)
        for j, vertex in enumerate(vertices):
            uvlayer.data[triangle.loop_indices[j]].uv = (sprite.uvs[vertex].uv[0], sprite.uvs[vertex].uv[1])

    if len(sprite.vertexnormals) == 0:
        return f"{sprite.tag} has no normals assigned"

    #mesh.use_auto_smooth = True # type: ignore
    #mesh.auto_smooth_angle = 3.14159 # type: ignore

    normals = list[list[float]]
    normals = []
    for _, normal in enumerate(sprite.vertexnormals):
        normals.append(normal.nxyz)

    mesh.normals_split_custom_set_from_vertices(normals)

    if len(sprite.vertexcolors) > 0:
        color_attribute = mesh.color_attributes.new(name="RGBA", domain="POINT", type='FLOAT_COLOR')
        v_index = 0
        for _, color in enumerate(sprite.vertexcolors):
            count = color.rgba[0]
            for i in range(count):
                color_attribute.data[v_index].color = (color.rgba[1] / 255.0, color.rgba[2] / 255.0, color.rgba[3] / 255.0) # type: ignore
                v_index += 1

    if len(sprite.vertexmaterialgroups) == 0:
        return f"{sprite.tag} has no vertex material groups"

    vertex_material_attribute = mesh.attributes.new(name="Vertex_Material_Index", type='INT', domain='POINT')
    count = 0
    for i, vmg in enumerate(sprite.vertexmaterialgroups):
        if i % 2 == 0:
            count = int(vmg)
            continue
        for j in range(count):
            vertex_material_attribute.data[j].value = int(vmg) # type: ignore

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