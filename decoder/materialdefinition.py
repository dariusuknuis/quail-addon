# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportAttributeAccessIssue=false

import bpy
from ..wce.wce import wce
from ..wce.materialdefinition import materialdefinition
from .context import Context
from ..common.rendermethod import apply_userdefined

def create_rendermethod_nodegroup():

    name = "RENDERMETHOD"

    # -----------------------------------------
    # Reuse if already exists
    # -----------------------------------------
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]

    group = bpy.data.node_groups.new(name, 'ShaderNodeTree')
    nodes = group.nodes
    links = group.links

    # -----------------------------------------
    # Group Input / Output
    # -----------------------------------------
    group_input = nodes.new("NodeGroupInput")
    group_input.location = (-1255, 135)

    group_output = nodes.new("NodeGroupOutput")
    group_output.location = (1428, 12)

    def add_input(name, socket_type):
        group.interface.new_socket(
            name=name,
            in_out='INPUT',
            socket_type=socket_type
        )

    def add_output(name, socket_type):
        group.interface.new_socket(
            name=name,
            in_out='OUTPUT',
            socket_type=socket_type
        )

    # -----------------------------------------
    # Core Inputs
    # -----------------------------------------
    add_input("sRGB Texture", "NodeSocketColor")
    add_input("Alpha", "NodeSocketFloat")

    add_input("Masked", "NodeSocketFloat")
    add_input("AlphaBlend", "NodeSocketFloat")
    add_input("Opacity", "NodeSocketFloat")
    add_input("Additive", "NodeSocketFloat")

    # Stored flags (future use)
    add_input("Drawstyle", "NodeSocketFloat")
    # add_input("Lighting", "NodeSocketFloat")
    # add_input("Shading", "NodeSocketFloat")
    add_input("TextureIndex", "NodeSocketFloat")
    # add_input("Dynamic", "NodeSocketFloat")
    # add_input("Prelit", "NodeSocketFloat")

    add_output("Shader", "NodeSocketShader")

    inp = group_input.outputs
    out = group_output.inputs

    # -----------------------------------------
    # Base Principled Shader
    # -----------------------------------------
    principled = nodes.new("ShaderNodeBsdfPrincipled")
    principled.location = (1108, 15)
    principled.inputs["Metallic"].default_value = 0.0
    principled.inputs["Specular IOR Level"].default_value = 0.0
    principled.inputs["Roughness"].default_value = 1.0
    principled.inputs["Anisotropic"].default_value = 0.0
    principled.inputs["Transmission Weight"].default_value = 0.0
    principled.inputs["Sheen Weight"].default_value = 0.0

    # ------------------------------------------------
    # NotAlphaBlend = 1 - AlphaBlend
    # ------------------------------------------------
    not_alpha = nodes.new("ShaderNodeMath")
    not_alpha.name = 'Not Alpha Blend'
    not_alpha.label = 'NotAlphaBlend'
    not_alpha.operation = 'SUBTRACT'
    not_alpha.location = (-181, 89)
    not_alpha.inputs[0].default_value = 1.0
    links.new(inp["AlphaBlend"], not_alpha.inputs[1])

    # ------------------------------------------------
    # BlendAlpha = Opacity/100
    # ------------------------------------------------
    blend_alpha = nodes.new("ShaderNodeMath")
    blend_alpha.name = 'Blend Alpha'
    blend_alpha.label = 'BlendAlpha'
    blend_alpha.operation = 'DIVIDE'
    blend_alpha.location = (-460, -58)
    blend_alpha.inputs[1].default_value = 100.0
    links.new(inp["Opacity"], blend_alpha.inputs[0])

    # ------------------------------------------------
    # MaskEnable = Masked * NotAlphaBlend
    # ------------------------------------------------
    mask_enable = nodes.new("ShaderNodeMath")
    mask_enable.name = 'Mask Enable'
    mask_enable.label = 'MaskEnable'
    mask_enable.operation = 'MULTIPLY'
    mask_enable.location = (-1, 422)
    links.new(inp["Masked"], mask_enable.inputs[0])
    links.new(not_alpha.outputs[0], mask_enable.inputs[1])

    # ------------------------------------------------
    # MaskAllowed = max(Additive, MaskEnable)
    # ------------------------------------------------
    mask_allow = nodes.new("ShaderNodeMath")
    mask_allow.name = 'Mask Allowed'
    mask_allow.label = 'MaskAllowed'
    mask_allow.operation = 'MAXIMUM'
    mask_allow.location = (215, 356)
    links.new(inp["Additive"], mask_allow.inputs[1])
    links.new(mask_enable.outputs[0], mask_allow.inputs[0])

    # ------------------------------------------------
    # MaskAlpha = mix(AlphaGate, MaskAllowed)
    # ------------------------------------------------
    mask_mix = nodes.new("ShaderNodeMix")
    mask_mix.name = 'Mask Alpha'
    mask_mix.label = 'MaskAlpha'
    mask_mix.data_type = 'FLOAT'
    mask_mix.location = (444, 332)
    mask_mix.inputs[2].default_value = 1
    links.new(mask_allow.outputs[0], mask_mix.inputs["Factor"])
    links.new(inp["Alpha"], mask_mix.inputs[3])

    # ------------------------------------------------
    # BlendEffective = mix(AlphaBlend, BlendAlpha)
    # ------------------------------------------------
    blend_effect = nodes.new("ShaderNodeMix")
    blend_effect.name = 'Blend Effective'
    blend_effect.label = 'BlendEffective'
    blend_effect.data_type = 'FLOAT'
    blend_effect.location = (419, 10)
    blend_effect.inputs[2].default_value = 1
    links.new(inp["AlphaBlend"], blend_effect.inputs["Factor"])
    links.new(blend_alpha.outputs[0], blend_effect.inputs[3])

    # ------------------------------------------------
    # FinalAlpha = MaskAlpha * BlendEffective
    # ------------------------------------------------
    final_mix = nodes.new("ShaderNodeMath")
    final_mix.name = 'Final Alpha'
    final_mix.label = 'FinalAlpha'
    final_mix.operation = 'MULTIPLY'
    final_mix.location = (717, 105)
    links.new(mask_mix.outputs[0], final_mix.inputs[0])
    links.new(blend_effect.outputs[0], final_mix.inputs[1])

    # ------------------------------------------------
    # Texture Toggle nodes
    # ------------------------------------------------
    texture0 = nodes.new('ShaderNodeMath')
    texture0.name = 'Texture Index 0'
    texture0.label = 'Texture0'
    texture0.operation = 'COMPARE'
    texture0.location = (-1019, -490)
    texture0.inputs[1].default_value = 0.0
    texture0.inputs[2].default_value = 0.0
    links.new(inp["TextureIndex"], texture0.inputs[0])

    solid_override = nodes.new('ShaderNodeMix')
    solid_override.name = 'SolidFill Override'
    solid_override.label = 'SolidFillOverride'
    solid_override.data_type = 'RGBA'
    solid_override.location = (902, 329)
    solid_override.inputs[7].default_value = (1.0, 1.0, 1.0, 1.0)
    links.new(texture0.outputs[0], solid_override.inputs[0])
    links.new(inp["sRGB Texture"], solid_override.inputs[6])

    links.new(solid_override.outputs[2], principled.inputs["Base Color"])

    # ------------------------------------------------
    # Transparent Toggle nodes
    # ------------------------------------------------
    draw0 = nodes.new('ShaderNodeMath')
    draw0.name = 'Drawstyle 0'
    draw0.label = 'Draw0'
    draw0.operation = 'COMPARE'
    draw0.location = (-1018, -266)
    draw0.inputs[1].default_value = 0.0
    draw0.inputs[2].default_value = 0.0
    links.new(inp["Drawstyle"], draw0.inputs[0])

    trans_effective = nodes.new('ShaderNodeMath')
    trans_effective.name = 'Transparent Effective'
    trans_effective.label = 'TransparentEffective'
    trans_effective.operation = 'MULTIPLY'
    trans_effective.location = (-720, -540)
    links.new(draw0.outputs[0], trans_effective.inputs[0])
    links.new(texture0.outputs[0], trans_effective.inputs[1])

    trans_override = nodes.new('ShaderNodeMix')
    trans_override.name = 'Transparent Override'
    trans_override.label = 'TransparentOverride'
    trans_override.location = (914, -29)
    trans_override.inputs[3].default_value = 0.1
    links.new(trans_effective.outputs[0], trans_override.inputs[0])
    links.new(final_mix.outputs[0], trans_override.inputs[2])

    links.new(trans_override.outputs[0], principled.inputs["Alpha"])

    # ------------------------------------------------
    # Additive Toggle nodes
    # ------------------------------------------------

    # EmissionStrength = Additive * FinalAlpha * 0.75
    add_effective = nodes.new("ShaderNodeMath")
    add_effective.name = 'Additive Effective'
    add_effective.label = 'AdditiveEffective'
    add_effective.operation = 'MULTIPLY'
    add_effective.location = (-707, -233)
    links.new(inp["AlphaBlend"], add_effective.inputs[0])
    links.new(inp["Additive"], add_effective.inputs[1])

    glow_strength = nodes.new("ShaderNodeMath")
    glow_strength.name = 'Glow Strength'
    glow_strength.label = 'GlowStrength'
    glow_strength.operation = 'MULTIPLY'
    glow_strength.location = (-291, -126)
    glow_strength.inputs[1].default_value = 8.0
    links.new(add_effective.outputs[0], glow_strength.inputs[0])

    emission_strength = nodes.new("ShaderNodeMath")
    emission_strength.name = 'Emission Strength'
    emission_strength.label = 'EmissionStrength'
    emission_strength.operation = 'MULTIPLY'
    emission_strength.location = (725, -187)
    links.new(mask_mix.outputs[0], emission_strength.inputs[0])
    links.new(glow_strength.outputs[0], emission_strength.inputs[1])

    links.new(emission_strength.outputs[0], principled.inputs["Emission Strength"])

    # sRGB Texture * 2 -> Saturation 1.4
    add_color = nodes.new('ShaderNodeMix')
    add_color.name = 'Additive Color'
    add_color.label = "AdditiveColor"
    add_color.data_type = 'RGBA'
    add_color.blend_type = 'MULTIPLY'
    add_color.location = (213, -345)
    add_color.inputs[0].default_value = 1.0
    links.new(inp["sRGB Texture"], add_color.inputs[6])
    links.new(inp["sRGB Texture"], add_color.inputs[7])

    saturation = nodes.new('ShaderNodeHueSaturation')
    saturation.name = 'Saturation Adjust'
    saturation.label = 'SaturationAdjust'
    saturation.location = (475, -401)
    saturation.inputs[1].default_value = 1.4
    links.new(add_color.outputs[2], saturation.inputs[4])

    links.new(saturation.outputs[0], principled.inputs["Emission Color"])

    # ------------------------------------------------
    # Output
    # ------------------------------------------------
    links.new(principled.outputs["BSDF"], out["Shader"])

    return group

def parse_rendermethod_string(rm: str) -> dict:

    result = {
        "use_userdefined": False,
        "userdefined_index": 0,

        "drawstyle": "SOLIDFILL",
        "lighting": "AMBIENT",
        "shading": "GOURAUD1",
        "texture_index": 0,

        "masked": False,
        "alphablend": False,
        "opacity": 100.0,
        "additive": False,
        "dynamic": False,
        "prelit": False,
    }

    if not rm:
        return result

    # ----------------------------------------
    # USERDEFINED
    # ----------------------------------------
    if rm.startswith("USERDEFINED_"):
        try:
            idx = int(rm.split("_")[1])
            result["use_userdefined"] = True
            result["userdefined_index"] = idx
            return result
        except:
            return result

    # ----------------------------------------
    # Masked
    # ----------------------------------------
    if "TRANS" in rm:
        result["masked"] = True

    # ----------------------------------------
    # Additive
    # ----------------------------------------
    if "ADDITIVE" in rm:
        result["additive"] = True

    if "DYNAMIC" in rm:
        result["dynamic"] = True

    if "PRELIT" in rm:
        result["prelit"] = True

    # ----------------------------------------
    # Alpha Blend + Opacity
    # ----------------------------------------
    if "BLEND" in rm:
        result["alphablend"] = True

    if "OPACITY" in rm:
        try:
            start = rm.index("OPACITY") + len("OPACITY")
            end = rm.index("%", start)
            val = float(rm[start:end])
            result["opacity"] = val
        except:
            pass

    # ----------------------------------------
    # Drawstyle
    # ----------------------------------------
    if "WIREFRAME" in rm:
        result["drawstyle"] = "WIREFRAME"
    elif "DRAW0" in rm:
        result["drawstyle"] = "DRAW0"
    elif "DRAW1" in rm:
        result["drawstyle"] = "DRAW1"
    elif "SOLIDFILL" in rm:
        result["drawstyle"] = "SOLIDFILL"

    # ----------------------------------------
    # Lighting
    # ----------------------------------------
    lighting_keywords = [
        "ZEROINTENSITY",
        "LIGHT1",
        "CONSTANT",
        "LIGHT3",
        "AMBIENT",
        "SCALEDAMBIENT",
        "LIGHT6",
        "LIGHT7",
    ]

    for key in lighting_keywords:
        if key in rm:
            result["lighting"] = key
            break

    # ----------------------------------------
    # Shading
    # ----------------------------------------
    if "GOURAUD1" in rm:
        result["shading"] = "GOURAUD1"
    elif "GOURAUD2" in rm:
        result["shading"] = "GOURAUD2"
    elif "SHADE1" in rm:
        result["shading"] = "SHADE1"
    elif "SHADE0" in rm:
        result["shading"] = "SHADE0"

    # ----------------------------------------
    # Texture index
    # ----------------------------------------
    if "TEXTURE" in rm:
        try:
            idx = rm.index("TEXTURE") + len("TEXTURE")
            num = ""
            while idx < len(rm) and rm[idx].isdigit():
                num += rm[idx]
                idx += 1
            result["texture_index"] = int(num)
        except:
            pass

    return result

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
    props.uvshiftperms = material.uvshiftperms
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
        "Masked",
        "AlphaBlend",
        "Additive",
        "Opacity",
        "Drawstyle",
        "TextureIndex",
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
    drawstyle_map = {
        "DRAW0": 0.0,
        "DRAW1": 1.0,
        "WIREFRAME": 2.0,
        "SOLIDFILL": 3.0,
    }

    group_node.inputs["Drawstyle"].default_value = drawstyle_map.get(
        props.drawstyle, 0.0
    )

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
