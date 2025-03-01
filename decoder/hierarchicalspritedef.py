# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
from bpy.types import Collection
from ..wce.wce import wce
from ..wce.hierarchicalspritedef import hierarchicalspritedef
from .dmsprite2def import decode_dmspritedef2

def decode_hierarchicalspritedef(parser:wce, collection:Collection, sprite:hierarchicalspritedef) -> str:
    empty = bpy.data.objects.new(sprite.tag, None)
    collection.objects.link(empty)

    for skin in sprite.attachedskins:
        dmspritedef2 = parser.dmspritedef2s[skin.dmsprite]
        if not dmspritedef2:
            return f"hsprite {sprite.tag} refers to dmsprite {skin.dmsprite} but not found"
        err = decode_dmspritedef2(parser, collection, empty, dmspritedef2)
        if err:
            return f"hsprite {sprite.tag}: {err}"

        #empty.data = bpy.data.meshes.new(hsprite.tag)
        #empty.data.from_pydata(sprite.vertices, [], skin.faces)
        #empty.data.update()

    return ""
