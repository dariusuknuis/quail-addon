# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from bpy.types import Object, Collection
from ..wce.wce import wce
from ..wce.polyhedrondefinition import polyhedrondefinition
from .context import Context

def decode_polyhedrondefinition(ctx:Context, volume:polyhedrondefinition) -> str:
    mesh = bpy.data.meshes.new(volume.tag)
    obj = bpy.data.objects.new(volume.tag, mesh)
    ctx.collection.objects.link(obj)
    obj['quaildef'] = 'polyhedrondefinition'

    obj.parent = ctx.parent

    # -------------------------
    # Vertices
    # -------------------------
    vertices = [
        mathutils.Vector(v.xyz)
        for v in volume.vertices
    ]

    # -------------------------
    # Faces (NGONS, untouched)
    # -------------------------
    faces = []
    for face in volume.faces:
        raw = [int(i) for i in face.vertexlist]

        count = raw[0]
        indices = raw[1:count + 1]

        faces.append(tuple(indices))

    # -------------------------
    # Build mesh
    # -------------------------
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    return ""