import bpy
from ..wce.globalambientlightdef import globalambientlightdef

def encode_globalambientlightdef(parser) -> str:

    world = bpy.context.scene.world

    # ----------------------------------------
    # Validate
    # ----------------------------------------
    if not world or world.get("quaildef") != "globalambientlightdef":
        return ""

    # ----------------------------------------
    # Create WCE object
    # ----------------------------------------
    wce = globalambientlightdef()

    # ----------------------------------------
    # Get Background node
    # ----------------------------------------
    color = (0, 0, 0, 255)

    if world.use_nodes and world.node_tree:
        for n in world.node_tree.nodes:
            if n.type == 'BACKGROUND':
                col = n.inputs["Color"].default_value

                # Blender → WCE
                color = (
                    int(col[0] * 255),
                    int(col[1] * 255),
                    int(col[2] * 255),
                    int(col[3] * 255)
                )

                break

    # ----------------------------------------
    # Assign color (RGBA)
    # ----------------------------------------
    wce.color = (
        color[0],
        color[1],
        color[2],
        color[3]
    )

    # ----------------------------------------
    # Store on parser (single, like worlddef)
    # ----------------------------------------
    parser.globalambientlightdef = wce

    return ""