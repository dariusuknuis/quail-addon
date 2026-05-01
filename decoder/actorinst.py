import bpy, math
from .context import Context
from ..wce.actorinst import actorinst


def decode_actorinst(ctx: Context, inst: actorinst) -> str:

    # ------------------------------------------------
    # Build tag FROM sprite
    # ------------------------------------------------
    sprite_tag = inst.sprite or "ACTOR"

    if sprite_tag.endswith("ACTORDEF"):
        inst.tag = sprite_tag.replace("ACTORDEF", "ACTORINST")
    else:
        inst.tag = f"{sprite_tag}_ACTORINST"

    name = inst.tag  # Blender object name = tag

    # ------------------------------------------------
    # Create object
    # ------------------------------------------------
    obj = bpy.data.objects.new(name, None)
    obj["quaildef"] = "actorinst"

    ctx.collection.objects.link(obj)

    props = obj.quail_actorinst

    # ------------------------------------------------
    # COLLECTION INSTANCE
    # ------------------------------------------------
    obj.instance_type = 'COLLECTION'

    sprite_col = bpy.data.collections.get(sprite_tag)
    if not sprite_col:
        return f"actorinst refers to collection {sprite_tag} but not found"

    obj.instance_collection = sprite_col

    props.sprite = sprite_col

    # ------------------------------------------------
    # Current Action
    # ------------------------------------------------
    if inst.currentaction is None:
        props.has_currentaction = False
        props.currentaction = ""
    else:
        props.has_currentaction = True
        props.currentaction = str(inst.currentaction)

    # ------------------------------------------------
    # Location
    # ------------------------------------------------
    if inst.location:
        props.has_location = True

        x, y, z, rz, ry, rx = inst.location

        props.loc_x = x
        props.loc_y = y
        props.loc_z = z
        props.rot_x = rz
        props.rot_y = ry
        props.rot_z = rx

        # ADD THIS
        obj.location = (x, y, z)

        scale = (2 * math.pi) / 512.0
        obj.rotation_euler = (
            ry * scale,  # X
            rx * scale,  # Y
            rz * scale,  # Z
        )

    # ------------------------------------------------
    # Optional fields
    # ------------------------------------------------
    props.has_boundingradius = inst.boundingradius is not None
    if inst.boundingradius is not None:
        props.boundingradius = inst.boundingradius

    props.has_scalefactor = inst.scalefactor is not None
    if inst.scalefactor is not None:
        props.scalefactor = inst.scalefactor

        # ADD THIS
        obj.scale = (inst.scalefactor,) * 3

    props.sound = inst.sound or ""

    props.has_active = inst.active is not None
    if inst.active is not None:
        props.active = inst.active

    # ------------------------------------------------
    # Required
    # ------------------------------------------------
    props.spritevolumeonly = bool(inst.spritevolumeonly)

    props.dmrgbtrack = inst.dmrgbtrack or ""

    props.sphere = inst.sphere
    props.sphereradius = inst.sphereradius

    props.useboundingbox = bool(inst.useboundingbox)

    props.userdata = inst.userdata or ""

    return ""