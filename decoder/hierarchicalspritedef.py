# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
from bpy.types import Collection
from ..wce.wce import wce
from ..wce.hierarchicalspritedef import hierarchicalspritedef
from .dmspritedef2 import decode_dmspritedef2
from .context import Context

def decode_hierarchicalspritedef(ctx:Context, sprite:hierarchicalspritedef) -> str:
    object = bpy.data.objects.new(sprite.tag, None)
    object.parent = ctx.parent

    for skin in sprite.attachedskins:
        dmspritedef2 = ctx.parser.dmspritedef2s[skin.dmsprite]
        if not dmspritedef2:
            return f"hsprite {sprite.tag} refers to dmsprite {skin.dmsprite} but not found"
        err = decode_dmspritedef2(ctx, dmspritedef2)
        if err:
            return f"hsprite {sprite.tag}: {err}"

        #empty.data = bpy.data.meshes.new(hsprite.tag)
        #empty.data.from_pydata(sprite.vertices, [], skin.faces)
        #empty.data.update()

    return ""
