#material.py

from . import _add_group_socket, _get_group_io_sockets

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
