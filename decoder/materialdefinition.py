# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportAttributeAccessIssue=false

import bpy
from ..wce.materialdefinition import materialdefinition
from .context import Context
from ..common.rendermethod import apply_userdefined, apply_transparent, parse_rendermethod_string, create_rendermethod_nodegroup

def decode_materialdefinition(ctx:Context, material:materialdefinition) -> str:
    if material.tag in bpy.data.materials:
        return ""
    mat = bpy.data.materials.new(material.tag)
    mat['quaildef'] = 'materialdefinition'

    # --------------------------------------------------
    # Parse RenderMethod
    # --------------------------------------------------
    parsed = parse_rendermethod_string(material.rendermethod)

    props = mat.quail_materialdefinition

    if parsed["use_userdefined"]:
        props.use_userdefined = True
        props.userdefined_index = parsed["userdefined_index"]

        apply_userdefined(props, props.userdefined_index)

    elif parsed.get("transparent"):
        props.use_userdefined = False
        props.transparent_override = True

        apply_transparent(props)

    else:
        props.use_userdefined = False

        props.drawstyle = parsed["drawstyle"]
        props.lighting = parsed["lighting"]
        props.shading = parsed["shading"]
        props.texture_index = parsed["texture_index"]

        props.masked = parsed["masked"]
        props.alphablend = parsed["alphablend"]
        props.opacity = parsed["opacity"]
        props.additive = parsed["additive"]
        props.dynamic = parsed["dynamic"]
        props.prelit = parsed["prelit"]

    props.rgbpen = (
        material.rgbpen[0] / 255.0,
        material.rgbpen[1] / 255.0,
        material.rgbpen[2] / 255.0,
    )
    props.brightness = material.brightness
    props.scaledambient = material.scaledambient
    tag = material.simplespriteinst.simplespritetag
    if tag:
        props.simplespritetag = tag
    props.simplespritehaveskipframes = material.simplespriteinst.simplespritehaveskipframes == 1
    props.simplespriteskipframes = material.simplespriteinst.simplespriteskipframes == 1
    if material.uvshiftperms is not None:
        props.has_uvshiftperms = True
        props.uvshiftperms = material.uvshiftperms
    else:
        props.has_uvshiftperms = False
        props.uvshiftperms = (0.0, 0.0)
    props.twosided = material.twosided == 1

    mat.use_nodes = True

    if mat.node_tree is None:
        return f"material {material.tag} has no node tree"

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Clear default nodes
    for n in nodes:
        nodes.remove(n)

    # Create RenderMethod group
    group_tree = create_rendermethod_nodegroup()

    group_node = nodes.new("ShaderNodeGroup")
    group_node.node_tree = group_tree
    group_node.location = (0, 0)

    # Hide internal control inputs (panel-controlled only)
    hide_inputs = {
        "PassableDisplay",
        "Masked",
        "AlphaBlend",
        "Additive",
        "Opacity",
        "Drawstyle",
        "TextureIndex",
        "Transparent Blit",
    }

    for socket in group_node.inputs:
        if socket.name in hide_inputs:
            socket.hide = True

    # Apply values to group inputs
    group_node.inputs["sRGB Texture"].default_value = (1.0, 1.0, 1.0, 1.0)
    group_node.inputs["Masked"].default_value = float(props.masked)
    group_node.inputs["AlphaBlend"].default_value = float(props.alphablend)
    group_node.inputs["Opacity"].default_value = props.opacity
    group_node.inputs["Additive"].default_value = float(props.additive)
    group_node.inputs["TextureIndex"].default_value = float(props.texture_index)
    group_node.inputs["Transparent Blit"].default_value = 1.0
    drawstyle_map = {
        "DRAW0": 0.0,
        "DRAW1": 1.0,
        "WIREFRAME": 2.0,
        "SOLIDFILL": 3.0,
    }

    group_node.inputs["Drawstyle"].default_value = drawstyle_map.get(
        props.drawstyle, 0.0
    )

    socket = group_node.inputs["PassableDisplay"]
    fcu = socket.driver_add("default_value")
    drv = fcu.driver
    drv.type = 'SCRIPTED'

    var = drv.variables.new()
    var.name = "s"
    tgt = var.targets[0]
    tgt.id_type = 'SCENE'
    tgt.id = bpy.context.scene
    tgt.data_path = 'passable_display_enabled'

    drv.expression = "s"

    # Add Material Output
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (300, 0)

    links.new(group_node.outputs["Shader"], output.inputs["Surface"])

    # Backface culling
    mat.use_backface_culling = not props.twosided

    if props.simplespritetag:
        sprite_group = bpy.data.node_groups.get(props.simplespritetag)
        if sprite_group:
            sprite_node = nodes.new("ShaderNodeGroup")
            sprite_node.node_tree = sprite_group
            sprite_node.location = (-400, 0)

            links.new(sprite_node.outputs["sRGB Texture"], group_node.inputs["sRGB Texture"])
            links.new(sprite_node.outputs["Alpha"], group_node.inputs["Alpha"])

    return ""
