# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from ..wce.eqgterdef import eqgterdef
from ..common.mesh import get_vertex_normal_nodegroup
from .eqgmaterialdef import decode_eqgmaterialdef
from .context import Context
from ..ui.panel.eqgface import set_face_property

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
        for tex in mat.animtextures:
            textures.append(tex.texture)
        err = decode_eqgmaterialdef(ctx, mesh, eqgterdef.tag, mat.materialtag, mat.shadertag, properties, mat.animsleep, textures)
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

    attr = mesh.attributes.new(
        name="vertex_normals",
        type='FLOAT_VECTOR',
        domain='POINT'
    )

    for i, vertex in enumerate(eqgterdef.vertices):
        attr.data[i].vector = vertex.normal

    uvlayer = mesh.uv_layers.new(name=eqgterdef.tag+"_uv")
    for _, triangle in enumerate(mesh.polygons):
        vertices = list(triangle.vertices)
        for j, vertex in enumerate(vertices):
            src_vert = eqgterdef.vertices[vertex]
            uvlayer.data[triangle.loop_indices[j]].uv = (src_vert.uv[0], src_vert.uv[1])

    for i, face in enumerate(eqgterdef.faces):
        poly = mesh.polygons[i]

        poly.material_index = mesh.materials.find(f"{eqgterdef.tag}_{face.material}")
        if poly.material_index == -1:
            return f"Material {eqgterdef.tag}_{face.material} not found"

        set_face_property(mesh, i, "passable", face.passable)
        set_face_property(mesh, i, "collisionrequired", face.collisionrequired)
        set_face_property(mesh, i, "transparent", face.transparent)
        set_face_property(mesh, i, "culled", face.culled)
        set_face_property(mesh, i, "degenerate", face.degenerate)

    # -----------------------------------------------------
    # Add vertex normal modifier
    # -----------------------------------------------------

    nodegroup = get_vertex_normal_nodegroup()

    mod = obj.modifiers.new("VertexNormals", 'NODES')
    mod.node_group = nodegroup

    mesh.update()

    return ""


