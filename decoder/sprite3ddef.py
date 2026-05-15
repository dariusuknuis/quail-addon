import bpy
import mathutils
from bpy.types import Object, Collection
from ..wce.sprite3ddef import sprite3ddef
from .context import Context
from ..common.s3dobject import apply_bounding_radius_geo
from ..common.renderinfo import build_renderinfo_material

def decode_sprite3ddef(ctx: Context, sprite: sprite3ddef) -> str:

    mesh = bpy.data.meshes.new(sprite.tag)
    obj = bpy.data.objects.new(sprite.tag, mesh)
    ctx.collection.objects.link(obj)

    obj['quaildef'] = 'sprite3ddef'
    obj.parent = ctx.parent

    props = obj.quail_sprite3ddef

    # ------------------------------------------------
    # Vertices
    # ------------------------------------------------

    vertices = [
        mathutils.Vector(v.xyz)
        for v in sprite.vertices
    ]

    # ------------------------------------------------
    # Faces
    # ------------------------------------------------

    faces = []
    face_material_indices = []

    for node_index, node in enumerate(sprite.bspnodes):

        raw = [int(i) for i in node.bspnode.vertexlist]

        if not raw:
            continue

        count = raw[0]
        indices = raw[1:count + 1]

        if len(indices) < 3:
            continue

        faces.append(tuple(indices))
        face_material_indices.append(node_index)

    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    # ------------------------------------------------
    # Materials (using new function)
    # ------------------------------------------------

    materials = []

    for i, node in enumerate(sprite.bspnodes):
        mat = build_renderinfo_material(sprite.tag, i, node)
        materials.append(mat)
        obj.data.materials.append(mat)

    for poly_index, poly in enumerate(mesh.polygons):
        if poly_index < len(face_material_indices):
            poly.material_index = face_material_indices[poly_index]

    # ------------------------------------------------
    # Gouraud flag
    # ------------------------------------------------

    props.enablegouraud2 = bool(sprite.enablegouraud2)

    # ------------------------------------------------
    # Center Offset
    # ------------------------------------------------

    if sprite.centeroffset is not None:
        props.hascenteroffset = True
        obj.location = sprite.centeroffset
        obj.lock_location = (False, False, False)
    else:
        props.hascenteroffset = False
        obj.location = (0.0, 0.0, 0.0)
        obj.lock_location = (True, True, True)

    # ------------------------------------------------
    # Bounding radius
    # ------------------------------------------------

    if sprite.boundingradius is not None:
        props.hasboundingradius = True
        props.boundingradius = sprite.boundingradius
    else:
        props.hasboundingradius = False
        props.boundingradius = 1.0

    apply_bounding_radius_geo(
        parent_obj=obj,
        radius=sprite.boundingradius,
        enabled=False
    )

    return ""