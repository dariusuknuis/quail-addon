# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportAttributeAccessIssue=false

import bpy
from ..wce.wce import wce
from ..wce.simplespritedef import simplespritedef
from .context import Context
from ..common.image_loader import load_texture

def get_noncolor_copy(image):
    nc_name = f"{image.name}_nc"

    # Reuse existing if already created
    existing = bpy.data.images.get(nc_name)
    if existing:
        return existing

    # Duplicate image datablock
    new_img = image.copy()
    new_img.name = nc_name

    return new_img

def create_bmp_wrapper_node(nodes, links, image, x_offset):

    group_name = f"{image.name}"

    if group_name in bpy.data.node_groups:
        wrapper_node = nodes.new("ShaderNodeGroup")
        wrapper_node.node_tree = bpy.data.node_groups[group_name]
        wrapper_node.location = (x_offset, 0)
        return wrapper_node

    group = bpy.data.node_groups.new(group_name, 'ShaderNodeTree')
    group['quaildef'] = 'bmp_wrapper'

    group.interface.new_socket("Color", in_out='OUTPUT', socket_type="NodeSocketColor")
    group.interface.new_socket("Alpha", in_out='OUTPUT', socket_type="NodeSocketFloat")

    gnodes = group.nodes
    glinks = group.links

    g_output = gnodes.new("NodeGroupOutput")
    g_output.location = (1200, 0)

    # ------------------------------------------------
    # sRGB image
    # ------------------------------------------------
    img_color = gnodes.new("ShaderNodeTexImage")
    img_color.image = image
    img_color.location = (-800, 0)

    # ------------------------------------------------
    # Non-color image
    # ------------------------------------------------
    img_nc = gnodes.new("ShaderNodeTexImage")

    nc_image = get_noncolor_copy(image)

    img_nc.image = nc_image
    img_nc.interpolation = 'Closest'
    img_nc.image.colorspace_settings.name = 'Non-Color'
    img_nc.location = (-800, -300)

    # ------------------------------------------------
    # Index-0 color from image metadata
    # ------------------------------------------------
    index0 = image.get("bmp_index0_color", (0.0, 0.0, 0.0))

    rgb_node = gnodes.new("ShaderNodeRGB")
    rgb_node.outputs[0].default_value = (*index0, 1.0)
    rgb_node.location = (-1000, -150)

    # ------------------------------------------------
    # Separate colors
    # ------------------------------------------------
    sep_color1 = gnodes.new('ShaderNodeSeparateColor')
    sep_color1.location = (-600, -150)
    glinks.new(rgb_node.outputs[0], sep_color1.inputs[0])

    sep_color2 = gnodes.new('ShaderNodeSeparateColor')
    sep_color2.location = (-600, -350)
    glinks.new(img_nc.outputs[0], sep_color2.inputs[0])

    # ------------------------------------------------
    # Subtract R/G/B
    # ------------------------------------------------
    subtract1 = gnodes.new("ShaderNodeMath")
    subtract1.operation = 'SUBTRACT'
    subtract1.location = (-400, -100)
    glinks.new(sep_color2.outputs[0], subtract1.inputs[0])
    glinks.new(sep_color1.outputs[0], subtract1.inputs[1])

    subtract2 = gnodes.new("ShaderNodeMath")
    subtract2.operation = 'SUBTRACT'
    subtract2.location = (-400, -250)
    glinks.new(sep_color2.outputs[1], subtract2.inputs[0])
    glinks.new(sep_color1.outputs[1], subtract2.inputs[1])

    subtract3 = gnodes.new("ShaderNodeMath")
    subtract3.operation = 'SUBTRACT'
    subtract3.location = (-400, -400)
    glinks.new(sep_color2.outputs[2], subtract3.inputs[0])
    glinks.new(sep_color1.outputs[2], subtract3.inputs[1])

    # ------------------------------------------------
    # Absolute R/G/B
    # ------------------------------------------------
    absolute1 = gnodes.new("ShaderNodeMath")
    absolute1.operation = 'ABSOLUTE'
    absolute1.location = (-200, -100)
    glinks.new(subtract1.outputs[0], absolute1.inputs[0])

    absolute2 = gnodes.new("ShaderNodeMath")
    absolute2.operation = 'ABSOLUTE'
    absolute2.location = (-200, -250)
    glinks.new(subtract2.outputs[0], absolute2.inputs[0])

    absolute3 = gnodes.new("ShaderNodeMath")
    absolute3.operation = 'ABSOLUTE'
    absolute3.location = (-200, -400)
    glinks.new(subtract3.outputs[0], absolute3.inputs[0])

    # ------------------------------------------------
    # Add R+G
    # ------------------------------------------------
    add1 = gnodes.new("ShaderNodeMath")
    add1.operation = 'ADD'
    add1.location = (0, -175)
    glinks.new(absolute1.outputs[0], add1.inputs[0])
    glinks.new(absolute2.outputs[0], add1.inputs[1])

    # ------------------------------------------------
    # Add (R+G)+B
    # ------------------------------------------------
    add2 = gnodes.new("ShaderNodeMath")
    add2.operation = 'ADD'
    add2.location = (200, -250)
    glinks.new(add1.outputs[0], add2.inputs[0])
    glinks.new(absolute3.outputs[0], add2.inputs[1])

    # ------------------------------------------------
    # Greater Than (final alpha mask)
    # ------------------------------------------------
    bitmap_alpha = gnodes.new("ShaderNodeMath")
    bitmap_alpha.operation = 'GREATER_THAN'
    bitmap_alpha.inputs[1].default_value = 0.00001
    bitmap_alpha.location = (400, -250)
    glinks.new(add2.outputs[0], bitmap_alpha.inputs[0])

    # ------------------------------------------------
    # Connect outputs
    # ------------------------------------------------
    glinks.new(img_color.outputs["Color"], g_output.inputs["Color"])
    glinks.new(bitmap_alpha.outputs[0], g_output.inputs["Alpha"])

    # ------------------------------------------------
    # Instance wrapper in parent graph
    # ------------------------------------------------
    wrapper_node = nodes.new("ShaderNodeGroup")
    wrapper_node.node_tree = group
    wrapper_node.location = (x_offset, 0)

    return wrapper_node

def create_frame_nodegroup(ctx, frame, sprite_tag):
    frame_group_name = f"{frame.name}"

    if frame_group_name in bpy.data.node_groups:
        return bpy.data.node_groups[frame_group_name]

    group = bpy.data.node_groups.new(frame_group_name, 'ShaderNodeTree')
    group['quaildef'] = 'simplesprite_frame'

    nodes = group.nodes
    links = group.links

    # Interface
    group.interface.new_socket("Color", in_out='OUTPUT', socket_type="NodeSocketColor")
    group.interface.new_socket("Alpha", in_out='OUTPUT', socket_type="NodeSocketFloat")

    detail_input = group.interface.new_socket(
        name="Detail Scale",
        in_out='INPUT',
        socket_type="NodeSocketFloat"
    )
    detail_input.default_value = 1.0

    for i in range(10):
        tiled_input = group.interface.new_socket(
            name=f"Tiled {i+1} Scale",
            in_out='INPUT',
            socket_type="NodeSocketFloat"
        )
        tiled_input.default_value = 1.0

    group_input = nodes.new("NodeGroupInput")
    group_input.location = (-1200, 0)

    group_output = nodes.new("NodeGroupOutput")
    group_output.location = (800, 0)

    current_x = 0

    if not frame.files:
        return group

    # ------------------------------------------------
    # BASE (File 0)
    # ------------------------------------------------
    base_file = frame.files[0]
    base_image = base_file.image

    if not base_image:
        return group

    image_type = base_image.get("image_type", "OTHER")

    if image_type == "BMP":
        base_tex = create_bmp_wrapper_node(nodes, links, base_image, current_x)
    else:
        base_tex = nodes.new("ShaderNodeTexImage")
        base_tex.image = base_image
        base_tex.location = (current_x, 0)

    # ------------------------------------------------
    # DETAIL case
    # ------------------------------------------------
    if len(frame.files) > 1 and frame.files[1].texture_mode == 'DETAIL':

        detail_file = frame.files[1]
        detail_image = detail_file.image

        if not detail_image:
            return group

        # Mapping node
        mapping = nodes.new("ShaderNodeMapping")
        mapping.location = (-800, -200)

        # Use UV
        texcoord = nodes.new("ShaderNodeTexCoord")
        texcoord.location = (-1000, -200)

        links.new(texcoord.outputs["UV"], mapping.inputs["Vector"])

        # Connect group input Detail Scale to Mapping Scale
        links.new(
            group_input.outputs["Detail Scale"],
            mapping.inputs["Scale"]
        )

        # Detail texture
        detail_tex = nodes.new("ShaderNodeTexImage")
        detail_tex.image = detail_image
        detail_tex.location = (-600, -200)

        links.new(mapping.outputs["Vector"], detail_tex.inputs["Vector"])

        # Mix
        mix = nodes.new("ShaderNodeMixRGB")
        mix.blend_type = 'MIX'
        mix.inputs["Fac"].default_value = 0.25
        mix.location = (-200, 0)

        # Base → Color1
        links.new(base_tex.outputs["Color"], mix.inputs["Color1"])

        # Detail → Color2
        links.new(detail_tex.outputs["Color"], mix.inputs["Color2"])

        # Output color
        links.new(mix.outputs["Color"], group_output.inputs["Color"])

        # Preserve alpha from base
        if "Alpha" in base_tex.outputs:
            links.new(base_tex.outputs["Alpha"], group_output.inputs["Alpha"])

    # ------------------------------------------------
    # LAYER case
    # ------------------------------------------------
    elif len(frame.files) > 1 and frame.files[1].texture_mode == 'LAYER':

        layer_file = frame.files[1]
        layer_image = layer_file.image

        if not layer_image:
            return group

        layer_tex = nodes.new("ShaderNodeTexImage")
        layer_tex.image = layer_image
        layer_tex.location = (-600, -150)

        mix = nodes.new("ShaderNodeMixRGB")
        mix.blend_type = 'MIX'
        mix.location = (-200, 0)

        # Base → Color1
        links.new(base_tex.outputs["Color"], mix.inputs["Color1"])

        # Layer → Color2
        links.new(layer_tex.outputs["Color"], mix.inputs["Color2"])

        # Layer alpha drives mix
        links.new(layer_tex.outputs["Alpha"], mix.inputs["Fac"])

        # Output color only
        links.new(mix.outputs["Color"], group_output.inputs["Color"])

        # Do NOT connect Alpha output

    else:
        # No layer → just base
        links.new(base_tex.outputs["Color"], group_output.inputs["Color"])
        if "Alpha" in base_tex.outputs:
            links.new(base_tex.outputs["Alpha"], group_output.inputs["Alpha"])

    current_x += 300

    return group

def decode_simplespritedef(ctx: Context, simplesprite: simplespritedef) -> str:

    if simplesprite.tag in bpy.data.node_groups:
        return ""

    simplesprite_node = bpy.data.node_groups.new(
        simplesprite.tag,
        'ShaderNodeTree'
    )
    simplesprite_node['quaildef'] = 'simplespritedef'

    props = simplesprite_node.quail_simplesprite

    props.skipframes = bool(simplesprite.skipframes)

    props.has_sleep = simplesprite.sleep is not None
    props.sleep = simplesprite.sleep or 0

    props.has_current_frame = simplesprite.currentframe is not None
    props.current_frame = simplesprite.currentframe or 0

    props.frames.clear()

    nodes = simplesprite_node.nodes
    links = simplesprite_node.links

    group_output = nodes.new("NodeGroupOutput")
    group_output.location = (1400, 0)

    simplesprite_node.interface.new_socket(
        name="sRGB Texture",
        in_out='OUTPUT',
        socket_type="NodeSocketColor"
    )

    simplesprite_node.interface.new_socket(
        name="Alpha",
        in_out='OUTPUT',
        socket_type="NodeSocketFloat"
    )

    frame_nodes = []
    x_offset = 0

    for frame_data in simplesprite.frames:

        # -----------------------------
        # Create UI frame
        # -----------------------------
        frame = props.frames.add()
        frame.name = frame_data.frame
        frame.files.clear()

        for f in frame_data.files:

            raw = f.file
            file_entry = frame.files.add()
            file_entry.raw_string = raw

            if "," in raw:
                parts = raw.split(",", 3)

                file_entry.palette_index = int(parts[0].strip())
                file_entry.scale = float(parts[1].strip())
                file_entry.blend = float(parts[2].strip())

                filename = parts[3].strip()
                file_entry.texture_mode = 'TILED'

            elif raw.endswith("_LAYER"):
                filename = raw.replace("_LAYER", "")
                file_entry.texture_mode = 'LAYER'

            elif "_DETAIL_" in raw:
                base, detail = raw.split("_DETAIL_")
                filename = base
                file_entry.scale = float(detail)
                file_entry.texture_mode = 'DETAIL'

            elif raw.endswith("PAL.BMP"):
                filename = raw
                file_entry.texture_mode = 'PALETTE'

            else:
                filename = raw
                file_entry.texture_mode = 'BASE'

            image, err = load_texture(ctx, filename)
            if image:
                file_entry.image = image

        frame.numfiles = len(frame.files)

        # -----------------------------
        # Create frame nodegroup
        # -----------------------------
        frame_group = create_frame_nodegroup(
            ctx,
            frame,
            simplesprite.tag
        )

        frame.frame_node = frame_group

        # -----------------------------
        # Instance nodegroup
        # -----------------------------
        frame_node = nodes.new("ShaderNodeGroup")
        frame_node.node_tree = frame_group
        frame_node.location = (x_offset, 0)

        # Hide ALL inputs
        for socket in frame_node.inputs:
            socket.hide = True

        for i, file in enumerate(frame.files):
            if file.texture_mode == 'DETAIL' and i == 1:
                if "Detail Scale" in frame_node.inputs:
                    frame_node.inputs["Detail Scale"].default_value = file.scale
            if file.texture_mode == 'TILED':
                tiled_index = i - 1  # File 2 = Tiled 1
                socket_name = f"Tiled {tiled_index} Scale"
                if socket_name in frame_node.inputs:
                    frame_node.inputs[socket_name].default_value = file.scale

        frame_nodes.append(frame_node)
        x_offset += 400

    props.numframes = len(props.frames)

    if frame_nodes:
        links.new(
            frame_nodes[0].outputs["Color"],
            group_output.inputs["sRGB Texture"]
        )
        links.new(
            frame_nodes[0].outputs["Alpha"],
            group_output.inputs["Alpha"]
        )

    return ""