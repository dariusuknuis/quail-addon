# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
from ..wce.wce import wce
from ..wce.actordef import actordef
from .hierarchicalspritedef import decode_hierarchicalspritedef

def decode_actordef(parser:wce, actordef:actordef) -> str:
    collection = bpy.data.collections.new(actordef.tag)
    bpy.context.scene.collection.children.link(collection)
    for action in actordef.actions:
        for lod in action.levelofdetails:
            hsprite = parser.hierarchicalspritedefs[lod.sprite]
            if not hsprite:
                return f"actordef {actordef.tag} refers to hsprite {lod.sprite} but not found"
            err = decode_hierarchicalspritedef(parser, collection, hsprite)
            if err:
                return f"actordef {actordef.tag}: {err}"
    return ""


