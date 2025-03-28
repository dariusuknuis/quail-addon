import bpy
import os

from .node import node_generate
from .context import Context
from ..wce.materialdefinition import materialdefinition
from ..wce.simplespritedef import simplespritedef

def create_material(ctx:Context, src_material:materialdefinition) -> str:
    #if src_material.tag in bpy.data.materials:
    #    return ""
    base_path = ctx.parser.path
    src_sprite = ctx.parser.simplespritedefs[src_material.simplespritetag]
    if src_sprite is None:
        return f"simplesprite {src_material.simplespritetag} not found"
    if len(src_sprite.frames) == 0:
        return f"simplesprite {src_material.simplespritetag} has no frames"
    if len(src_sprite.frames) > 1:
        return f"simplesprite {src_material.simplespritetag} has multiple frames, only 1 supported for now"
    frame = src_sprite.frames[0]
    if len(frame.files) == 0:
        return f"simplesprite {src_material.simplespritetag} has no files"
    if len(frame.files) > 1:
        return f"simplesprite {src_material.simplespritetag} has multiple files, only 1 supported for now"
    src_file_name = frame.files[0].file
    texture_path = os.path.join(base_path, "assets", src_file_name)
    if not os.path.exists(texture_path):
        # fallback to iterating path for case insensitive
        is_found = False
        for file in os.listdir(os.path.join(base_path, "assets")):
            if file.lower() == src_file_name.lower():
                texture_path = os.path.join(base_path, "assets", file)
                is_found = True
                break
        if not is_found:
            return f"texture {texture_path} not found"

    err = node_generate(src_material, texture_path, src_material.rendermethod)
    if err != "":
        return f"apply material {src_material.tag}: {err}"
    return ""