# common/rendermethod.py

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

def sync_rendermethod_node(mat):
    if not mat or not mat.node_tree:
        return

    group_node = None

    for node in mat.node_tree.nodes:
        if node.type == 'GROUP' and node.node_tree and node.node_tree.name == "RENDERMETHOD":
            group_node = node
            break

    if not group_node:
        return

    props = mat.quail_materialdefinition

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