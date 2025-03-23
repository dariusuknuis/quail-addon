# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from bpy.types import Object, Collection
from ..wce.wce import wce
from ..wce.dmspritedef2 import dmspritedef2
from .context import Context

def decode_dmspritedef2(ctx:Context, sprite:dmspritedef2) -> str:
    mesh = bpy.data.meshes.new(sprite.tag)
    obj = bpy.data.objects.new(sprite.tag, mesh)

    ctx.collection.objects.link(obj)
    obj.parent = ctx.parent

    obj.location = mathutils.Vector(sprite.centeroffset)

    faces_for_creation = []
    for face in sprite.dmface2s:
        faces_for_creation.append(face.triangle)

    vertices = []
    for _, vertex in enumerate(sprite.vxyzs):
        vertices.append(mathutils.Vector(vertex.vxyz))
    mesh.from_pydata(vertices, [], faces_for_creation)
    mesh.update()

    if len(sprite.uvs) == 0:
        return f"{sprite.tag} has no uvs assigned"
    uvlayer = mesh.uv_layers.new(name=sprite.tag+"_uv")
    for _, triangle in enumerate(mesh.polygons):
        vertices = list(triangle.vertices)
        for j, vertex in enumerate(vertices):
            uvlayer.data[triangle.loop_indices[j]].uv = (sprite.uvs[vertex].uv[0], sprite.uvs[vertex].uv[1]-1)

    #mesh.use_auto_smooth = True
    #mesh.normals_split_custom_set_from_vertices([list(nxyz) for nxyz in sprite.nxyzs])


    return ""