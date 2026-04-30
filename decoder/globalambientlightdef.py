import bpy
from .context import Context
from ..wce.globalambientlightdef import globalambientlightdef

def decode_globalambientlightdef(ctx: Context, gald: globalambientlightdef) -> str:

    # ------------------------------------------------
    # Ensure World exists
    # ------------------------------------------------
    world = bpy.context.scene.world

    if world is None:
        world = bpy.data.worlds.new("World")
        bpy.context.scene.world = world

    world["quaildef"] = "globalambientlightdef"

    world.use_nodes = True
    nt = world.node_tree

    # ------------------------------------------------
    # Get Background node
    # ------------------------------------------------
    bg = None
    for n in nt.nodes:
        if n.type == 'BACKGROUND':
            bg = n
            break

    if bg is None:
        bg = nt.nodes.new(type="ShaderNodeBackground")

    # ------------------------------------------------
    # Apply color (RGB only)
    # ------------------------------------------------
    r, g, b, a = gald.color

    bg.inputs["Color"].default_value = (
        r / 255.0,
        g / 255.0,
        b / 255.0,
        a / 255.0
    )

    return ""