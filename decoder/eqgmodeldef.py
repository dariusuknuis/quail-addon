# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from ..wce.eqgmodeldef import eqgmodeldef
from .context import Context

def decode_eqgmodeldef(ctx:Context, eqgmodeldef:eqgmodeldef, location:mathutils.Vector) -> str:
    mesh = bpy.data.meshes.new(eqgmodeldef.tag)
    obj = bpy.data.objects.new(eqgmodeldef.tag, mesh)
    ctx.collection.objects.link(obj)

    obj.parent = ctx.parent
    obj.location = location

    faces_for_creation = []
    for face in eqgmodeldef.faces:
        faces_for_creation.append(face.triangle)

    vertices = []
    for _, vertex in enumerate(eqgmodeldef.vertexs):
        vertices.append(mathutils.Vector(vertex.xyz))
    mesh.from_pydata(vertices, [], faces_for_creation)
    mesh.update()

    uvlayer = mesh.uv_layers.new(name=eqgmodeldef.tag+"_uv")
    for _, triangle in enumerate(mesh.polygons):
        vertices = list(triangle.vertices)
        for j, vertex in enumerate(vertices):
            src_vert = eqgmodeldef.vertexs[vertex]
            uvlayer.data[triangle.loop_indices[j]].uv = (src_vert.uv[0], src_vert.uv[1]-1)

    return ""


