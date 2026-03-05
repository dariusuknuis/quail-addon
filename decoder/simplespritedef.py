# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportAttributeAccessIssue=false

import bpy
import struct
from ..wce.wce import wce
from ..wce.simplespritedef import simplespritedef
from .context import Context
from ..common.image_loader import load_texture
from ..common import _add_group_socket, _get_group_io_sockets

def read_bmp_palette_color(file_path, color_index):
    """
    Reads the color at the specified index from a BMP palette.

    :param file_path: The path to the BMP file.
    :param color_index: The index of the color in the BMP palette.
    :return: The RGB color as a tuple (red, green, blue).
    """
    with open(file_path, 'rb') as f:
        palette_offset = 54 + color_index * 4  # BMP header is 54 bytes + 4 bytes per color entry
        f.seek(palette_offset)
        palette_data = f.read(4)  # Read the color data (BGRX format)
        blue, green, red, _ = struct.unpack('BBBB', palette_data)
        return red / 255.0, green / 255.0, blue / 255.0

def create_palette_mask_node_group(palette_mask_node_group):
    """
    Creates the PaletteMask node group used for tiled textures.

    :param palette_mask_node_group: The node group to be populated.
    """
    nodes = palette_mask_node_group.nodes
    links = palette_mask_node_group.links

    nodes.clear()

    # ---- Create Interface Sockets (Blender 4/5 way, 3.6 safe via helper) ----
    _add_group_socket(palette_mask_node_group, "ClrPalette", "NodeSocketColor", True)
    _add_group_socket(palette_mask_node_group, "NdxClr", "NodeSocketColor", True)
    _add_group_socket(palette_mask_node_group, "Mix", "NodeSocketColor", True)
    _add_group_socket(palette_mask_node_group, "Texture", "NodeSocketColor", True)

    _add_group_socket(palette_mask_node_group, "Color", "NodeSocketColor", False)

    # ---- Get actual linkable IO sockets ----
    gi, go = _get_group_io_sockets(palette_mask_node_group)

    # ---- Create nodes ----
    separate_clr_palette = nodes.new(type='ShaderNodeSeparateColor')
    separate_clr_palette.location = (-400, 300)

    separate_ndx_clr = nodes.new(type='ShaderNodeSeparateColor')
    separate_ndx_clr.location = (-400, 100)

    less_than_red = nodes.new(type='ShaderNodeMath')
    less_than_red.operation = 'LESS_THAN'
    less_than_red.location = (-200, 300)

    greater_than_red = nodes.new(type='ShaderNodeMath')
    greater_than_red.operation = 'GREATER_THAN'
    greater_than_red.location = (-200, 250)

    less_than_green = nodes.new(type='ShaderNodeMath')
    less_than_green.operation = 'LESS_THAN'
    less_than_green.location = (-200, 200)

    greater_than_green = nodes.new(type='ShaderNodeMath')
    greater_than_green.operation = 'GREATER_THAN'
    greater_than_green.location = (-200, 150)

    less_than_blue = nodes.new(type='ShaderNodeMath')
    less_than_blue.operation = 'LESS_THAN'
    less_than_blue.location = (-200, 100)

    greater_than_blue = nodes.new(type='ShaderNodeMath')
    greater_than_blue.operation = 'GREATER_THAN'
    greater_than_blue.location = (-200, 50)

    # --- math offset nodes ---
    def _offset_math(op, y):
        n = nodes.new(type='ShaderNodeMath')
        n.operation = op
        n.location = (-400, y)
        n.inputs[1].default_value = 0.001
        return n

    add_red = _offset_math('ADD', -100)
    sub_red = _offset_math('SUBTRACT', -150)
    add_green = _offset_math('ADD', -200)
    sub_green = _offset_math('SUBTRACT', -250)
    add_blue = _offset_math('ADD', -300)
    sub_blue = _offset_math('SUBTRACT', -350)

    multiply_red = nodes.new(type='ShaderNodeMath')
    multiply_red.operation = 'MULTIPLY'
    multiply_red.location = (0, 300)

    multiply_green = nodes.new(type='ShaderNodeMath')
    multiply_green.operation = 'MULTIPLY'
    multiply_green.location = (0, 200)

    multiply_blue = nodes.new(type='ShaderNodeMath')
    multiply_blue.operation = 'MULTIPLY'
    multiply_blue.location = (0, 100)

    final_multiply = nodes.new(type='ShaderNodeMath')
    final_multiply.operation = 'MULTIPLY'
    final_multiply.location = (200, 200)

    final_multiply_2 = nodes.new(type='ShaderNodeMath')
    final_multiply_2.operation = 'MULTIPLY'
    final_multiply_2.location = (400, 100)

    mix_color = nodes.new(type='ShaderNodeMix')
    mix_color.data_type = 'RGBA'
    mix_color.location = (500, 0)

    # ---- Interface → nodes ----
    links.new(gi["ClrPalette"], separate_clr_palette.inputs["Color"])
    links.new(gi["NdxClr"], separate_ndx_clr.inputs["Color"])

    # Palette comparisons
    links.new(separate_clr_palette.outputs["Red"], less_than_red.inputs[0])
    links.new(separate_clr_palette.outputs["Red"], greater_than_red.inputs[0])
    links.new(separate_clr_palette.outputs["Green"], less_than_green.inputs[0])
    links.new(separate_clr_palette.outputs["Green"], greater_than_green.inputs[0])
    links.new(separate_clr_palette.outputs["Blue"], less_than_blue.inputs[0])
    links.new(separate_clr_palette.outputs["Blue"], greater_than_blue.inputs[0])

    # Index offsets
    links.new(separate_ndx_clr.outputs["Red"], add_red.inputs[0])
    links.new(separate_ndx_clr.outputs["Red"], sub_red.inputs[0])
    links.new(separate_ndx_clr.outputs["Green"], add_green.inputs[0])
    links.new(separate_ndx_clr.outputs["Green"], sub_green.inputs[0])
    links.new(separate_ndx_clr.outputs["Blue"], add_blue.inputs[0])
    links.new(separate_ndx_clr.outputs["Blue"], sub_blue.inputs[0])

    links.new(add_red.outputs["Value"], less_than_red.inputs[1])
    links.new(sub_red.outputs["Value"], greater_than_red.inputs[1])
    links.new(add_green.outputs["Value"], less_than_green.inputs[1])
    links.new(sub_green.outputs["Value"], greater_than_green.inputs[1])
    links.new(add_blue.outputs["Value"], less_than_blue.inputs[1])
    links.new(sub_blue.outputs["Value"], greater_than_blue.inputs[1])

    links.new(less_than_red.outputs["Value"], multiply_red.inputs[0])
    links.new(greater_than_red.outputs["Value"], multiply_red.inputs[1])
    links.new(less_than_green.outputs["Value"], multiply_green.inputs[0])
    links.new(greater_than_green.outputs["Value"], multiply_green.inputs[1])
    links.new(less_than_blue.outputs["Value"], multiply_blue.inputs[0])
    links.new(greater_than_blue.outputs["Value"], multiply_blue.inputs[1])

    links.new(multiply_red.outputs["Value"], final_multiply.inputs[0])
    links.new(multiply_green.outputs["Value"], final_multiply.inputs[1])
    links.new(final_multiply.outputs["Value"], final_multiply_2.inputs[0])
    links.new(multiply_blue.outputs["Value"], final_multiply_2.inputs[1])

    links.new(final_multiply_2.outputs["Value"], mix_color.inputs[0])

    links.new(gi["Mix"], mix_color.inputs[6])
    links.new(gi["Texture"], mix_color.inputs[7])

    # ---- Output ----
    links.new(mix_color.outputs[2], go["Color"])

def create_blur_node_group(blur_node_group):

    """
    Creates the Blur node group used for palette mask textures.

    :param blur_node_group: The node group to be populated.
    """

    nodes = blur_node_group.nodes
    links = blur_node_group.links

    # Clear existing nodes if recreating
    nodes.clear()

    # Add interface output socket (Vector)
    _add_group_socket(blur_node_group, "Vector", "NodeSocketVector", is_input=False)

    # Ensure Group Input / Output nodes exist and get real sockets
    _, go = _get_group_io_sockets(blur_node_group)

    # Create nodes
    tex_coord_node = nodes.new(type='ShaderNodeTexCoord')
    tex_coord_node.location = (-600, 0)

    add_vector_node = nodes.new(type='ShaderNodeVectorMath')
    add_vector_node.operation = 'ADD'
    add_vector_node.location = (0, 0)

    noise_texture_node = nodes.new(type='ShaderNodeTexWhiteNoise')
    noise_texture_node.location = (-400, -100)

    map_range_node = nodes.new(type='ShaderNodeMapRange')
    map_range_node.data_type = 'FLOAT_VECTOR'
    map_range_node.location = (-200, -100)

    value_node = nodes.new(type='ShaderNodeValue')
    value_node.location = (-800, -500)
    value_node.outputs[0].default_value = 0.005

    multiply_node = nodes.new(type='ShaderNodeMath')
    multiply_node.operation = 'MULTIPLY'
    multiply_node.location = (-600, -300)
    multiply_node.inputs[1].default_value = -1

    # --- Links ---

    links.new(tex_coord_node.outputs['UV'], add_vector_node.inputs[0])
    links.new(tex_coord_node.outputs['UV'], noise_texture_node.inputs['Vector'])
    links.new(noise_texture_node.outputs['Color'], map_range_node.inputs['Vector'])

    # Safe socket lookup
    to_max_vector_input = next(s for s in map_range_node.inputs if s.name == 'To Max' and s.type == 'VECTOR')
    to_min_vector_input = next(s for s in map_range_node.inputs if s.name == 'To Min' and s.type == 'VECTOR')

    links.new(value_node.outputs[0], to_max_vector_input)
    links.new(value_node.outputs[0], multiply_node.inputs[0])
    links.new(multiply_node.outputs[0], to_min_vector_input)

    links.new(map_range_node.outputs['Vector'], add_vector_node.inputs[1])

    # Output to group
    links.new(add_vector_node.outputs['Vector'], go["Vector"])

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

    # ------------------------------------------------
    # Palette Mask/Tiled case
    # ------------------------------------------------
    elif len(frame.files) > 1 and frame.files[1].texture_mode == 'PALETTE':

        palette_file = frame.files[1]
        palette_image = palette_file.image

        if not palette_image:
            return group

        palette_tex = nodes.new("ShaderNodeTexImage")
        palette_tex.image = palette_image
        palette_tex.location = (-600, -150)
        palette_tex.location = (-1400, -1200)
        palette_tex.interpolation = 'Closest'
        palette_tex.image.colorspace_settings.name = 'Non-Color'

        # Create or get the Blur node group
        blur_node_group_name = "Blur"
        if blur_node_group_name not in bpy.data.node_groups:
            blur_node_group = bpy.data.node_groups.new(name=blur_node_group_name, type='ShaderNodeTree')
            create_blur_node_group(blur_node_group)
        else:
            blur_node_group = bpy.data.node_groups[blur_node_group_name]

        blur_node = nodes.new(type='ShaderNodeGroup')
        blur_node.node_tree = blur_node_group
        blur_node.location = (-1600, -1200)

        # Connect the Blur node group to the palette mask texture
        links.new(blur_node.outputs[0], palette_tex.inputs['Vector'])

        palette_mask_group = bpy.data.node_groups.get("PaletteMask")
        if not palette_mask_group:
            palette_mask_group = bpy.data.node_groups.new("PaletteMask", 'ShaderNodeTree')
            create_palette_mask_node_group(palette_mask_group)

        accumulated_color = None

        tiled_index = 0

        for file in frame.files[2:]:

            if file.texture_mode != 'TILED':
                continue

            tiled_tex = nodes.new("ShaderNodeTexImage")
            tiled_tex.image = file.image
            tiled_tex.location = (-1000, -400 - tiled_index * 300)

            # Mapping
            multiply = nodes.new("ShaderNodeMath")
            multiply.operation = 'MULTIPLY'
            multiply.inputs[1].default_value = 10.0
            texcoord = nodes.new("ShaderNodeTexCoord")
            mapping = nodes.new("ShaderNodeMapping")

            multiply.location = (-1000, -400 - tiled_index * 300)
            texcoord.location = (-1300, -400 - tiled_index * 300)
            mapping.location = (-1150, -400 - tiled_index * 300)

            links.new(texcoord.outputs["UV"], mapping.inputs["Vector"])
            links.new(group_input.outputs[f"Tiled {tiled_index+1} Scale"], multiply.inputs[0])
            links.new(multiply.outputs[0], mapping.inputs["Scale"])
            links.new(mapping.outputs["Vector"], tiled_tex.inputs["Vector"])

            # Index color node
            index_color = nodes.new("ShaderNodeRGB")
            index_color.location = (-800, -400 - tiled_index * 300)

            # Set palette color (read from bmp like your old code)
            palette_color = read_bmp_palette_color(
                palette_image.filepath,
                (file.palette_index - 1)
            )
            index_color.outputs[0].default_value = (*palette_color, 1.0)

            # PaletteMask group node
            mask_node = nodes.new("ShaderNodeGroup")
            mask_node.node_tree = palette_mask_group
            mask_node.location = (-400, -400 - tiled_index * 300)

            links.new(palette_tex.outputs["Color"], mask_node.inputs["ClrPalette"])
            links.new(index_color.outputs["Color"], mask_node.inputs["NdxClr"])
            links.new(tiled_tex.outputs["Color"], mask_node.inputs["Texture"])

            if accumulated_color is not None:
                links.new(accumulated_color, mask_node.inputs["Mix"])

            # Update accumulated
            accumulated_color = mask_node.outputs[0]

            tiled_index += 1

        mix_node = nodes.new('ShaderNodeMix')
        mix_node.location = (1200, 670)
        mix_node.data_type = 'RGBA'
        mix_node.inputs[0].default_value = 0.5

        links.new(base_tex.outputs["Color"], mix_node.inputs[6])
        links.new(accumulated_color, mix_node.inputs[7])
        links.new(mix_node.outputs[2], group_output.inputs["Color"])

        if "Alpha" in base_tex.outputs:
            links.new(base_tex.outputs["Alpha"], group_output.inputs["Alpha"])

    else:
        # No extra images → just base
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