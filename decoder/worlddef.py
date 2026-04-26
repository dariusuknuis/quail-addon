import bpy
from .context import Context
from ..wce.worlddef import worlddef

def decode_worlddef(ctx: Context, wd: worlddef) -> str:

    col = ctx.collection

    # Tag collection
    col["quaildef"] = "worlddef"

    props = col.quail_worlddef

    # ----------------------------------------
    # Direct mappings
    # ----------------------------------------
    props.newworld = bool(wd.newworld)
    props.zone = bool(wd.zone)

    # ----------------------------------------
    # Optional EQG
    # ----------------------------------------
    if wd.eqgversion is None:
        props.use_eqg = False
        props.eqgversion = 0
    else:
        props.use_eqg = True
        props.eqgversion = wd.eqgversion

    return ""