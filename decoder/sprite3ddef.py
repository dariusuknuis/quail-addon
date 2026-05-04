import bpy
import mathutils
from bpy.types import Object, Collection
from ..wce.wce import wce
from ..wce.sprite3ddef import sprite3ddef
from .context import Context
from ..common.s3dobject import apply_bounding_radius_geo

def decode_sprite3ddef(ctx: Context, sprite: sprite3ddef) -> str:

    mesh = bpy.data.meshes.new(sprite.tag)
    obj = bpy.data.objects.new(sprite.tag, mesh)
    ctx.collection.objects.link(obj)

    obj['quaildef'] = 'sprite3ddef'
    obj.parent = ctx.parent

    # ------------------------------------------------
    # Vertices
    # ------------------------------------------------

    vertices = [
        mathutils.Vector(v.xyz)
        for v in sprite.vertices
    ]

    # ------------------------------------------------
    # Faces (from BSP nodes)
    # ------------------------------------------------

    faces = []

    for node in sprite.bspnodes:
        raw = [int(i) for i in node.bspnode.vertexlist]

        if not raw:
            continue

        count = raw[0]
        indices = raw[1:count + 1]

        # Skip invalid faces
        if len(indices) < 3:
            continue

        faces.append(tuple(indices))

    # ------------------------------------------------
    # Build mesh
    # ------------------------------------------------

    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    # ------------------------------------------------
    # Shading (Gouraud flag)
    # ------------------------------------------------

    if sprite.enablegouraud2:
        for poly in mesh.polygons:
            poly.use_smooth = True

    # ------------------------------------------------
    # Two-sided handling (per BSP node)
    # ------------------------------------------------

    # If any node is two-sided, mark whole mesh as such
    # (Blender doesn't support per-face double-sided cleanly)
    two_sided = any(
        node.bspnode.renderinfo.twosided
        for node in sprite.bspnodes
    )

    if two_sided:
        mesh.use_auto_smooth = False  # avoid weird shading issues
        if hasattr(obj, "show_double_sided"):
            obj.show_double_sided = True

    # ------------------------------------------------
    # Material (very basic for now)
    # ------------------------------------------------

    mat = bpy.data.materials.get(sprite.tag)

    if not mat:
        mat = bpy.data.materials.new(sprite.tag)

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)

    # ------------------------------------------------
    # Bounding radius geo node
    # ------------------------------------------------

    apply_bounding_radius_geo(
        parent_obj=obj,
        radius=sprite.boundingradius,
        enabled=False
    )

    return ""