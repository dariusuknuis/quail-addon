# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportAttributeAccessIssue=false

import bpy
import mathutils
from .context import Context
from ..wce.actordef import actordef
from .hierarchicalspritedef import decode_hierarchicalspritedef
from .dmspritedef2 import decode_dmspritedef2

def decode_actordef(ctx: Context, actordef: actordef) -> str:
    obj = bpy.data.objects.new(actordef.tag, None)
    obj.empty_display_type = 'SINGLE_ARROW'
    obj['quaildef'] = 'actordef'

    props = obj.quail_actordef

    # -------------------------
    # Current Action
    # -------------------------
    ca = actordef.currentaction[0] if isinstance(actordef.currentaction, tuple) else actordef.currentaction
    if ca is None:
        props.has_currentaction = False
        props.currentaction = 0
    else:
        props.has_currentaction = True
        props.currentaction = int(ca)

    # -------------------------
    props.boundsref = actordef.boundsref
    props.callback = actordef.callback

    # -------------------------
    # Active Geometry (flag)
    # -------------------------
    ag = actordef.activegeometry[0] if isinstance(actordef.activegeometry, tuple) else actordef.activegeometry
    props.activegeometry = ag is not None

    # -------------------------
    props.collider = actordef.spritevolumeonly == 1
    props.userdata = actordef.userdata

    # -------------------------
    # Location (6 x (value, None))
    # -------------------------
    loc = actordef.location

    if loc and isinstance(loc, tuple):
        values = [v[0] if isinstance(v, tuple) else v for v in loc]

        if all(v is None for v in values):
            props.has_location = False
        else:
            props.has_location = True

            props.loc_x, props.loc_y, props.loc_z = values[:3]
            props.rot_x, props.rot_y, props.rot_z = values[3:]

            # Only assign if valid floats
            if all(v is not None for v in values[:3]):
                obj.location = mathutils.Vector(values[:3])
    else:
        props.has_location = False

    # -------------------------
    # Actions (FIXED)
    # -------------------------
    props.numactions = len(actordef.actions)

    # Clear existing
    while len(props.actions) > 0:
        props.actions.remove(0)

    for action in actordef.actions:
        act = props.actions.add()
        a = action.action

        # unk1 (may or may not exist depending on parser)
        act.unk1 = bool(getattr(a, "unk1", 0))

        act.numlods = len(a.levelsofdetails)

        # Clear LODs
        while len(act.lods) > 0:
            act.lods.remove(0)

        for lod in a.levelsofdetails:
            l = act.lods.add()
            ldef = lod.levelofdetail

            tag = ldef.sprite
            sprite_obj = bpy.data.objects.get(tag)

            if sprite_obj:
                l.sprite = sprite_obj

            l.mindistance = ldef.mindistance

    # -------------------------
    obj.parent = ctx.parent
    ctx.parent = obj
    ctx.collection.objects.link(obj)

    # -------------------------
    # Attach sprites (unchanged logic)
    # -------------------------
    for action in actordef.actions:
        a = action.action
        for lod in a.levelsofdetails:
            ldef = lod.levelofdetail

            tag = ldef.sprite
            sprite_obj = bpy.data.objects.get(tag)

            if sprite_obj:
                sprite_obj.parent = obj
                continue

            elif tag in ctx.parser.dmspritedefinitions:
                pass

            elif tag in ctx.parser.blitspritedefs:
                pass

            elif tag in ctx.parser.sprite2ddefs:
                pass

            elif tag in ctx.parser.sprite3ddefs:
                pass

            else:
                return f"actordef {actordef.tag} refers to sprite {tag} but not found"

    return ""


