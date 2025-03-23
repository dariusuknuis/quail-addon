# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportAttributeAccessIssue=false

import bpy
from ..wce.wce import wce
from ..wce.materialdefinition import materialdefinition
from .context import Context

def decode_materialdefinition(ctx:Context, material:materialdefinition) -> str:
    if material.tag in bpy.data.materials:
        return ""
    mat = bpy.data.materials.new(material.tag)
    mat['quaildef'] = 'materialdefinition'
    mat.quail_materialdefinition.rendermethod = material.rendermethod
    mat.quail_materialdefinition.rgbpen = f"{material.rgbpen[0]} {material.rgbpen[1]} {material.rgbpen[2]}"
    mat.quail_materialdefinition.brightness = material.brightness
    mat.quail_materialdefinition.scaledambient = material.scaledambient
    mat.quail_materialdefinition.hexfiftyflags = material.hexfiftyflag == 1
    mat.quail_materialdefinition.doublesided = material.doublesided == 1

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
