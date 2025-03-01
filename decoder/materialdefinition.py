# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
from ..wce.wce import wce
from ..wce.materialdefinition import materialdefinition

def decode_materialdefinition(parser:wce, material:materialdefinition) -> str:
    if material.tag in bpy.data.materials:
        return ""
    mat = bpy.data.materials.new(material.tag)
    mat.use_nodes = True
    bsdf_index = 0
    node_position = (-350, 280)
    if mat.node_tree is None:
        return f"material {material.tag} has no node tree"


    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf is None:
        return f"material {material.tag} has no Principled BSDF node"
    tex_image = mat.node_tree.nodes.new('ShaderNodeTexImage')
    # tex_image.image = bpy.data.images.load(material.texture_path)
    mat.node_tree.links.new(bsdf.inputs['Base Color'], tex_image.outputs['Color'])
    return ""
