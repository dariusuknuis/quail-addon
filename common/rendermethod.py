# common/rendermethod.py
import bpy

USERDEFINED_MAP = {

1:  ('DRAW0',     'ZEROINTENSITY', 'SHADE0',   0, False, False, False, False, False, 0.0),   #0          "TRANSPARENT"
2:  ('SOLIDFILL', 'SCALEDAMBIENT', 'GOURAUD1', 5, False, False, False, True,  False, 0.0),   #0x200557   "TEXTURE5SCALEDAMBIENTGOURAUD1DYNAMIC"
3:  ('SOLIDFILL', 'CONSTANT',      'GOURAUD1', 5, False, False, False, True,  False, 0.0),   #0x20054b   "TEXTURE5CONSTANTGOURAUD1DYNAMIC"
4:  ('SOLIDFILL', 'SCALEDAMBIENT', 'GOURAUD1', 0, False, False, False, False, False, 0.0),   #0x57       "SOLIDFILLSCALEDAMBIENTGOURAUD1"
5:  ('SOLIDFILL', 'CONSTANT',      'GOURAUD1', 0, False, False, False, False, False, 0.0),   #0x4b       "SOLIDFILLCONSTANTGOURAUD1"
6:  ('SOLIDFILL', 'SCALEDAMBIENT', 'GOURAUD1', 5, False, True,  False, True,  False, 50.0),  #0x1280557  "TEXTURE5SCALEDAMBIENTGOURAUD1DYNAMICBLENDOPACITY50.0%"
7:  ('SOLIDFILL', 'CONSTANT',      'GOURAUD1', 5, False, True,  False, True,  False, 25.0),  #0x124054b  "TEXTURE5CONSTANTGOURAUD1DYNAMICBLENDOPACITY25.0%"
8:  ('SOLIDFILL', 'SCALEDAMBIENT', 'GOURAUD1', 5, True,  False, False, True,  False, 0.0),   #0x2005d7   "TRANSTEXTURE5SCALEDAMBIENTGOURAUD1DYNAMIC"
9:  ('SOLIDFILL', 'CONSTANT',      'GOURAUD1', 5, True,  False, False, False, False, 0.0),   #0x5cb      "TRANSTEXTURE5CONSTANTGOURAUD1"
10: ('SOLIDFILL', 'SCALEDAMBIENT', 'GOURAUD1', 5, False, True,  False, True,  False, 25.0),  #0x1240557  "TEXTURE5SCALEDAMBIENTGOURAUD1DYNAMICBLENDOPACITY25.0%"
11: ('SOLIDFILL', 'SCALEDAMBIENT', 'GOURAUD1', 5, False, True,  False, True,  False, 75.0),  #0x12c0557  "TEXTURE5SCALEDAMBIENTGOURAUD1DYNAMICBLENDOPACITY75.0%"
12: ('SOLIDFILL', 'SCALEDAMBIENT', 'GOURAUD1', 5, False, True,  True,  True,  False, 68.75), #0x13b0557  "TEXTURE5SCALEDAMBIENTGOURAUD1ADDITIVEDYNAMICBLENDOPACITY68.75%"
13: ('SOLIDFILL', 'LIGHT1',        'SHADE0',   5, False, False, False, False, False, 0.0),   #0x507      "TEXTURE5LIGHT1SHADE0"
14: ('SOLIDFILL', 'LIGHT1',        'SHADE0',   4, False, False, False, False, True,  0.0),   #0x40000407 "TEXTURE4LIGHT1SHADE0PRELIT"
15: ('SOLIDFILL', 'LIGHT3',        'GOURAUD2', 4, False, False, False, False, True,  0.0),   #0x40000473 "TEXTURE4LIGHT3GOURAUD2PRELIT"
16: ('SOLIDFILL', 'LIGHT1',        'SHADE0',   4, False, True,  False, False, True,  50.0),  #0x41080407 "TEXTURE4LIGHT1SHADE0PRELITBLENDOPACITY50.0%"
17: ('SOLIDFILL', 'LIGHT1',        'SHADE0',   4, False, True,  True,  False, True,  68.75), #0x411b0407 "TEXTURE4LIGHT1SHADE0ADDITIVEPRELITBLENDOPACITY68.75%"
18: ('SOLIDFILL', 'LIGHT1',        'SHADE0',   5, False, False, False, False, False, 0.0),   #0x507      "TEXTURE5LIGHT1SHADE0"
19: ('SOLIDFILL', 'LIGHT1',        'SHADE0',   5, False, False, False, False, False, 0.0),   #0x507      "TEXTURE5LIGHT1SHADE0"
20: ('SOLIDFILL', 'SCALEDAMBIENT', 'GOURAUD1', 5, True,  False, False, False, False, 0.0),   #0x5d7      "TRANSTEXTURE5SCALEDAMBIENTGOURAUD1"
21: ('SOLIDFILL', 'LIGHT3',        'GOURAUD2', 4, False, False, False, True,  False, 0.0),   #0x200473   "TEXTURE4LIGHT3GOURAUD2DYNAMIC"
22: ('SOLIDFILL', 'LIGHT3',        'GOURAUD2', 4, False, False, False, True,  False, 0.0),   #0x200473   "TEXTURE4LIGHT3GOURAUD2DYNAMIC"
23: ('SOLIDFILL', 'LIGHT3',        'GOURAUD2', 4, True,  False, False, True,  False, 0.0),   #0x2004f3   "TRANSTEXTURE4LIGHT3GOURAUD2DYNAMIC"
24: ('SOLIDFILL', 'LIGHT1',        'SHADE0',   5, False, True,  True,  False, False, 68.75), #0x11b0507  "TEXTURE5LIGHT1SHADE0ADDITIVEBLENDOPACITY68.75%"
25: ('SOLIDFILL', 'LIGHT1',        'SHADE0',   5, False, True,  False, False, False, 50.0),  #0x1080507  "TEXTURE5LIGHT1SHADE0BLENDOPACITY50.0%"
26: ('SOLIDFILL', 'LIGHT1',        'SHADE0',   5, True,  False, False, False, False, 0.0),   #0x587      "TRANSTEXTURE5LIGHT1SHADE0"
27: ('DRAW0',     'ZEROINTENSITY', 'SHADE0',   0, False, False, False, False, False, 0.0),   #0          "TRANSPARENT"
28: ('DRAW0',     'ZEROINTENSITY', 'SHADE0',   0, False, False, False, False, False, 0.0),   #0          "INVALID/RESERVED"
29: ('DRAW0',     'ZEROINTENSITY', 'SHADE0',   0, False, False, False, False, False, 0.0),   #0          "INVALID/RESERVED"
30: ('DRAW0',     'ZEROINTENSITY', 'SHADE0',   0, False, False, False, False, False, 0.0),   #0          "INVALID/RESERVED"
31: ('DRAW0',     'ZEROINTENSITY', 'SHADE0',   0, False, False, False, False, False, 0.0),   #0          "TRANSPARENT"
32: ('SOLIDFILL', 'SCALEDAMBIENT', 'GOURAUD1', 5, False, False, False, False, True,  0.0),   #0x40000557 "TEXTURE5SCALEDAMBIENTGOURAUD1PRELIT"
33: ('SOLIDFILL', 'CONSTANT',      'GOURAUD1', 5, False, False, False, False, True,  0.0),   #0x4000054b "TEXTURE5CONSTANTGOURAUD1PRELIT"
34: ('SOLIDFILL', 'SCALEDAMBIENT', 'GOURAUD1', 0, False, False, False, False, True,  0.0),   #0x40000057 "SOLIDFILLSCALEDAMBIENTGOURAUD1PRELIT"
35: ('SOLIDFILL', 'CONSTANT',      'GOURAUD1', 0, False, False, False, False, True,  0.0),   #0x4000004b "SOLIDFILLCONSTANTGOURAUD1PRELIT"
36: ('SOLIDFILL', 'SCALEDAMBIENT', 'GOURAUD1', 5, False, True,  False, False, True,  50.0),  #0x41080557 "TEXTURE5SCALEDAMBIENTGOURAUD1PRELITBLENDOPACITY50.0%"
37: ('SOLIDFILL', 'CONSTANT',      'GOURAUD1', 5, False, True,  False, False, True,  25.0),  #0x4104054b "TEXTURE5CONSTANTGOURAUD1PRELITBLENDOPACITY25.0%"
38: ('SOLIDFILL', 'SCALEDAMBIENT', 'GOURAUD1', 5, False, False, False, False, True,  0.0),   #0x400005d7 "TEXTURE5SCALEDAMBIENTGOURAUD1PRELIT"
39: ('SOLIDFILL', 'CONSTANT',      'GOURAUD1', 5, True,  False, False, False, True,  0.0),   #0x400005cb "TRANSTEXTURE5CONSTANTGOURAUD1PRELIT"
40: ('SOLIDFILL', 'SCALEDAMBIENT', 'GOURAUD1', 5, False, True,  False, False, True,  25.0),  #0x41040557 "TEXTURE5SCALEDAMBIENTGOURAUD1PRELITBLENDOPACITY25.0%"
41: ('SOLIDFILL', 'SCALEDAMBIENT', 'GOURAUD1', 5, False, True,  False, False, True,  68.75), #0x410c0557 "TEXTURE5SCALEDAMBIENTGOURAUD1PRELITBLENDOPACITY75.0%"
}

def apply_userdefined(props, index: int):
    data = USERDEFINED_MAP.get(index)
    if not data:
        return

    (
        drawstyle,
        lighting,
        shading,
        texture,
        masked,
        alphablend,
        additive,
        dynamic,
        prelit,
        opacity
    ) = data

    props.drawstyle = drawstyle
    props.lighting = lighting
    props.shading = shading
    props.texture_index = texture
    props.masked = masked
    props.alphablend = alphablend
    props.additive = additive
    props.dynamic = dynamic
    props.prelit = prelit
    props.opacity = opacity

def sync_rendermethod_node(mat, props):
    if not mat or not mat.node_tree:
        return

    group_node = None

    for node in mat.node_tree.nodes:
        if node.type == 'GROUP' and node.node_tree and node.node_tree.name == "RENDERMETHOD":
            group_node = node
            break

    if not group_node:
        return

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

def apply_transparent(props):

    props.drawstyle = "DRAW0"
    props.lighting = "ZEROINTENSITY"
    props.shading = "SHADE0"
    props.texture_index = 0
    props.masked = False
    props.alphablend = False
    props.additive = False
    props.dynamic = False
    props.prelit = False
    props.opacity = 0.0

def build_rendermethod_string(props) -> str:

    # ----------------------------------------
    # Userdefined shortcut
    # ----------------------------------------
    if props.use_userdefined:
        return f"USERDEFINED_{props.userdefined_index}"

    # ----------------------------------------
    # Transparent override
    # ----------------------------------------
    if props.transparent_override:
        return "TRANSPARENT"

    parts = []

    # ----------------------------------------
    # Texture
    # ----------------------------------------
    if props.texture_index > 0:
        parts.append(f"TEXTURE{props.texture_index}")

    # ----------------------------------------
    # Masked (TRANS prefix)
    # ----------------------------------------
    if props.masked:
        parts.insert(0, "TRANS")

    # ----------------------------------------
    # Lighting
    # ----------------------------------------
    parts.append(props.lighting)

    # ----------------------------------------
    # Shading
    # ----------------------------------------
    parts.append(props.shading)

    # ----------------------------------------
    # Dynamic / Prelit
    # ----------------------------------------
    if props.dynamic:
        parts.append("DYNAMIC")

    if props.prelit:
        parts.append("PRELIT")

    # ----------------------------------------
    # Alpha blend
    # ----------------------------------------
    if props.alphablend:
        parts.append("BLEND")

        # Only include opacity if blending
        parts.append(f"OPACITY{props.opacity}%")

    # ----------------------------------------
    # Additive
    # ----------------------------------------
    if props.additive:
        parts.append("ADDITIVE")

    # ----------------------------------------
    # Drawstyle fallback (rarely needed)
    # ----------------------------------------
    if not parts:
        parts.append(props.drawstyle)

    return "".join(parts)

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
    group_output.location = (1728, 12)

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
    add_input("PassableDisplay", "NodeSocketFloat") # Not really part of Rendermethod, but for displaying passable face flag

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

    # Transparent blit flag addon
    transparent_blit = group.interface.new_socket(
        name="Transparent Blit",
        in_out='INPUT',
        socket_type="NodeSocketFloat"
    )

    transparent_blit.default_value = 1.0

    inp = group_input.outputs
    out = group_output.inputs

    # -----------------------------------------
    # Base Principled Shader
    # -----------------------------------------
    principled = nodes.new("ShaderNodeBsdfPrincipled")
    principled.location = (1408, 15)
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
    texture0.location = (-921, -605)
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

    # ------------------------------------------------
    # Passable flag stuff
    # ------------------------------------------------
    passable_attribute = nodes.new('ShaderNodeAttribute')
    passable_attribute.name = 'Passable Attribute'
    passable_attribute.label = 'PassableAttribute'
    passable_attribute.attribute_name = "PASSABLE"
    passable_attribute.location = (444, 732)

    passable_effective = nodes.new("ShaderNodeMath")
    passable_effective.name = 'Passable Effective'
    passable_effective.label = 'PassableEffective'
    passable_effective.operation = 'MULTIPLY'
    passable_effective.location = (644, 732)
    links.new(inp["PassableDisplay"], passable_effective.inputs[0])
    links.new(passable_attribute.outputs[0], passable_effective.inputs[1])

    passable_override = nodes.new('ShaderNodeMix')
    passable_override.name = 'Passable Override'
    passable_override.label = 'PassableOverride'
    passable_override.data_type = 'RGBA'
    passable_override.blend_type = 'COLOR'
    passable_override.location = (1022, 529)
    passable_override.inputs[7].default_value = (0.0, 1.0, 0.0, 1.0)
    links.new(passable_effective.outputs[0], passable_override.inputs[0])
    links.new(solid_override.outputs[2], passable_override.inputs[6])

    links.new(passable_override.outputs[2], principled.inputs["Base Color"])

    # ------------------------------------------------
    # Transparent Toggle nodes
    # ------------------------------------------------
    draw0 = nodes.new('ShaderNodeMath')
    draw0.name = 'Drawstyle 0'
    draw0.label = 'Draw0'
    draw0.operation = 'COMPARE'
    draw0.location = (-920, -381)
    draw0.inputs[1].default_value = 0.0
    draw0.inputs[2].default_value = 0.0
    links.new(inp["Drawstyle"], draw0.inputs[0])

    trans_effective = nodes.new('ShaderNodeMath')
    trans_effective.name = 'Transparent Effective'
    trans_effective.label = 'TransparentEffective'
    trans_effective.operation = 'MULTIPLY'
    trans_effective.location = (-539, -611)
    links.new(draw0.outputs[0], trans_effective.inputs[0])
    links.new(texture0.outputs[0], trans_effective.inputs[1])

    trans_override = nodes.new('ShaderNodeMix')
    trans_override.name = 'Transparent Override'
    trans_override.label = 'TransparentOverride'
    trans_override.location = (914, -29)
    trans_override.inputs[3].default_value = 0.1
    links.new(trans_effective.outputs[0], trans_override.inputs[0])
    links.new(final_mix.outputs[0], trans_override.inputs[2])

    # ------------------------------------------------
    # More Passable flag stuff
    # ------------------------------------------------
    passable_mix = nodes.new("ShaderNodeMix")
    passable_mix.name = 'Passable Factor'
    passable_mix.label = 'PassableFactor'
    passable_mix.data_type = 'FLOAT'
    passable_mix.location = (1124, 170)
    passable_mix.inputs[2].default_value = 1
    passable_mix.inputs[3].default_value = 0.5
    links.new(passable_effective.outputs[0], passable_mix.inputs["Factor"])

    passable_alpha = nodes.new("ShaderNodeMath")
    passable_alpha.name = 'Passable Alpha'
    passable_alpha.label = 'PassableAlpha'
    passable_alpha.operation = 'MULTIPLY'
    passable_alpha.location = (1224, 35)
    links.new(passable_mix.outputs[0], passable_alpha.inputs[0])
    links.new(trans_override.outputs[0], passable_alpha.inputs[1])

    links.new(passable_alpha.outputs[0], principled.inputs["Alpha"])

    # ------------------------------------------------
    # Additive Toggle nodes
    # ------------------------------------------------

    rgb_to_bw = nodes.new("ShaderNodeRGBToBW")
    rgb_to_bw.name = 'RGB to BW'
    rgb_to_bw.label = 'RGBtoBW'
    rgb_to_bw.location = (-939, -94)
    links.new(inp["sRGB Texture"], rgb_to_bw.inputs[0])

    black_range = nodes.new("ShaderNodeMapRange")
    black_range.name = 'Blackness Range'
    black_range.label = 'BlacknessRange'
    black_range.location = (-760, -94)
    black_range.clamp = True
    black_range.inputs["From Min"].default_value = 0.0
    black_range.inputs["From Max"].default_value = 0.03
    black_range.inputs["To Min"].default_value = 0.0
    black_range.inputs["To Max"].default_value = 1.0

    links.new(rgb_to_bw.outputs[0], black_range.inputs["Value"])

    # EmissionStrength = Additive * FinalAlpha * 0.75
    add_effective = nodes.new("ShaderNodeMath")
    add_effective.name = 'Additive Effective'
    add_effective.label = 'AdditiveEffective'
    add_effective.operation = 'MULTIPLY'
    add_effective.location = (-707, -233)
    links.new(inp["AlphaBlend"], add_effective.inputs[0])
    links.new(inp["Additive"], add_effective.inputs[1])

    additive_enabled = nodes.new('ShaderNodeMix')
    additive_enabled.name = 'Additive Mask Enabled'
    additive_enabled.label = 'AdditiveMaskEnabled'
    additive_enabled.data_type = 'FLOAT'
    additive_enabled.location = (-619, -288)
    additive_enabled.inputs[2].default_value = 1
    links.new(add_effective.outputs[0], additive_enabled.inputs["Factor"])
    links.new(black_range.outputs[0], additive_enabled.inputs[3])

    additive_blend = nodes.new("ShaderNodeMath")
    additive_blend.name = 'Additive Blend'
    additive_blend.label = 'AdditiveBlend'
    additive_blend.operation = 'MULTIPLY'
    additive_blend.location = (62, 79)
    links.new(additive_enabled.outputs[0], additive_blend.inputs[0])
    links.new(blend_alpha.outputs[0], additive_blend.inputs[1])
    links.new(additive_blend.outputs[0], blend_effect.inputs[3])

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
    # Transparent Blit Override (Prevents masked)
    # ------------------------------------------------

    trans_blit_flag = nodes.new("ShaderNodeMath")
    trans_blit_flag.name = 'Transparent Blit Flag'
    trans_blit_flag.label = 'TransparentBlitFlag'
    trans_blit_flag.operation = 'MULTIPLY'
    trans_blit_flag.location = (265, 406)
    links.new(inp["Transparent Blit"], trans_blit_flag.inputs[0])
    links.new(mask_allow.outputs[0], trans_blit_flag.inputs[1])
    links.new(trans_blit_flag.outputs[0], mask_mix.inputs["Factor"])

    # ------------------------------------------------
    # Output
    # ------------------------------------------------
    links.new(principled.outputs["BSDF"], out["Shader"])

    return group

def parse_rendermethod_string(rm: str) -> dict:

    result = {
        "transparent": False,
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
    # TRANSPARENT (SPECIAL CASE)
    # ----------------------------------------
    if rm.strip().upper() == "TRANSPARENT":
        result["transparent"] = True
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
    if "TRANS" in rm and rm.strip().upper() != "TRANSPARENT":
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