# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from ..wce.eqgmodeldef import eqgmodeldef
from .eqgmaterialdef import decode_eqgmaterialdef
from .context import Context
from ..ui.panel.eqgface import set_face_property

def decode_eqgmodeldef(ctx:Context, eqgmodeldef:eqgmodeldef, location:mathutils.Vector) -> str:
    mesh = bpy.data.meshes.new(eqgmodeldef.tag)
    obj = bpy.data.objects.new(eqgmodeldef.tag, mesh)
    ctx.collection.objects.link(obj)

    obj.parent = ctx.parent
    obj.location = location
    obj['quaildef'] = 'eqgmodeldef'
    obj.quail_eqgmodeldef.version = str(eqgmodeldef.version) # type: ignore

    for _, mat in enumerate(eqgmodeldef.materials):
        properties = []
        for _, prop in enumerate(mat.properties):
            properties.append((prop.property[0], prop.property[1], prop.property[2]))
        textures = []
        for _, tex in enumerate(mat.animtextures):
            textures.append(tex.texture)
        err = decode_eqgmaterialdef(ctx, mesh, eqgmodeldef.tag, mat.materialtag, mat.shadertag, mat.hexoneflag, properties, mat.animsleep, textures)
        if err != "":
            return f"decode {mat.materialtag}: {err}"

    faces_for_creation = []
    for face in eqgmodeldef.faces:
        faces_for_creation.append(face.triangle)

    vertices = []
    for _, vertex in enumerate(eqgmodeldef.vertices):
        vertices.append(mathutils.Vector(vertex.xyz))
    mesh.from_pydata(vertices, [], faces_for_creation)
    mesh.update()

    uvlayer = mesh.uv_layers.new(name=eqgmodeldef.tag+"_uv")
    for _, triangle in enumerate(mesh.polygons):
        vertices = list(triangle.vertices)
        for j, vertex in enumerate(vertices):
            src_vert = eqgmodeldef.vertices[vertex]
            uvlayer.data[triangle.loop_indices[j]].uv = (src_vert.uv[0], src_vert.uv[1]-1)

    for i, face in enumerate(eqgmodeldef.faces):
        poly = mesh.polygons[i]

        poly.material_index = mesh.materials.find(f"{eqgmodeldef.tag}_{face.material}")
        if poly.material_index == -1:
            return f"Material {eqgmodeldef.tag}_{face.material} not found"

        set_face_property(mesh, i, "passable", face.passable)
        set_face_property(mesh, i, "collisionrequired", face.collisionrequired)
        set_face_property(mesh, i, "transparent", face.transparent)
        set_face_property(mesh, i, "culled", face.culled)
        set_face_property(mesh, i, "degenerate", face.degenerate)


    mesh.update()
    return ""


