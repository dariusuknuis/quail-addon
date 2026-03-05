# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportAttributeAccessIssue=false

import bpy
import mathutils
from .context import Context
from ..wce.actordef import actordef
from .hierarchicalspritedef import decode_hierarchicalspritedef
from .dmspritedef2 import decode_dmspritedef2

def decode_actordef(ctx:Context, actordef:actordef) -> str:
    obj = bpy.data.objects.new(actordef.tag, None)
    obj.empty_display_type = 'SINGLE_ARROW'
    obj['quaildef'] = 'actordef'
    obj.quail_actordef.currentaction = actordef.currentaction or ""
    obj.quail_actordef.boundsref = actordef.boundsref
    obj.quail_actordef.callback = actordef.callback
    obj.quail_actordef.activegeometry = actordef.activegeometry or ""
    obj.quail_actordef.spritevolumeonly = actordef.spritevolumeonly == 1
    obj.quail_actordef.userdata = actordef.userdata
    if actordef.location[0]:
        obj.location = mathutils.Vector(actordef.location[0:3])
    obj.parent = ctx.parent
    ctx.parent = obj
    ctx.collection.objects.link(obj)


    for action in actordef.actions:
        for lod in action.levelsofdetails:

            tag = lod.sprite

            sprite_obj = bpy.data.objects.get(tag)

            if sprite_obj:
                sprite_obj.parent = obj
                continue

            if tag in ctx.parser.hierarchicalspritedefs:
                hsprite = ctx.parser.hierarchicalspritedefs[tag]
                err = decode_hierarchicalspritedef(ctx, hsprite)
                if err:
                    return f"actordef {actordef.tag}: {err}"

            # elif tag in ctx.parser.dmspritedef2s:
            #     sprite = ctx.parser.dmspritedef2s[tag]
            #     err = decode_dmspritedef2(ctx, sprite)
            #     if err:
            #         return f"actordef {actordef.tag}: {err}"

            elif tag in ctx.parser.dmspritedefinitions:
                # TODO: implement decode_dmspritedef later
                pass

            elif tag in ctx.parser.blitspritedefs:
                # TODO
                pass

            elif tag in ctx.parser.sprite2ddefs:
                # TODO
                pass

            elif tag in ctx.parser.sprite3ddefs:
                # TODO
                pass

            else:
                return f"actordef {actordef.tag} refers to sprite {tag} but not found"

    return ""


