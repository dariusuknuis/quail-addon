import bpy
from .context import Context
from ..wce.actordef import actordef
from ..common.s3dobject import collect_sprite_graph

def decode_actordef(ctx: Context, actordef: actordef) -> str:

    # ------------------------------------------------
    # Create collection (instead of object)
    # ------------------------------------------------
    col = bpy.data.collections.new(actordef.tag)
    col["quaildef"] = "actordef"

    ctx.collection.children.link(col)

    props = col.quail_actordef

    # ------------------------------------------------
    # Current Action
    # ------------------------------------------------
    ca = actordef.currentaction[0] if isinstance(actordef.currentaction, tuple) else actordef.currentaction

    if ca is None:
        props.has_currentaction = False
        props.currentaction = 0
    else:
        props.has_currentaction = True
        props.currentaction = int(ca)

    # ------------------------------------------------
    props.boundsref = actordef.boundsref
    props.callback = actordef.callback

    # ------------------------------------------------
    # Active Geometry
    # ------------------------------------------------
    ag = actordef.activegeometry[0] if isinstance(actordef.activegeometry, tuple) else actordef.activegeometry
    props.activegeometry = ag is not None

    # ------------------------------------------------
    props.collider = actordef.spritevolumeonly == 1
    props.userdata = actordef.userdata

    # ------------------------------------------------
    # Location (store only, no transform)
    # ------------------------------------------------
    loc = actordef.location

    if loc and isinstance(loc, tuple):
        values = [v[0] if isinstance(v, tuple) else v for v in loc]

        if all(v is None for v in values):
            props.has_location = False
        else:
            props.has_location = True
            props.loc_x, props.loc_y, props.loc_z = values[:3]
            props.rot_x, props.rot_y, props.rot_z = values[3:]
    else:
        props.has_location = False

    # ------------------------------------------------
    # Actions
    # ------------------------------------------------
    props.numactions = len(actordef.actions)

    while len(props.actions) > 0:
        props.actions.remove(0)

    for action in actordef.actions:
        act = props.actions.add()
        a = action.action

        act.unk1 = bool(getattr(a, "unk1", 0))
        act.numlods = len(a.levelsofdetails)

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

    # ------------------------------------------------
    # Attach sprites → move full dependency graph
    # ------------------------------------------------
    for action in actordef.actions:
        a = action.action

        for lod in a.levelsofdetails:
            ldef = lod.levelofdetail
            tag = ldef.sprite

            sprite_obj = bpy.data.objects.get(tag)

            if sprite_obj:

                # ----------------------------------------
                # Collect full graph (sprite + children + constrained objects)
                # ----------------------------------------
                objs = collect_sprite_graph(sprite_obj)

                for obj in objs:

                    # ----------------------------------------
                    # Remove from NON-ACTORDEF collections
                    # ----------------------------------------
                    for c in list(obj.users_collection):
                        if c.get("quaildef") != "actordef":
                            c.objects.unlink(obj)

                    # ----------------------------------------
                    # Ensure it's linked to THIS ACTORDEF
                    # ----------------------------------------
                    if col not in obj.users_collection:
                        col.objects.link(obj)

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