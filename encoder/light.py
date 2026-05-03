from ..wce.pointlight import pointlight
from ..wce.lightdefinition import lightdefinition


def encode_light(parser, obj) -> str:

    if obj.get("quaildef") != "light":
        return ""

    props = obj.quail_light

    index = len(parser.pointlights)

    # ----------------------------------------
    # Generate names
    # ----------------------------------------
    ldef_name = f"L{index}_LDEF"
    key = f"__pointlight_{index}"

    # ========================================
    # LIGHTDEFINITION
    # ========================================
    ldef = lightdefinition()
    ldef.tag = ldef_name

    ldef.currentframe = props.currentframe if props.has_currentframe else None
    ldef.sleep = props.sleep if props.has_sleep else None
    ldef.haveskipframes = int(props.haveskipframes)
    ldef.skipframes = int(props.skipframes)

    # --- frames ---
    ldef.frames = []
    frame = lightdefinition.lightlevels()
    frame.lightlevels = float(props.lightlevel)
    ldef.frames.append(frame)

    # --- colors ---
    ldef.colors = []
    color = lightdefinition.color()
    color.color = (
        float(props.color[0]),
        float(props.color[1]),
        float(props.color[2]),
    )
    ldef.colors.append(color)

    # store
    parser.lightdefinitions[ldef.tag] = ldef

    # ========================================
    # POINTLIGHT
    # ========================================
    pt = pointlight()

    pt.tag = ""  # matches your input files
    pt.light = ldef_name

    pt.static = int(props.static)
    pt.staticinfluence = int(props.staticinfluence)
    pt.dynamicinfluence = int(props.dynamicinfluence)

    # location
    loc = obj.location
    pt.xyz = (
        float(loc.x),
        float(loc.y),
        float(loc.z),
    )

    pt.radiusofinfluence = float(props.radiusofinfluence)

    # regions
    if props.has_regions and props.regions:
        pt.regions = props.regions.split()
    else:
        pt.regions = None

    # store
    parser.pointlights[key] = pt

    return ""