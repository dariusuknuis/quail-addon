# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportAttributeAccessIssue=false

import bpy
import struct
from ..wce.wce import wce
from ..wce.simplespritedef import simplespritedef
from .context import Context
from ..common.image_loader import load_s3d_image
from ..common import _add_group_socket, _get_group_io_sockets
from ..common import state

def read_bmp_palette_color(file_path, color_index):
    """
    Reads the color at the specified index from a BMP palette.

    :param file_path: The path to the BMP file.
    :param color_index: The index of the color in the BMP palette.
    :return: The RGB color as a tuple (red, green, blue).
    """

    print(f"\n=== BMP PALETTE DEBUG ===")
    print("File:", file_path)
    print("Requested index:", color_index)

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

def create_frame_nodegroup(ctx, frame, sprite_tag, force_rebuild=False):

    print(f"[FRAME GROUP] create_frame_nodegroup: {frame.frame_name} rebuild={force_rebuild}")

    group = bpy.data.node_groups.get(frame.frame_name)

    if group and not force_rebuild:
        return group

    if group and force_rebuild:
        group.nodes.clear()
        group.links.clear()
        group.interface.clear()
        print("group_clear")
    else:
        group = bpy.data.node_groups.new(frame.frame_name, 'ShaderNodeTree')
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
    base_image = bpy.data.images.get(base_file.image_name)

    base_tex = nodes.new("ShaderNodeTexImage")
    base_tex.location = (current_x, 0)
    base_tex["file_index"] = 0
    base_tex.name = base_file.file_name
    base_tex.label = base_tex.name
    if base_image:
        base_tex.image = base_image

    # ------------------------------------------------
    # DETAIL case
    # ------------------------------------------------
    if len(frame.files) > 1 and frame.files[1].texture_mode == 'DETAIL':
        group["mode"] = "DETAIL"

        detail_file = frame.files[1]
        detail_image = bpy.data.images.get(detail_file.image_name)

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
        detail_tex.location = (-600, -200)
        detail_tex["file_index"] = 1
        detail_tex.name = detail_file.file_name
        detail_tex.label = detail_tex.name
        if detail_image:
            detail_tex.image = detail_image

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
        group["mode"] = "LAYER"

        layer_file = frame.files[1]
        layer_image = bpy.data.images.get(layer_file.image_name)

        layer_tex = nodes.new("ShaderNodeTexImage")
        layer_tex.location = (-600, -150)
        layer_tex["file_index"] = 1
        layer_tex.name = layer_file.file_name
        layer_tex.label = layer_tex.name
        if layer_image:
            layer_tex.image = layer_image

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
        group["mode"] = "PALETTE"

        palette_file = frame.files[1]
        palette_image = bpy.data.images.get(palette_file.image_name)

        palette_tex = nodes.new("ShaderNodeTexImage")
        palette_tex.location = (-600, -150)
        palette_tex.location = (-1400, -1200)
        palette_tex["file_index"] = 1
        palette_tex.interpolation = 'Closest'
        palette_tex.name = palette_file.file_name
        palette_tex.label = palette_tex.name
        if palette_image:
            palette_tex.image = palette_image
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
            tiled_tex.location = (-1000, -400 - tiled_index * 300)
            tiled_tex["file_index"] = tiled_index + 2
            tiled_image = bpy.data.images.get(file.image_name)
            tiled_tex.name = file.file_name
            tiled_tex.label = tiled_tex.name
            if tiled_image:
                tiled_tex.image = tiled_image

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
            if palette_image and "bmp_palette" in palette_image:
                palette = palette_image["bmp_palette"]
                idx = max(0, file.palette_index - 1)
                if idx < len(palette):
                    r, g, b = palette[idx]
                    palette_color = (r / 255.0, g / 255.0, b / 255.0)
                else:
                    print(f"[WARN] Palette index out of range: {idx}")
                    palette_color = (0.0, 0.0, 0.0)

            else:
                print(f"[WARN] No palette on image: {palette_image.name if palette_image else 'None'}")
                palette_color = (0.0, 0.0, 0.0)

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
        if accumulated_color:
            links.new(accumulated_color, mix_node.inputs[7])
        else:
            links.new(base_tex.outputs["Color"], mix_node.inputs[7])
        links.new(mix_node.outputs[2], group_output.inputs["Color"])

        if "Alpha" in base_tex.outputs:
            links.new(base_tex.outputs["Alpha"], group_output.inputs["Alpha"])

    else:
        # No extra images → just base
        group["mode"] = "BASE"
        links.new(base_tex.outputs["Color"], group_output.inputs["Color"])
        if "Alpha" in base_tex.outputs:
            links.new(base_tex.outputs["Alpha"], group_output.inputs["Alpha"])

    current_x += 300

    return group

def build_texture_atlas(images, name="atlas", padding=2):
    if not images:
        return None

    # --------------------------------------------------
    # Determine target size (max of all images)
    # --------------------------------------------------
    valid_images = [img for img in images if img is not None]

    if not valid_images:
        return None

    max_w = max(img.size[0] for img in valid_images)
    max_h = max(img.size[1] for img in valid_images)

    count = len(images)

    atlas_width = count * (max_w + padding * 2)
    atlas_height = max_h + padding * 2

    # --------------------------------------------------
    # CREATE / REUSE / REPLACE IMAGE
    # --------------------------------------------------
    atlas = bpy.data.images.get(name)

    if atlas:
        if atlas.size[0] != atlas_width or atlas.size[1] != atlas_height:
            # Size mismatch → must replace

            if atlas.users > 0:
                # Safer: rename old instead of deleting
                atlas.name = name + "_old"
            else:
                bpy.data.images.remove(atlas)

            atlas = bpy.data.images.new(
                name,
                width=atlas_width,
                height=atlas_height,
                alpha=True
            )
        # else: same size → reuse (overwrite pixels below)
    else:
        atlas = bpy.data.images.new(
            name,
            width=atlas_width,
            height=atlas_height,
            alpha=True
        )

    atlas.alpha_mode = 'CHANNEL_PACKED'

    atlas_pixels = [0.0] * (atlas_width * atlas_height * 4)

    # --------------------------------------------------
    # Nearest-neighbor resample into target size
    # --------------------------------------------------
    def resample_to_size(img, target_w, target_h):
        src_w, src_h = img.size
        src_pixels = list(img.pixels)

        result = [0.0] * (target_w * target_h * 4)

        for y in range(target_h):
            sy = int(y * src_h / target_h)
            for x in range(target_w):
                sx = int(x * src_w / target_w)

                src_idx = (sy * src_w + sx) * 4
                dst_idx = (y * target_w + x) * 4

                result[dst_idx:dst_idx+4] = src_pixels[src_idx:src_idx+4]

        return result

    # --------------------------------------------------
    # Copy pixel helper
    # --------------------------------------------------
    def copy_pixel(src_pixels, sx, sy, sw, dx, dy, dw):
        src_index = (sy * sw + sx) * 4
        dst_index = (dy * dw + dx) * 4
        atlas_pixels[dst_index:dst_index+4] = src_pixels[src_index:src_index+4]

    # --------------------------------------------------
    # Build atlas
    # --------------------------------------------------
    for i, img in enumerate(images):

        if img:
            img_pixels = resample_to_size(img, max_w, max_h)
        else:
            img_pixels = [1.0, 0.0, 1.0, 1.0] * (max_w * max_h)

        x_offset = i * (max_w + padding * 2) + padding
        y_offset = padding

        # main copy
        for y in range(max_h):
            for x in range(max_w):
                copy_pixel(
                    img_pixels,
                    x, y, max_w,
                    x + x_offset,
                    y + y_offset,
                    atlas_width
                )

        # padding (edge bleed)
        for p in range(padding):
            for y in range(max_h):
                copy_pixel(img_pixels, 0, y, max_w,
                           x_offset - p - 1, y + y_offset, atlas_width)
                copy_pixel(img_pixels, max_w - 1, y, max_w,
                           x_offset + max_w + p, y + y_offset, atlas_width)

            for x in range(max_w):
                copy_pixel(img_pixels, x, 0, max_w,
                           x + x_offset, y_offset - p - 1, atlas_width)
                copy_pixel(img_pixels, x, max_h - 1, max_w,
                           x + x_offset, y_offset + max_h + p, atlas_width)

    # --------------------------------------------------
    # WRITE PIXELS (overwrite)
    # --------------------------------------------------
    atlas.pixels[:] = atlas_pixels
    atlas.update()

    # Optional: only pack once
    if not atlas.packed_file:
        atlas.pack()

    return atlas

def add_texture_animation(simplesprite_node):
    nodes = simplesprite_node.nodes
    links = simplesprite_node.links
    props = simplesprite_node.quail_simplesprite

    group_name = f"{simplesprite_node.name}_TEXANIM"

    # --------------------------------------------------
    # 1. COLLECT FRAME IMAGES
    # --------------------------------------------------
    frame_nodes = [
        n for n in nodes
        if n.type == 'GROUP'
        and n.node_tree
        and n.node_tree.get("quaildef") == "simplesprite_frame"
    ]

    frame_nodes.sort(key=lambda n: n.location.y, reverse=True)

    images = []
    for fn in frame_nodes:
        base = next(
            (n for n in fn.node_tree.nodes
            if n.type == 'TEX_IMAGE' and n.get("file_index") == 0),
            None
        )

        if base:
            images.append(base.image if base.image else None)
        else:
            images.append(None)

    if not images:
        return

    # --------------------------------------------------
    # 2. BUILD ATLAS
    # --------------------------------------------------
    atlas = build_texture_atlas(images, name=f"{simplesprite_node.name}_atlas")

    # for img in images:
    #     if img and not img.packed_file:
    #         try:
    #             img.reload()
    #         except:
    #             pass

    # --------------------------------------------------
    # 3. CREATE / RESET TEXANIM GROUP
    # --------------------------------------------------
    if group_name in bpy.data.node_groups:
        group = bpy.data.node_groups[group_name]
        group.nodes.clear()
        group.links.clear()
        group.interface.clear()
        print("tex_clear")
    else:
        group = bpy.data.node_groups.new(group_name, 'ShaderNodeTree')

    group['quaildef'] = 'simplesprite_texanim'

    gnodes = group.nodes
    glinks = group.links

    # --------------------------------------------------
    # 4. INTERFACE
    # --------------------------------------------------
    group.interface.new_socket("Color", in_out='OUTPUT', socket_type="NodeSocketColor")
    group.interface.new_socket("Alpha", in_out='OUTPUT', socket_type="NodeSocketFloat")

    g_output = gnodes.new("NodeGroupOutput")
    g_output.location = (800, 0)

    # --------------------------------------------------
    # 5. FRAME INDEX DRIVER (INSIDE GROUP)
    # --------------------------------------------------
    frame_value = gnodes.new("ShaderNodeValue")
    frame_value.name = "Frame_Index"
    frame_value.label = "Frame Index"
    frame_value.location = (-600, 200)
    frame_value.hide = True

    driver = frame_value.outputs[0].driver_add("default_value")
    drv = driver.driver

    drv.expression = "((frame - 1) // max(1, int((sleep * fps) / 1000))) % max(1, total)"

    for name, path, id_type, id_val in [
        ("frame", "frame_current", 'SCENE', bpy.context.scene),
        ("sleep", "quail_simplesprite.sleep", 'NODETREE', simplesprite_node),
        ("fps", "render.fps", 'SCENE', bpy.context.scene),
        ("total", "quail_simplesprite.numframes", 'NODETREE', simplesprite_node),
    ]:
        var = drv.variables.new()
        var.name = name
        var.targets[0].id_type = id_type
        var.targets[0].id = id_val
        var.targets[0].data_path = path

    # --------------------------------------------------
    # 6. IMAGE TEXTURE
    # --------------------------------------------------
    tex = gnodes.new("ShaderNodeTexImage")
    tex.image = atlas
    tex.extension = 'REPEAT'
    tex.location = (600, 0)

    # --------------------------------------------------
    # 7. UV PIPELINE
    # --------------------------------------------------
    coord = gnodes.new("ShaderNodeTexCoord")
    coord.location = (-1200, 0)

    mapping = gnodes.new("ShaderNodeMapping")
    mapping.location = (-1000, 0)

    glinks.new(coord.outputs["UV"], mapping.inputs["Vector"])

    sep = gnodes.new("ShaderNodeSeparateXYZ")
    sep.location = (-800, 0)
    glinks.new(mapping.outputs["Vector"], sep.inputs["Vector"])

    fract_x = gnodes.new("ShaderNodeMath")
    fract_x.operation = 'FRACT'
    fract_x.location = (-600, 150)

    fract_y = gnodes.new("ShaderNodeMath")
    fract_y.operation = 'FRACT'
    fract_y.location = (-600, -50)

    glinks.new(sep.outputs["X"], fract_x.inputs[0])
    glinks.new(sep.outputs["Y"], fract_y.inputs[0])

    scale = gnodes.new("ShaderNodeMath")
    scale.operation = 'DIVIDE'
    scale.inputs[1].default_value = props.numframes
    scale.location = (-400, 150)

    glinks.new(fract_x.outputs[0], scale.inputs[0])

    offset = gnodes.new("ShaderNodeMath")
    offset.operation = 'DIVIDE'
    offset.inputs[1].default_value = props.numframes
    offset.location = (-400, 0)

    glinks.new(frame_value.outputs[0], offset.inputs[0])

    add = gnodes.new("ShaderNodeMath")
    add.operation = 'ADD'
    add.location = (-200, 150)

    glinks.new(scale.outputs[0], add.inputs[0])
    glinks.new(offset.outputs[0], add.inputs[1])

    comb = gnodes.new("ShaderNodeCombineXYZ")
    comb.location = (0, 0)

    glinks.new(add.outputs[0], comb.inputs["X"])
    glinks.new(fract_y.outputs[0], comb.inputs["Y"])

    glinks.new(comb.outputs["Vector"], tex.inputs["Vector"])

    # --------------------------------------------------
    # 8. GROUP OUTPUT
    # --------------------------------------------------
    glinks.new(tex.outputs["Color"], g_output.inputs["Color"])
    glinks.new(tex.outputs["Alpha"], g_output.inputs["Alpha"])

    # --------------------------------------------------
    # 9. INSTANCE GROUP IN MAIN TREE
    # --------------------------------------------------
    for n in list(nodes):
        if n.get("texanim_node"):
            nodes.remove(n)

    texanim_node = nodes.new("ShaderNodeGroup")
    texanim_node.node_tree = group
    texanim_node.location = (600, 0)
    texanim_node["texanim_node"] = True

    # --------------------------------------------------
    # 10. CONNECT TO OUTPUT
    # --------------------------------------------------
    group_output = next(n for n in nodes if n.type == "GROUP_OUTPUT")

    for l in list(links):
        if l.to_node == group_output:
            links.remove(l)

    links.new(texanim_node.outputs["Color"], group_output.inputs["sRGB Texture"])
    links.new(texanim_node.outputs["Alpha"], group_output.inputs["Alpha"])

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
    y_offset = 0

    for frame_data in simplesprite.frames:

        # -----------------------------
        # Create UI frame
        # -----------------------------
        frame = props.frames.add()
        frame.frame_name = frame_data.frame
        frame.frame_id = len(props.frames) - 1
        frame.files.clear()

        for f in frame_data.files:

            raw = f.file
            file_entry = frame.files.add()
            file_entry.file_index = len(frame.files) - 1
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

            file_entry.file_name = filename
            image, err = load_s3d_image(ctx, filename)
            if image:
                file_entry.image_name = image.name

        frame.numfiles = len(frame.files)

        # -----------------------------
        # Create frame nodegroup
        # -----------------------------
        frame_group = create_frame_nodegroup(
            ctx,
            frame,
            simplesprite.tag,
            force_rebuild=False
        )

        frame.frame_node_name = frame_group.name

        # -----------------------------
        # Instance nodegroup
        # -----------------------------
        frame_node = nodes.new("ShaderNodeGroup")
        frame_node.node_tree = frame_group
        frame_node.location = (0, y_offset)
        frame_node["frame_id"] = frame.frame_id

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
        y_offset += -200

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

    if props.has_sleep:
        add_texture_animation(simplesprite_node)

    return ""