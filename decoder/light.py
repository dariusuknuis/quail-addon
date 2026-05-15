import bpy
from .context import Context
from ..wce.pointlight import pointlight
from ..wce.lightdefinition import lightdefinition


def decode_light(ctx: Context, point: pointlight) -> str:

    parser = ctx.parser

    # ----------------------------------------
    # Lookup LIGHTDEFINITION
    # ----------------------------------------

    ldef = parser.lightdefinitions.get(point.light)

    if not ldef:
        return ""

    # ----------------------------------------
    # Create Blender light DATA
    # ----------------------------------------

    light_data = bpy.data.lights.new(ldef.tag, type='POINT')

    # Energy
    if ldef.frames:
        energy = float(ldef.frames[0].lightlevels) * 100.0
        light_data.energy = energy

    # Color
    if ldef.colors:
        c = ldef.colors[0].color
        light_data.color = (c[0], c[1], c[2])

    # Radius → exposure
    exposure = 18.0
    light_data.exposure = exposure

    light_data.shadow_soft_size = point.radiusofinfluence

    # ----------------------------------------
    # Create OBJECT
    # ----------------------------------------

    obj = bpy.data.objects.new(ldef.tag, light_data)
    obj["quaildef"] = "light"

    props = obj.quail_light

    # ----------------------------------------
    # Location
    # ----------------------------------------
    obj.location = point.xyz

    # ----------------------------------------
    # Store data
    # ----------------------------------------
    if ldef.currentframe is not None:
        props.has_currentframe = True
        props.currentframe = ldef.currentframe
    else:
        props.has_currentframe = False

    props.numframes = len(ldef.frames)
    props.lightlevel = float(ldef.frames[0].lightlevels)
    props.light = point.light
    props.radiusofinfluence = point.radiusofinfluence
    props.static = bool(point.static)
    props.staticinfluence = bool(point.staticinfluence)
    props.dynamicinfluence = bool(point.dynamicinfluence)

    if point.regions and point.regions != ["NULL"]:
        props.has_regions = True
        props.regions = " ".join(point.regions)
    else:
        props.has_regions = False
        props.regions = ""

    if ldef.sleep is not None:
        props.has_sleep = True
        props.sleep = ldef.sleep
    else:
        props.has_sleep = False

    props.haveskipframes = bool(ldef.haveskipframes)
    props.skipframes = bool(ldef.skipframes)

    if ldef.frames:
        props.lightlevel = float(ldef.frames[0].lightlevels)

    if ldef.colors:
        c = ldef.colors[0].color
        props.color = c
        props.color_r = c[0]
        props.color_g = c[1]
        props.color_b = c[2]

    # ----------------------------------------
    # Link
    # ----------------------------------------

    obj.parent = ctx.parent
    ctx.collection.objects.link(obj)

    return ""