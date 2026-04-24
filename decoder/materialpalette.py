import bpy
from .context import Context
from ..wce.materialpalette import materialpalette

def decode_materialpalette(ctx: Context, mat_palette: materialpalette) -> str:

    # ------------------------------------------------
    # Try reuse existing object
    # ------------------------------------------------
    palette_obj = bpy.data.objects.get(mat_palette.tag)

    if palette_obj and palette_obj.get("quaildef") == "materialpalette":
        return ""

    # ------------------------------------------------
    # Create new palette object
    # ------------------------------------------------
    palette_obj = bpy.data.objects.new(mat_palette.tag, None)
    ctx.collection.objects.link(palette_obj)
    palette_obj["quaildef"] = "materialpalette"

    props = palette_obj.quail_materialpalette
    props.tag = mat_palette.tag

    # ------------------------------------------------
    # Populate materials (only on first creation)
    # ------------------------------------------------
    for m in mat_palette.materials:

        mat = bpy.data.materials.get(m.material)

        if mat is None:
            mat = bpy.data.materials.new(m.material)

        item = props.materials.add()
        item.material = mat

    palette_obj.hide_viewport = True
    palette_obj.hide_select = True
    palette_obj.hide_render = True

    return ""