# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportAttributeAccessIssue=false

import bpy
from ..wce.wce import wce
from ..wce.simplespritedef import simplespritedef
from .context import Context
from ..common.image_loader import load_texture

def create_bmp_wrapper_node(nodes, links, image, x_offset):

    group_name = f"{image.name}_BMP"

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
    img_nc.image = image
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
    frame_group_name = f"{sprite_tag}_{frame.frame}"

    if frame_group_name in bpy.data.node_groups:
        return bpy.data.node_groups[frame_group_name]

    group = bpy.data.node_groups.new(frame_group_name, 'ShaderNodeTree')
    group['quaildef'] = 'simplesprite_frame'

    nodes = group.nodes
    links = group.links

    # Interface
    group.interface.new_socket("Color", in_out='OUTPUT', socket_type="NodeSocketColor")
    group.interface.new_socket("Alpha", in_out='OUTPUT', socket_type="NodeSocketFloat")

    group_output = nodes.new("NodeGroupOutput")
    group_output.location = (800, 0)

    current_x = 0

    for file_entry in frame.files:
        filename = file_entry.file

        # Load image
        err = load_texture(ctx, filename)
        if err:
            print(err)
            continue

        image = bpy.data.images.get(filename)
        if image is None:
            continue

        image_type = image.get("image_type", "OTHER")

        if image_type == "BMP":
            image_node = create_bmp_wrapper_node(nodes, links, image, current_x)
        else:
            image_node = nodes.new("ShaderNodeTexImage")
            image_node.image = image
            image_node.location = (current_x, 0)

        # Connect outputs
        links.new(image_node.outputs["Color"], group_output.inputs["Color"])

        if "Alpha" in image_node.outputs:
            links.new(image_node.outputs["Alpha"], group_output.inputs["Alpha"])

        current_x += 300

    return group

def decode_simplespritedef(ctx:Context, simplesprite:simplespritedef) -> str:
    if simplesprite.tag in bpy.data.node_groups:
        return ""
    simplesprite_node = bpy.data.node_groups.new(simplesprite.tag, 'ShaderNodeTree')
    simplesprite_node['quaildef'] = 'simplespritedef'

    nodes = simplesprite_node.nodes
    links = simplesprite_node.links

    group_output = nodes.new("NodeGroupOutput")
    group_output.location = (1428, 12)

    def add_output(name, socket_type):
        simplesprite_node.interface.new_socket(
            name=name,
            in_out='OUTPUT',
            socket_type=socket_type
        )

    add_output("sRGB Texture", "NodeSocketColor")
    add_output("Alpha", "NodeSocketFloat")

    out = group_output.inputs



    return ""