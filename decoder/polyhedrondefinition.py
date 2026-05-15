# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from bpy.types import Object, Collection
from ..wce.wce import wce
from ..wce.polyhedrondefinition import polyhedrondefinition
from .context import Context
from ..common.s3dobject import apply_bounding_radius_geo, get_collision_volume_material

def decode_polyhedrondefinition(ctx:Context, volume:polyhedrondefinition) -> str:
    mesh = bpy.data.meshes.new(volume.tag)
    obj = bpy.data.objects.new(volume.tag, mesh)
    ctx.collection.objects.link(obj)
    obj['quaildef'] = 'polyhedrondefinition'

    obj.parent = ctx.parent

    # ------------------------------------------------
    # Populate properties for panel
    # ------------------------------------------------

    props = obj.quail_polyhedrondefinition

    props.boundingradius = volume.boundingradius

    if volume.scalefactor is not None:
        props.has_scalefactor = True
        props.scalefactor = volume.scalefactor
    else:
        props.has_scalefactor = False
        props.scalefactor = 1.0

    # ------------------------------------------------
    # Build Volume
    # ------------------------------------------------

    # Vertices
    vertices = [
        mathutils.Vector(v.xyz)
        for v in volume.vertices
    ]

    # Faces
    faces = []
    for face in volume.faces:
        raw = [int(i) for i in face.vertexlist]

        count = raw[0]
        indices = raw[1:count + 1]

        faces.append(tuple(indices))

    # Build mesh
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    mat = get_collision_volume_material()

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    # Apply scale factor
    scale = volume.scalefactor if volume.scalefactor is not None else 1.0
    obj.scale = (scale, scale, scale)

    # ------------------------------------------------
    # Add bouding radius geo node
    # ------------------------------------------------

    apply_bounding_radius_geo(parent_obj=obj, radius=volume.boundingradius, enabled=False)


    return ""