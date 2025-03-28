# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
from bpy.types import NodeTree
from ...wce import materialdefinition
# from .transparent import create_node_group_transparent, create_material_with_node_group_transparent
# from .solidfillambientgouraud1 import create_node_group_sfag1, create_material_with_node_group_sfag1
# from .texture5ambientgouraud1 import create_node_group_t5ag1, create_material_with_node_group_t5ag1
# from .texture5ambientgouraud2 import create_node_group_t5ag2, create_material_with_node_group_t5ag2

def node_generate(src_material: materialdefinition, texture_path:str, render_method:str) -> str:
    return ""
#     node_group_cache = {}

#     if render_method == 'SOLIDFILLAMBIENTGOURAUD1':
#         node_group = get_or_create_node_group('SOLIDFILLAMBIENTGOURAUD1', create_node_group_sfag1, node_group_cache)
#         mat = create_material_with_node_group_sfag1(src_material, node_group)
#     elif render_method == 'TEXTURE5AMBIENTGOURAUD1':
#         node_group = get_or_create_node_group('TEXTURE5AMBIENTGOURAUD1', create_node_group_t5ag1, node_group_cache)
#         mat = create_material_with_node_group_t5ag1(mat_name, texture_full_path, node_group)
#     elif render_method == 'TEXTURE5AMBIENTGOURAUD2':
#         node_group = get_or_create_node_group('TEXTURE5AMBIENTGOURAUD2', create_node_group_t5ag2, node_group_cache)
#         mat = create_material_with_node_group_t5ag2(mat_name, texture_full_path, node_group)
#     elif render_method == 'TRANSPARENT':
#         node_group = get_or_create_node_group('TRANSPARENT', create_node_group_transparent, node_group_cache)
#         mat = create_material_with_node_group_transparent(mat_name, node_group)
#     elif render_method == 'USERDEFINED_2':
#         node_group = get_or_create_node_group('USERDEFINED_2', create_node_group_ud02, node_group_cache)
#         mat = create_material_with_node_group_ud02(mat_name, texture_full_path, node_group)
#     elif render_method == 'USERDEFINED_6':
#         node_group = get_or_create_node_group('USERDEFINED_6', create_node_group_ud06, node_group_cache)
#         mat = create_material_with_node_group_ud06(mat_name, texture_full_path, node_group)
#     elif render_method == 'USERDEFINED_8':
#         node_group = get_or_create_node_group('USERDEFINED_8', create_node_group_ud08, node_group_cache, texture_full_path)
#         mat = create_material_with_node_group_ud08(mat_name, texture_full_path, node_group)
#     elif render_method == 'USERDEFINED_10':
#         node_group = get_or_create_node_group('USERDEFINED_10', create_node_group_ud10, node_group_cache)
#         mat = create_material_with_node_group_ud10(mat_name, texture_full_path, node_group)
#     elif render_method == 'USERDEFINED_11':
#         node_group = get_or_create_node_group('USERDEFINED_11', create_node_group_ud11, node_group_cache)
#         mat = create_material_with_node_group_ud11(mat_name, texture_full_path, node_group)
#     elif render_method == 'USERDEFINED_12':
#         node_group = get_or_create_node_group('USERDEFINED_12', create_node_group_ud12, node_group_cache)
#         mat = create_material_with_node_group_ud12(mat_name, texture_full_path, node_group)
#     elif render_method == 'USERDEFINED_17':
#         node_group = get_or_create_node_group('USERDEFINED_17', create_node_group_ud17, node_group_cache)
#         mat = create_material_with_node_group_ud17(mat_name, texture_full_path, node_group)
#     elif render_method == 'USERDEFINED_19':
#         node_group = get_or_create_node_group('USERDEFINED_19', create_node_group_ud19, node_group_cache)
#         mat = create_material_with_node_group_ud19(mat_name, texture_full_path, node_group)
#     elif render_method == 'USERDEFINED_20':
#         node_group = get_or_create_node_group('USERDEFINED_20', create_node_group_ud20, node_group_cache, texture_full_path)
#         mat = create_material_with_node_group_ud20(mat_name, texture_full_path, node_group)
#     elif render_method == 'USERDEFINED_21':
#         node_group = get_or_create_node_group('USERDEFINED_21', create_node_group_ud21, node_group_cache)
#         mat = create_material_with_node_group_ud21(mat_name, texture_full_path, node_group)
#     elif render_method == 'USERDEFINED_22':
#         node_group = get_or_create_node_group('USERDEFINED_22', create_node_group_ud22, node_group_cache)
#         mat = create_material_with_node_group_ud22(mat_name, texture_full_path, node_group)
#     elif render_method == 'USERDEFINED_24':
#         node_group = get_or_create_node_group('USERDEFINED_24', create_node_group_ud24, node_group_cache)
#         mat = create_material_with_node_group_ud24(mat_name, texture_full_path, node_group)
#     elif render_method == 'USERDEFINED_25':
#         node_group = get_or_create_node_group('USERDEFINED_25', create_node_group_ud25, node_group_cache)
#         mat = create_material_with_node_group_ud25(mat_name, texture_full_path, node_group)
#     elif render_method == 'USERDEFINED_26':
#         node_group = get_or_create_node_group('USERDEFINED_26', create_node_group_ud26, node_group_cache, texture_full_path)
#         mat = create_material_with_node_group_ud26(mat_name, texture_full_path, node_group)
#     else:
#         mat = bpy.data.materials.new(name=mat_name)
#         mat.use_nodes = True
#         bsdf = mat.node_tree.nodes.get('Principled BSDF')
#         if bsdf:
#             bsdf.inputs['Base Color'].default_value = (0.698, 0.698, 0.698, 0.0)


#     return ""



# def get_or_create_node_group(group_name, create_function, node_group_cache, texture_path=None) -> NodeTree:
#     """
#     Retrieves an existing node group or creates a new one if it doesn't exist.
#     """
#     if group_name in node_group_cache:
#         return node_group_cache[group_name]

#     if group_name in bpy.data.node_groups:
#         node_group = bpy.data.node_groups[group_name]
#     else:
#         if texture_path is not None:
#             node_group = create_function(texture_path)
#         else:
#             # If the function doesn't require texture_path, you can call it without arguments
#             node_group = create_function()

#     node_group_cache[group_name] = node_group
#     return node_group
