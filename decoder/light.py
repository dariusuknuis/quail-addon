import bpy
from .context import Context
from ..wce.pointlight import pointlight
from ..wce.lightdefinition import lightdefinition


def decode_light(ctx: Context, point: pointlight) -> str:

    parser = ctx.parser

    print("\n=== DECODE LIGHT START ===")
    print("POINTLIGHT tag:", point.tag)
    print("POINTLIGHT light ref:", point.light)
    print("POINTLIGHT xyz:", point.xyz)

    # ----------------------------------------
    # Lookup LIGHTDEFINITION
    # ----------------------------------------
    print("Available LIGHTDEFINITION keys:", list(parser.lightdefinitions.keys()))

    ldef = parser.lightdefinitions.get(point.light)

    if not ldef:
        print(f"WARNING: Missing LIGHTDEFINITION '{point.light}'")
        print("=== DECODE LIGHT END (FAIL) ===\n")
        return ""

    print("Matched LIGHTDEFINITION:", ldef.tag)

    # ----------------------------------------
    # Create Blender light DATA
    # ----------------------------------------
    print("Creating light DATA:", ldef.tag)

    light_data = bpy.data.lights.new(ldef.tag, type='POINT')

    # Energy
    if ldef.frames:
        energy = float(ldef.frames[0].lightlevels) * 100.0
        light_data.energy = energy
        print("Energy set to:", energy)

    # Color
    if ldef.colors:
        c = ldef.colors[0].color
        light_data.color = (c[0], c[1], c[2])
        print("Color set to:", c)

    # Radius → exposure
    exposure = point.radiusofinfluence / 10
    light_data.exposure = exposure
    print("Exposure set to:", exposure)

    # ----------------------------------------
    # Create OBJECT
    # ----------------------------------------
    print("Creating OBJECT with name:", ldef.tag)

    obj = bpy.data.objects.new(ldef.tag, light_data)
    obj["quaildef"] = "light"

    # ----------------------------------------
    # Location
    # ----------------------------------------
    obj.location = point.xyz
    print("Location set to:", point.xyz)

    # ----------------------------------------
    # Store data
    # ----------------------------------------
    obj["light"] = point.light
    obj["radiusofinfluence"] = point.radiusofinfluence
    obj["static"] = point.static
    obj["staticinfluence"] = point.staticinfluence
    obj["dynamicinfluence"] = point.dynamicinfluence
    obj["regions"] = point.regions

    obj["ldef_tag"] = ldef.tag
    obj["sleep"] = ldef.sleep
    obj["haveskipframes"] = ldef.haveskipframes
    obj["skipframes"] = ldef.skipframes

    if ldef.frames:
        obj["lightlevel"] = float(ldef.frames[0].lightlevels)

    if ldef.colors:
        obj["color"] = ldef.colors[0].color

    # ----------------------------------------
    # Link
    # ----------------------------------------
    print("Linking object:", obj.name)

    obj.parent = ctx.parent
    ctx.collection.objects.link(obj)

    print("SUCCESS: Created", obj.name)
    print("=== DECODE LIGHT END ===\n")

    return ""