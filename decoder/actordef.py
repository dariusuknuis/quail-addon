# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportAttributeAccessIssue=false

import bpy
import mathutils
from .context import Context
from ..wce.actordef import actordef
from .hierarchicalspritedef import decode_hierarchicalspritedef

def decode_actordef(ctx:Context, actordef:actordef) -> str:
    obj = bpy.data.objects.new(actordef.tag, None)
    obj.empty_display_type = 'SINGLE_ARROW'
    obj['quaildef'] = 'actordef'
    obj.quail_actordef.currentaction = actordef.currentaction or ""
    obj.quail_actordef.boundsref = actordef.boundsref
    obj.quail_actordef.callback = actordef.callback
    obj.quail_actordef.activegeometry = actordef.activegeometry or ""
    obj.quail_actordef.collider = actordef.usemodelcollider == 1
    obj.quail_actordef.userdata = actordef.userdata
    if actordef.location[0]:
        obj.location = mathutils.Vector(actordef.location[0:3])
    obj.parent = ctx.parent
    ctx.parent = obj
    ctx.collection.objects.link(obj)


    for action in actordef.actions:
        for lod in action.levelofdetails:
            hsprite = ctx.parser.hierarchicalspritedefs[lod.sprite]
            if not hsprite:
                return f"actordef {actordef.tag} refers to hsprite {lod.sprite} but not found"
            err = decode_hierarchicalspritedef(ctx, hsprite)
            if err:
                return f"actordef {actordef.tag}: {err}"
    return ""


