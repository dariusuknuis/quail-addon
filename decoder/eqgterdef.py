# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from ..wce.eqgterdef import eqgterdef
from .eqgmaterialdef import decode_eqgmaterialdef
from .context import Context

def decode_eqgterdef(ctx:Context, eqgterdef:eqgterdef, location:mathutils.Vector) -> str:
    mesh = bpy.data.meshes.new(eqgterdef.tag)
    obj = bpy.data.objects.new(eqgterdef.tag, mesh)
    ctx.collection.objects.link(obj)

    obj.parent = ctx.parent
    obj.location = location
    obj['quaildef'] = 'eqgterdef'
    obj.quail_eqgterdef.version = str(eqgterdef.version) # type: ignore

    for _, mat in enumerate(eqgterdef.materials):
        properties = []
        for _, prop in enumerate(mat.properties):
            properties.append((prop.property[0], prop.property[1], prop.property[2]))
        textures = []
        for _, tex in enumerate(mat.textures):
            textures.append(tex.texture)
        err = decode_eqgmaterialdef(ctx, mesh, eqgterdef.tag, mat.materialtag, mat.shadertag, mat.hexoneflag, properties, mat.animsleep, textures)
        if err != "":
            return f"decode {mat.materialtag}: {err}"

    faces_for_creation = []
    for face in eqgterdef.faces:
        faces_for_creation.append(face.triangle)

    vertices = []
    for _, vertex in enumerate(eqgterdef.vertices):
        vertices.append(mathutils.Vector(vertex.xyz))
    mesh.from_pydata(vertices, [], faces_for_creation)
    mesh.update()

    uvlayer = mesh.uv_layers.new(name=eqgterdef.tag+"_uv")
    for _, triangle in enumerate(mesh.polygons):
        vertices = list(triangle.vertices)
        for j, vertex in enumerate(vertices):
            src_vert = eqgterdef.vertices[vertex]
            uvlayer.data[triangle.loop_indices[j]].uv = (src_vert.uv[0], src_vert.uv[1])

    return ""


