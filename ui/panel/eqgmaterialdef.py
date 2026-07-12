# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
from bpy.types import Material
import os
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty, EnumProperty, CollectionProperty
from ...logger.error import error

def eqg_apply(material:Material) -> str:
    if material is None:
        return "Material is None"
    if material['quaildef'] != 'eqgmaterialdef':
        return f"{material['quaildef']} is not a valid eqgmaterialdef"

    material.use_nodes = True

    for node in material.node_tree.nodes: # type: ignore
        material.node_tree.nodes.remove(node) # type: ignore

    # make Principled BSDF
    bsdf_node = material.node_tree.nodes.new("ShaderNodeBsdfPrincipled") # type: ignore
    bsdf_node.location = (0, 0)
    bsdf_node.label = "Principled BSDF"

    shadertag = material.quail_eqgmaterialdef.shadertag


    if is_shader_property(shadertag, "e_TextureDiffuse0") and material.quail_eqgmaterialdef.e_TextureDiffuse0:
        texture_path = material.quail_eqgmaterialdef.e_TextureDiffuse0
        image = bpy.data.images.get(texture_path, None)
        if image is None:
            try:
                image = bpy.data.images.load(texture_path)
            except Exception as e:
                return f"Error loading image {texture_path}: {e}"
            texture_path = os.path.basename(texture_path)
            material.quail_eqgmaterialdef.e_TextureDiffuse0 = texture_path
            print(f"Loaded image {texture_path}")

        texture_node = material.node_tree.nodes.new("ShaderNodeTexImage") # type: ignore
        texture_node.label = "Diffuse Texture"

        texture_node.image = image
        material.node_tree.links.new( # type: ignore
            texture_node.outputs["Color"],
            material.node_tree.nodes["Principled BSDF"].inputs["Base Color"] # type: ignore
        )
        texture_node.location = (-350, 280)

    if material.quail_eqgmaterialdef.e_TextureNormal0:
        texture_node = material.node_tree.nodes.new("ShaderNodeTexImage") # type: ignore
        texture_node.label = "Normal Texture"
        texture_path = material.quail_eqgmaterialdef.e_TextureNormal0
        image = bpy.data.images.get(texture_path, None)
        if image is None:
            try:
                image = bpy.data.images.load(texture_path)
            except Exception as e:
                return f"Error loading image {texture_path}: {e}"
            texture_path = os.path.basename(texture_path)
            material.quail_eqgmaterialdef.e_TextureNormal0 = texture_path
            print(f"Loaded image {texture_path}")

        texture_node.image = image

        normal_map = material.node_tree.nodes.new("ShaderNodeNormalMap")
        normal_map.label = "Normal Map"
        normal_map.location = (-250, 0)

        material.node_tree.links.new( # type: ignore
            texture_node.outputs["Color"],
            material.node_tree.nodes["Normal Map"].inputs["Color"] # type: ignore
        )

        material.node_tree.links.new( # type: ignore
            normal_map.outputs["Normal"],
            material.node_tree.nodes["Principled BSDF"].inputs["Normal"] # type: ignore
        )
        texture_node.location = (-550, 0)

    if is_shader_property(shadertag, "e_fBumpiness0") and material.quail_eqgmaterialdef.e_fBumpiness0:
        bump_node = material.node_tree.nodes.new("ShaderNodeBump") # type: ignore
        bump_node.label = "Bump"
        bump_node.inputs["Strength"].default_value = material.quail_eqgmaterialdef.e_fBumpiness0
        bump_node.location = (-150, 0)
        material.node_tree.links.new( # type: ignore
            material.node_tree.nodes["Normal Map"].outputs["Normal"], # type: ignore
            bump_node.inputs["Height"]
        )
        material.node_tree.links.new( # type: ignore
            bump_node.outputs["Normal"],
            material.node_tree.nodes["Principled BSDF"].inputs["Normal"] # type: ignore
        )

    if is_shader_property(shadertag, "e_fShininess0") and material.quail_eqgmaterialdef.e_fShininess0:
        bsdf_node.inputs["Specular IOR Level"].default_value = material.quail_eqgmaterialdef.e_fShininess0/128.0

    if is_shader_property(shadertag, "e_fGloss0") and material.quail_eqgmaterialdef.e_fGloss0:
        bsdf_node.inputs["Roughness"].default_value = float(material.quail_eqgmaterialdef.e_fGloss0)

    if is_shader_property(shadertag, "e_fReflectionColor") and material.quail_eqgmaterialdef.e_fReflectionColor:
        bsdf_node.inputs["Metallic"].default_value = float(material.quail_eqgmaterialdef.e_fReflectionColor)

    # link bsdf to material output node

    material_output_node = material.node_tree.nodes.new("ShaderNodeOutputMaterial") # type: ignore
    material_output_node.location = (300, 0)
    material.node_tree.links.new( # type: ignore
        bsdf_node.outputs["BSDF"],
        material_output_node.inputs["Surface"] # type: ignore
    )


    return ""


# Define Actor properties
class QuailEqgMaterialDefinitionProperties(bpy.types.PropertyGroup):

    def update_shader(self, context):
        """Update material shader when shadertag changes"""
        # Find the material owning this property group
        material = None
        for mat in bpy.data.materials:
            if hasattr(mat, 'quail_eqgmaterialdef') and mat.quail_eqgmaterialdef == self:
                material = mat
                break

        if material is None:
            return

        err = eqg_apply(material)
        if err:
            error(err)
            return

        # Force UI redraw
        for area in context.screen.areas:
            if area.type == 'PROPERTIES':
                area.tag_redraw()

    shadertag: EnumProperty(
        name="Shader",
        description="Shader",
        items=[
            ('AddAlpha_MaxC1.fx', 'AddAlpha_MaxC1.fx', ""),
            ('AddAlpha_MaxCB1.fx', 'AddAlpha_MaxCB1.fx', ""),
            ('AddAlpha_MaxCBSG1.fx', 'AddAlpha_MaxCBSG1.fx', ""),
            ('AddAlpha_MaxCG1.fx', 'AddAlpha_MaxCG1.fx', ""),
            ('AddAlpha_MPLBasicA.fx', 'AddAlpha_MPLBasicA.fx', ""),
            ('AddAlpha_MPLBasicAT.fx', 'AddAlpha_MPLBasicAT.fx', ""),
            ('AddAlpha_MPLBumpA.fx', 'AddAlpha_MPLBumpA.fx', ""),
            ('AddAlphaC1Max.fx', 'AddAlphaC1Max.fx', ""),
            ('Alpha_MaxC1.fx', 'Alpha_MaxC1.fx', ""),
            ('Alpha_MaxCB1.fx', 'Alpha_MaxCB1.fx', ""),
            ('Alpha_MaxCBS1.fx', 'Alpha_MaxCBS1.fx', ""),
            ('Alpha_MaxCBSG1.fx', 'Alpha_MaxCBSG1.fx', ""),
            ('Alpha_MaxCBSGE1.fx', 'Alpha_MaxCBSGE1.fx', ""),
            ('Alpha_MaxCE1.fx', 'Alpha_MaxCE1.fx', ""),
            ('Alpha_MPLBasicA.fx', 'Alpha_MPLBasicA.fx', ""),
            ('Alpha_MPLBasicAT.fx', 'Alpha_MPLBasicAT.fx', ""),
            ('Alpha_MPLBumpA.fx', 'Alpha_MPLBumpA.fx', ""),
            ('Alpha_MPLBumpAT.fx', 'Alpha_MPLBumpAT.fx', ""),
            ('AlphaRegionCE1Max.fx', 'AlphaRegionCE1Max.fx', ""),
            ('AlphaSModelC1Max.fx', 'AlphaSModelC1Max.fx', ""),
            ('AlphaSModelCB1Max.fx', 'AlphaSModelCB1Max.fx', ""),
            ('AlphaSModelCBGG1Max.fx', 'AlphaSModelCBGG1Max.fx', ""),
            ('Chroma_MaxC1.fx', 'Chroma_MaxC1.fx', ""),
            ('Chroma_MaxCB1.fx', 'Chroma_MaxCB1.fx', ""),
            ('Chroma_MaxCBS1.fx', 'Chroma_MaxCBS1.fx', ""),
            ('Chroma_MaxCBSG1.fx', 'Chroma_MaxCBSG1.fx', ""),
            ('Chroma_MaxCBSGE1.fx', 'Chroma_MaxCBSGE1.fx', ""),
            ('Chroma_MPLBasicA.fx', 'Chroma_MPLBasicA.fx', ""),
            ('Chroma_MPLBasicAT.fx', 'Chroma_MPLBasicAT.fx', ""),
            ('Chroma_MPLBumpA.fx', 'Chroma_MPLBumpA.fx', ""),
            ('Chroma_MPLBumpAT.fx', 'Chroma_MPLBumpAT.fx', ""),
            ('Chroma_MPLGBAT.fx', 'Chroma_MPLGBAT.fx', ""),
            ('Opaque_AddAlphaC1Max.fx', 'Opaque_AddAlphaC1Max.fx', ""),
            ('Opaque_Default.fx', 'Opaque_Default.fx', ""),
            ('Opaque_MaxC1_2UV.fx', 'Opaque_MaxC1_2UV.fx', ""),
            ('Opaque_MaxC1.fx', 'Opaque_MaxC1.fx', ""),
            ('Opaque_MaxC1DTP.fx', 'Opaque_MaxC1DTP.fx', ""),
            ('Opaque_MaxCB1_2UV.fx', 'Opaque_MaxCB1_2UV.fx', ""),
            ('Opaque_MaxCB1.fx', 'Opaque_MaxCB1.fx', ""),
            ('Opaque_MaxCBE1.fx', 'Opaque_MaxCBE1.fx', ""),
            ('Opaque_MaxCBS_2UV.fx', 'Opaque_MaxCBS_2UV.fx', ""),
            ('Opaque_MaxCBS1.fx', 'Opaque_MaxCBS1.fx', ""),
            ('Opaque_MaxCBSE1.fx', 'Opaque_MaxCBSE1.fx', ""),
            ('Opaque_MaxCBSG1_2UV.fx', 'Opaque_MaxCBSG1_2UV.fx', ""),
            ('Opaque_MaxCBSG1.fx', 'Opaque_MaxCBSG1.fx', ""),
            ('Opaque_MaxCBSGE1.fx', 'Opaque_MaxCBSGE1.fx', ""),
            ('Opaque_MaxCBST2_2UV.fx', 'Opaque_MaxCBST2_2UV.fx', ""),
            ('Opaque_MaxCE1.fx', 'Opaque_MaxCE1.fx', ""),
            ('Opaque_MaxCG1.fx', 'Opaque_MaxCG1.fx', ""),
            ('Opaque_MaxCSG1.fx', 'Opaque_MaxCSG1.fx', ""),
            ('Opaque_MaxLava.fx', 'Opaque_MaxLava.fx', ""),
            ('Opaque_MaxLava2.fx', 'Opaque_MaxLava2.fx', ""),
            ('Opaque_MaxSMLava2.fx', 'Opaque_MaxSMLava2.fx', ""),
            ('Opaque_MaxTerrain.fx', 'Opaque_MaxTerrain.fx', ""),
            ('Opaque_MaxWater.fx', 'Opaque_MaxWater.fx', ""),
            ('Opaque_MaxWaterFall.fx', 'Opaque_MaxWaterFall.fx', ""),
            ('Opaque_MPLBasic.fx', 'Opaque_MPLBasic.fx', ""),
            ('Opaque_MPLBasicA.fx', 'Opaque_MPLBasicA.fx', ""),
            ('Opaque_MPLBasicAT.fx', 'Opaque_MPLBasicAT.fx', ""),
            ('Opaque_MPLBlend.fx', 'Opaque_MPLBlend.fx', ""),
            ('Opaque_MPLBlendNoBump.fx', 'Opaque_MPLBlendNoBump.fx', ""),
            ('Opaque_MPLBump.fx', 'Opaque_MPLBump.fx', ""),
            ('Opaque_MPLBump2UV.fx', 'Opaque_MPLBump2UV.fx', ""),
            ('Opaque_MPLBumpA.fx', 'Opaque_MPLBumpA.fx', ""),
            ('Opaque_MPLBumpAT.fx', 'Opaque_MPLBumpAT.fx', ""),
            ('Opaque_MPLFull.fx', 'Opaque_MPLFull.fx', ""),
            ('Opaque_MPLFull2UV.fx', 'Opaque_MPLFull2UV.fx', ""),
            ('Opaque_MPLGB.fx', 'Opaque_MPLGB.fx', ""),
            ('Opaque_MPLGB2UV.fx', 'Opaque_MPLGB2UV.fx', ""),
            ('Opaque_MPLRB.fx', 'Opaque_MPLRB.fx', ""),
            ('Opaque_MPLRB2UV.fx', 'Opaque_MPLRB2UV.fx', ""),
            ('Opaque_MPLSB.fx', 'Opaque_MPLSB.fx', ""),
            ('Opaque_MPLSB2UV.fx', 'Opaque_MPLSB2UV.fx', ""),
            ('Opaque_OpaqueRegionCB1Max.fx', 'Opaque_OpaqueRegionCB1Max.fx', ""),
            ('Opaque_OpaqueRegionCBGG1Max.fx', 'Opaque_OpaqueRegionCBGG1Max.fx', ""),
            ('Opaque_OpaqueSkinMeshCBGG1Max.fx', 'Opaque_OpaqueSkinMeshCBGG1Max.fx', ""),
            ('Opaque_OpaqueSkinMeshCBGGE1Max.fx', 'Opaque_OpaqueSkinMeshCBGGE1Max.fx', ""),
            ('Opaque_OpaqueSModelC1Max.fx', 'Opaque_OpaqueSModelC1Max.fx', ""),
            ('Opaque_OpaqueSModelCB1Max.fx', 'Opaque_OpaqueSModelCB1Max.fx', ""),
            ('Opaque_OpaqueSModelCBGG1Max.fx', 'Opaque_OpaqueSModelCBGG1Max.fx', ""),
            ('Opaque_OpaqueSModelCG1Max.fx', 'Opaque_OpaqueSModelCG1Max.fx', ""),
            ('OpaqueRegionC1DTPMax.fx', 'OpaqueRegionC1DTPMax.fx', ""),
            ('OpaqueRegionC1Max.fx', 'OpaqueRegionC1Max.fx', ""),
            ('OpaqueRegionCB1Max.fx', 'OpaqueRegionCB1Max.fx', ""),
            ('OpaqueRegionCBGG1Max.fx', 'OpaqueRegionCBGG1Max.fx', ""),
            ('OpaqueRegionCE1Max.fx', 'OpaqueRegionCE1Max.fx', ""),
            ('OpaqueSModelCB1Max.fx', 'OpaqueSModelCB1Max.fx', ""),
            ('OpaqueSModelCBGG1Max.fx', 'OpaqueSModelCBGG1Max.fx', ""),
            ('OpaqueSModelCG1Max.fx', 'OpaqueSModelCG1Max.fx', ""),
        ],
        default='Opaque_MaxCB1.fx',
        update=update_shader
    )

    e_fShininess0: FloatProperty(
        name="e_fShininess0",
        description="Shininess",
        default=0,
        update=update_shader
    )

    e_TextureDiffuse0: StringProperty(
        name="e_TextureDiffuse0",
        description="Diffuse Texture",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureDiffuse0mapChannel: StringProperty(
        name="e_TextureDiffuse0mapChannel",
        description="Diffuse Texture Map Channel",
        default="",
        update=update_shader
    )

    e_TextureDiffuse1: StringProperty(
        name="e_TextureDiffuse1",
        description="Diffuse Texture 1",
        default="",
        update=update_shader
    )

    e_TextureEnvironment: StringProperty(
        name="e_TextureEnvironment",
        description="Environment Texture",
        default="",
        update=update_shader
    )

    e_TextureEnvironment0: StringProperty(
        name="e_TextureEnvironment0",
        description="Environment Texture 0",
        default="",
        update=update_shader
    )

    e_TextureFallback: StringProperty(
        name="e_TextureFallback",
        description="Fallback Texture",
        default="",
        update=update_shader
    )

    e_TextureFallback0: StringProperty(
        name="e_TextureFallback0",
        description="Fallback Texture 0",
        default="",
        update=update_shader
    )

    e_TextureNormal0: StringProperty(
        name="e_TextureNormal0",
        description="Normal Texture",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureNormal0mapChannel: StringProperty(
        name="e_TextureNormal0mapChannel",
        description="Normal Texture Map Channel",
        default="",
        update=update_shader
    )

    e_TextureNormal1: StringProperty(
        name="e_TextureNormal1",
        description="Normal Texture 1",
        default="",
        update=update_shader
    )

    e_fBumpiness0: StringProperty(
        name="e_fBumpiness0",
        description="Bumpiness",
        default="",
        update=update_shader
    )

    e_fCoverageScale0: StringProperty(
        name="e_fCoverageScale0",
        description="Coverage Scale",
        default="",
        update=update_shader
    )

    e_fEnvMapStrength0: StringProperty(
        name="e_fEnvMapStrength0",
        description="Env Map Strength",
        default="",
        update=update_shader
    )
    e_fFresnelBias: StringProperty(
        name="e_fFresnelBias",
        description="Fresnel Bias",
        default="",
        update=update_shader
    )

    e_fFresnelPower: StringProperty(
        name="e_fFresnelPower",
        description="Fresnel Power",
        default="",
        update=update_shader
    )

    e_fGloss0: StringProperty(
        name="e_fGloss0",
        description="Gloss",
        default="",
        update=update_shader
    )

    e_fGrassDensity0: StringProperty(
        name="e_fGrassDensity0",
        description="Grass Density 0",
        default="",
        update=update_shader
    )

    e_fGrassDensity1: StringProperty(
        name="e_fGrassDensity1",
        description="Grass Density 1",
        default="",
        update=update_shader
    )

    e_fGrassDensity2: StringProperty(
        name="e_fGrassDensity2",
        description="Grass Density 2",
        default="",
        update=update_shader
    )

    e_fGrassDensity3: StringProperty(
        name="e_fGrassDensity3",
        description="Grass Density 3",
        default="",
        update=update_shader
    )

    e_fGrassDensity4: StringProperty(
        name="e_fGrassDensity4",
        description="Grass Density 4",
        default="",
        update=update_shader
    )

    e_fGrassDensity5: StringProperty(
        name="e_fGrassDensity5",
        description="Grass Density 5",
        default="",
        update=update_shader
    )

    e_fGrassDensity6: StringProperty(
        name="e_fGrassDensity6",
        description="Grass Density 6",
        default="",
        update=update_shader
    )

    e_fGrassDensity7: StringProperty(
        name="e_fGrassDensity7",
        description="Grass Density 7",
        default="",
        update=update_shader
    )

    e_fGrassDensity8: StringProperty(
        name="e_fGrassDensity8",
        description="Grass Density 8",
        default="",
        update=update_shader
    )

    e_fGrassDensity9: StringProperty(
        name="e_fGrassDensity9",
        description="Grass Density 9",
        default="",
        update=update_shader
    )

    e_fReflectionAmount: StringProperty(
        name="e_fReflectionAmount",
        description="Reflection Amount",
        default="",
        update=update_shader
    )

    e_fReflectionColor: StringProperty(
        name="e_fReflectionColor",
        description="Reflection Color",
        default="",
        update=update_shader
    )

    e_fScale0: StringProperty(
        name="e_fScale0",
        description="Scale 0",
        default="",
        update=update_shader
    )

    e_fScale1: StringProperty(
        name="e_fScale1",
        description="Scale 1",
        default="",
        update=update_shader
    )

    e_fScale2: StringProperty(
        name="e_fScale2",
        description="Scale 2",
        default="",
        update=update_shader
    )

    e_fScale3: StringProperty(
        name="e_fScale3",
        description="Scale 3",
        default="",
        update=update_shader
    )

    e_fScale4: StringProperty(
        name="e_fScale4",
        description="Scale 4",
        default="",
        update=update_shader
    )

    e_fScale5: StringProperty(
        name="e_fScale5",
        description="Scale 5",
        default="",
        update=update_shader
    )

    e_fScale6: StringProperty(
        name="e_fScale6",
        description="Scale 6",
        default="",
        update=update_shader
    )

    e_fScale7: StringProperty(
        name="e_fScale7",
        description="Scale 7",
        default="",
        update=update_shader
    )

    e_fScale8: StringProperty(
        name="e_fScale8",
        description="Scale 8",
        default="",
        update=update_shader
    )

    e_fScale9: StringProperty(
        name="e_fScale9",
        description="Scale 9",
        default="",
        update=update_shader
    )

    e_fSlide1X: StringProperty(
        name="e_fSlide1X",
        description="Slide 1 X",
        default="",
        update=update_shader
    )

    e_fSlide1Y: StringProperty(
        name="e_fSlide1Y",
        description="Slide 1 Y",
        default="",
        update=update_shader
    )

    e_fSlide2X: StringProperty(
        name="e_fSlide2X",
        description="Slide 2 X",
        default="",
        update=update_shader
    )

    e_fSlide2Y: StringProperty(
        name="e_fSlide2Y",
        description="Slide 2 Y",
        default="",
        update=update_shader
    )

    e_fWaterColor1: StringProperty(
        name="e_fWaterColor1",
        description="Water Color 1",
        default="",
        update=update_shader
    )

    e_fWaterColor2: StringProperty(
        name="e_fWaterColor2",
        description="Water Color 2",
        default="",
        update=update_shader
    )

    e_TextureCoverage: StringProperty(
        name="e_TextureCoverage",
        description="Coverage Texture",
        default="",
        update=update_shader
    )

    e_TextureCoverage0: StringProperty(
        name="e_TextureCoverage0",
        description="Coverage Texture 0",
        default="",
        update=update_shader
    )

    e_TextureDetail0: StringProperty(
        name="e_TextureDetail0",
        description="Detail Texture 0",
        default="",
        update=update_shader
    )

    e_TextureDetail1: StringProperty(
        name="e_TextureDetail1",
        description="Detail Texture 1",
        default="",
        update=update_shader
    )

    e_TextureDetail2: StringProperty(
        name="e_TextureDetail2",
        description="Detail Texture 2",
        default="",
        update=update_shader
    )

    e_TextureDetail3: StringProperty(
        name="e_TextureDetail3",
        description="Detail Texture 3",
        default="",
        update=update_shader
    )

    e_TextureDetail4: StringProperty(
        name="e_TextureDetail4",
        description="Detail Texture 4",
        default="",
        update=update_shader
    )

    e_TextureDetail5: StringProperty(
        name="e_TextureDetail5",
        description="Detail Texture 5",
        default="",
        update=update_shader
    )

    e_TextureDetail6: StringProperty(
        name="e_TextureDetail6",
        description="Detail Texture 6",
        default="",
        update=update_shader
    )

    e_TextureDetail7: StringProperty(
        name="e_TextureDetail7",
        description="Detail Texture 7",
        default="",
        update=update_shader
    )

    e_TextureDetail8: StringProperty(
        name="e_TextureDetail8",
        description="Detail Texture 8",
        default="",
        update=update_shader
    )

    e_TextureDetail9: StringProperty(
        name="e_TextureDetail9",
        description="Detail Texture 9",
        default="",
        update=update_shader
    )

    e_TextureGlow0: StringProperty(
        name="e_TextureGlow0",
        description="Glow Texture 0",
        default="",
        update=update_shader
    )

    e_TexturePalette0: StringProperty(
        name="e_TexturePalette0",
        description="Palette Texture 0",
        default="",
        update=update_shader
    )

    e_TextureSecond0: StringProperty(
        name="e_TextureSecond0",
        description="Second Texture 0",
        default="",
        update=update_shader
    )

    e_TextureSecond0mapChannel: StringProperty(
        name="e_TextureSecond0mapChannel",
        description="Second Texture 0 Map Channel",
        default="",
        update=update_shader
    )

    animsleep: IntProperty(
        name="Anim Sleep",
        description="Anim Sleep",
        default=0
    )

def draw_eqgmaterialdefinition_in_transform(self, context):
    obj = context.object
    if not obj or not obj.active_material:
        return

    material = obj.active_material
    if not material.get('quaildef') == 'eqgmaterialdef':
        return

    layout = self.layout
    box = layout.box()
    box.label(text="EQGMATERIALDEF")

    row = box.row()
    row.prop(material.quail_eqgmaterialdef, "shadertag")

    shadertag = material.quail_eqgmaterialdef.shadertag
    if is_shader_property(shadertag, "e_fShininess0"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fShininess0")
    if is_shader_property(shadertag, "e_TextureDiffuse0"):
        row = box.row(align=True)
        row.label(text="Diffuse0:")
        row.prop(material.quail_eqgmaterialdef, "e_TextureDiffuse0", text="")
    if is_shader_property(shadertag, "e_TextureDiffuse0mapChannel"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureDiffuse0mapChannel")
    if is_shader_property(shadertag, "e_TextureDiffuse1"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureDiffuse1")
    if is_shader_property(shadertag, "e_TextureEnvironment"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureEnvironment")
    if is_shader_property(shadertag, "e_TextureEnvironment0"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureEnvironment0")
    if is_shader_property(shadertag, "e_TextureFallback"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureFallback")
    if is_shader_property(shadertag, "e_TextureFallback0"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureFallback0")
    if is_shader_property(shadertag, "e_TextureNormal0"):
        row = box.row(align=True)
        row.label(text="Normal0:")
        row.prop(material.quail_eqgmaterialdef, "e_TextureNormal0", text="")
    if is_shader_property(shadertag, "e_TextureNormal0mapChannel"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureNormal0mapChannel")
    if is_shader_property(shadertag, "e_TextureNormal1"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureNormal1")
    if is_shader_property(shadertag, "e_fBumpiness0"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fBumpiness0")
    if is_shader_property(shadertag, "e_fCoverageScale0"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fCoverageScale0")
    if is_shader_property(shadertag, "e_fEnvMapStrength0"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fEnvMapStrength0")
    if is_shader_property(shadertag, "e_fFresnelBias"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fFresnelBias")
    if is_shader_property(shadertag, "e_fFresnelPower"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fFresnelPower")
    if is_shader_property(shadertag, "e_fGloss0"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fGloss0")
    if is_shader_property(shadertag, "e_fGrassDensity0"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fGrassDensity0")
    if is_shader_property(shadertag, "e_fGrassDensity1"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fGrassDensity1")
    if is_shader_property(shadertag, "e_fGrassDensity2"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fGrassDensity2")
    if is_shader_property(shadertag, "e_fGrassDensity3"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fGrassDensity3")
    if is_shader_property(shadertag, "e_fGrassDensity4"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fGrassDensity4")
    if is_shader_property(shadertag, "e_fGrassDensity5"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fGrassDensity5")
    if is_shader_property(shadertag, "e_fGrassDensity6"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fGrassDensity6")
    if is_shader_property(shadertag, "e_fGrassDensity7"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fGrassDensity7")
    if is_shader_property(shadertag, "e_fGrassDensity8"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fGrassDensity8")
    if is_shader_property(shadertag, "e_fGrassDensity9"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fGrassDensity9")
    if is_shader_property(shadertag, "e_fReflectionAmount"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fReflectionAmount")
    if is_shader_property(shadertag, "e_fReflectionColor"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fReflectionColor")
    if is_shader_property(shadertag, "e_fScale0"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fScale0")
    if is_shader_property(shadertag, "e_fScale1"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fScale1")
    if is_shader_property(shadertag, "e_fScale2"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fScale2")
    if is_shader_property(shadertag, "e_fScale3"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fScale3")
    if is_shader_property(shadertag, "e_fScale4"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fScale4")
    if is_shader_property(shadertag, "e_fScale5"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fScale5")
    if is_shader_property(shadertag, "e_fScale6"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fScale6")
    if is_shader_property(shadertag, "e_fScale7"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fScale7")
    if is_shader_property(shadertag, "e_fScale8"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fScale8")
    if is_shader_property(shadertag, "e_fScale9"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fScale9")
    if is_shader_property(shadertag, "e_fSlide1X"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fSlide1X")
    if is_shader_property(shadertag, "e_fSlide1Y"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fSlide1Y")
    if is_shader_property(shadertag, "e_fSlide2X"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fSlide2X")
    if is_shader_property(shadertag, "e_fSlide2Y"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fSlide2Y")
    if is_shader_property(shadertag, "e_fWaterColor1"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fWaterColor1")
    if is_shader_property(shadertag, "e_fWaterColor2"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_fWaterColor2")
    if is_shader_property(shadertag, "e_TextureCoverage"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureCoverage")
    if is_shader_property(shadertag, "e_TextureCoverage0"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureCoverage0")
    if is_shader_property(shadertag, "e_TextureDetail0"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureDetail0")
    if is_shader_property(shadertag, "e_TextureDetail1"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureDetail1")
    if is_shader_property(shadertag, "e_TextureDetail2"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureDetail2")
    if is_shader_property(shadertag, "e_TextureDetail3"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureDetail3")
    if is_shader_property(shadertag, "e_TextureDetail4"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureDetail4")
    if is_shader_property(shadertag, "e_TextureDetail5"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureDetail5")
    if is_shader_property(shadertag, "e_TextureDetail6"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureDetail6")
    if is_shader_property(shadertag, "e_TextureDetail7"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureDetail7")
    if is_shader_property(shadertag, "e_TextureDetail8"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureDetail8")
    if is_shader_property(shadertag, "e_TextureDetail9"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureDetail9")
    if is_shader_property(shadertag, "e_TextureGlow0"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureGlow0")
    if is_shader_property(shadertag, "e_TexturePalette0"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TexturePalette0")
    if is_shader_property(shadertag, "e_TextureSecond0"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureSecond0")
    if is_shader_property(shadertag, "e_TextureSecond0mapChannel"):
        row = box.row()
        row.prop(material.quail_eqgmaterialdef, "e_TextureSecond0mapChannel")

    row = box.row()
    row.prop(material.quail_eqgmaterialdef, "animsleep")

def is_shader_property(shader:str, property:str):
    if shader == 'Opaque_MaxCBSG1.fx' and (property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'Alpha_MPLBasicAT.fx' and (property == 'e_TextureDiffuse0' or property == 'e_fShininess0' or property == 'e_TextureFallback0'):
        return True
    if shader == 'Opaque_MPLRB.fx' and (property == 'e_TextureNormal0' or property == 'e_TextureCoverage0' or property == 'e_TextureEnvironment0' or property == 'e_fEnvMapStrength0' or property == 'e_fShininess0' or property == 'e_fCoverageScale0' or property == 'e_TextureDiffuse0'):
        return True
    if shader == 'Opaque_MaxCB1_2UV.fx' and (property == 'e_TextureNormal0mapChannel' or property == 'e_TextureSecond0mapChannel' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureSecond0' or property == 'e_TextureDiffuse0mapChannel'):
        return True
    if shader == 'Opaque_MPLRB2UV.fx' and (property == 'e_fEnvMapStrength0' or property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0' or property == 'e_TextureEnvironment0'):
        return True
    if shader == 'Alpha_MPLBasicA.fx' and (property == 'e_fShininess0' or property == 'e_TextureFallback0' or property == 'e_fCoverageScale0' or property == 'e_TextureCoverage0' or property == 'e_TextureNormal0' or property == 'e_TextureDiffuse0'):
        return True
    if shader == 'Opaque_OpaqueSModelCB1Max.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'AddAlpha_MPLBasicAT.fx' and (property == 'e_TextureDiffuse0'):
        return True
    if shader == 'Opaque_MaxCBE1.fx' and (property == 'e_fGloss0' or property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_fEnvMapStrength0' or property == 'e_TextureEnvironment0'):
        return True
    if shader == 'Opaque_MPLBlend.fx' and (property == 'e_TextureFallback0' or property == 'e_fShininess0' or property == 'e_fCoverageScale0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0' or property == 'e_TextureDiffuse1' or property == 'e_TextureNormal1'):
        return True
    if shader == 'Opaque_AddAlphaC1Max.fx' and (property == 'e_TextureDiffuse0'):
        return True
    if shader == 'Opaque_MaxWaterFall.fx' and (property == 'e_fSlide2Y' or property == 'e_TextureDiffuse0' or property == 'e_fSlide1X' or property == 'e_fSlide1Y' or property == 'e_fSlide2X'):
        return True
    if shader == 'Opaque_OpaqueSModelC1Max.fx' and (property == 'e_TextureDiffuse0'):
        return True
    if shader == 'AddAlpha_MaxCBSG1.fx' and (property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'AlphaSModelCB1Max.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'AlphaRegionCE1Max.fx' and (property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_fEnvMapStrength0' or property == 'e_TextureEnvironment' or property == 'e_fGloss0'):
        return True
    if shader == 'AlphaSModelCBGG1Max.fx' and (property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_fBumpiness0'):
        return True
    if shader == 'Opaque_MaxCG1.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureGlow0'):
        return True
    if shader == 'Alpha_MaxC1.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'Alpha_MaxCBSG1.fx' and (property == 'e_TextureNormal0' or property == 'e_fShininess0' or property == 'e_TextureDiffuse0'):
        return True
    if shader == 'Alpha_MaxCB1.fx' and (property == 'e_TextureNormal0' or property == 'e_TextureDiffuse0'):
        return True
    if shader == 'OpaqueRegionC1DTPMax.fx' and (property == 'e_TextureDiffuse0' or property == 'e_fScale1' or property == 'e_TextureDetail2' or property == 'e_TextureDetail0' or property == 'e_fGrassDensity0' or property == 'e_fScale2' or property == 'e_fGrassDensity2' or property == 'e_fGrassDensity6' or property == 'e_TextureDetail9' or property == 'e_fGrassDensity9' or property == 'e_TextureDetail3' or property == 'e_fScale3' or property == 'e_fGrassDensity3' or property == 'e_TextureDetail8' or property == 'e_TextureDetail1' or property == 'e_fGrassDensity1' or property == 'e_fScale5' or property == 'e_TextureDetail6' or property == 'e_fGrassDensity7' or property == 'e_TextureDetail4' or property == 'e_fScale7' or property == 'e_fScale9' or property == 'e_TexturePalette0' or property == 'e_fGrassDensity5' or property == 'e_fScale6' or property == 'e_TextureDetail7' or property == 'e_fGrassDensity8' or property == 'e_fScale0' or property == 'e_fScale4' or property == 'e_fGrassDensity4' or property == 'e_TextureDetail5' or property == 'e_fScale8'):
        return True
    if shader == 'AddAlpha_MaxCG1.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureGlow0'):
        return True
    if shader == 'Opaque_MaxC1.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'Opaque_OpaqueRegionCBGG1Max.fx' and (property == 'e_fBumpiness0' or property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'AddAlphaC1Max.fx' and (property == 'e_TextureDiffuse0'):
        return True
    if shader == 'Chroma_MaxCBS1.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_fShininess0'):
        return True
    if shader == 'Alpha_MaxCBS1.fx' and (property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'Alpha_MPLBumpAT.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0' or property == 'e_TextureFallback0' or property == 'e_fCoverageScale0' or property == 'e_fShininess0'):
        return True
    if shader == 'Opaque_MPLBumpAT.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0' or property == 'e_TextureFallback0' or property == 'e_fCoverageScale0'):
        return True
    if shader == 'Opaque_MPLBasic.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0'):
        return True
    if shader == 'Opaque_MPLGB.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0' or property == 'e_fCoverageScale0'):
        return True
    if shader == 'Chroma_MaxCB1.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'Opaque_MPLSB.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0' or property == 'e_fShininess0' or property == 'e_fCoverageScale0'):
        return True
    if shader == 'Opaque_MaxC1DTP.fx' and (property == 'e_fScale8' or property == 'e_fGrassDensity8' or property == 'e_fGrassDensity3' or property == 'e_TextureDiffuse0' or property == 'e_TextureDetail0' or property == 'e_fScale2' or property == 'e_fScale3' or property == 'e_TextureDetail9' or property == 'e_fScale9' or property == 'e_fGrassDensity0' or property == 'e_fGrassDensity2' or property == 'e_TextureDetail3' or property == 'e_fGrassDensity7' or property == 'e_TextureDetail8' or property == 'e_TexturePalette0' or property == 'e_TextureDetail1' or property == 'e_fGrassDensity1' or property == 'e_fScale7' or property == 'e_fScale0' or property == 'e_fScale1' or property == 'e_TextureDetail4' or property == 'e_fScale4' or property == 'e_TextureDetail5' or property == 'e_fScale6' or property == 'e_TextureDetail2' or property == 'e_fGrassDensity5' or property == 'e_TextureDetail6' or property == 'e_TextureDetail7' or property == 'e_fGrassDensity4' or property == 'e_fScale5' or property == 'e_fGrassDensity6' or property == 'e_fGrassDensity9'):
        return True
    if shader == 'OpaqueRegionC1Max.fx' and (property == 'e_TextureDiffuse0'):
        return True
    if shader == 'Opaque_MPLBasicA.fx' and (property == 'e_TextureDiffuse0'):
        return True
    if shader == 'Opaque_OpaqueSkinMeshCBGGE1Max.fx' and (property == 'e_TextureEnvironment0' or property == 'e_fBumpiness0' or property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_fEnvMapStrength0'):
        return True
    if shader == 'Opaque_MaxCB1.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'Opaque_MPLBump2UV.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0' or property == 'e_fShininess0'):
        return True
    if shader == 'Opaque_MaxLava.fx' and (property == 'e_fSlide1Y' or property == 'e_fSlide2X' or property == 'e_fSlide2Y' or property == 'e_TextureDiffuse0' or property == 'e_TextureDiffuse1' or property == 'e_TextureNormal0' or property == 'e_fSlide1X'):
        return True
    if shader == 'Opaque_MaxTerrain.fx' and (property == 'e_fCoverageScale' or property == 'e_TextureDetail1' or property == 'e_TextureDetail2' or property == 'e_TextureCoverage' or property == 'e_TextureFallback'):
        return True
    if shader == 'Opaque_MaxCBS_2UV.fx' and (property == 'e_TextureCoverage0' or property == 'e_TextureFallback0' or property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'Chroma_MPLBumpAT.fx' and (property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0' or property == 'e_TextureFallback0' or property == 'e_fCoverageScale0'):
        return True
    if shader == 'Alpha_MaxCE1.fx' and (property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_fEnvMapStrength0' or property == 'e_TextureEnvironment' or property == 'e_fGloss0'):
        return True
    if shader == 'Chroma_MaxCBSG1.fx' and (property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'Opaque_MPLFull.fx' and (property == 'e_fShininess0' or property == 'e_fCoverageScale0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0'):
        return True
    if shader == 'OpaqueChroma' and (property == 'e_TextureDiffuse0' or property == 'e_TextureDiffuse1'):
        return True
    if shader == 'Opaque_MaxCSG1.fx' and (property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureGlow0'):
        return True
    if shader == 'OpaqueRegionCB1Max.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'Opaque_MaxCBS1.fx' and (property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'Opaque_MPLBasicAT.fx' and (property == 'e_TextureDiffuse0'):
        return True
    if shader == 'Opaque_OpaqueSModelCG1Max.fx' and (property == 'e_TextureGlow0' or property == 'e_TextureDiffuse0'):
        return True
    if shader == 'OpaqueSModelCB1Max.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'Chroma_MPLBasicAT.fx' and (property == 'e_TextureDiffuse0' or property == 'e_fShininess0' or property == 'e_TextureFallback0' or property == 'e_fCoverageScale0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0'):
        return True
    if shader == 'Opaque_OpaqueRegionCB1Max.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'AlphaSModelC1Max.fx' and (property == 'e_TextureDiffuse0'):
        return True
    if shader == 'Opaque_MaxWater.fx' and (property == 'e_fSlide1Y' or property == 'e_fSlide2X' or property == 'e_fFresnelBias' or property == 'e_fFresnelPower' or property == 'e_fReflectionAmount' or property == 'e_fSlide1X' or property == 'e_fSlide2Y' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureEnvironment0' or property == 'e_fWaterColor1' or property == 'e_fWaterColor2' or property == 'e_fReflectionColor'):
        return True
    if shader == 'Opaque_MaxCBSE1.fx' and (property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_fEnvMapStrength0' or property == 'e_TextureEnvironment0'):
        return True
    if shader == 'Opaque_MaxCBSGE1.fx' and (property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_fEnvMapStrength0' or property == 'e_TextureEnvironment0'):
        return True
    if shader == 'Alpha_MaxCBSGE1.fx' and (property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_fEnvMapStrength0' or property == 'e_TextureEnvironment0'):
        return True
    if shader == 'Opaque_MaxCE1.fx' and (property == 'e_TextureDiffuse0' or property == 'e_fEnvMapStrength0' or property == 'e_TextureEnvironment' or property == 'e_fGloss0' or property == 'e_fShininess0'):
        return True
    if shader == 'AddAlpha_MaxCB1.fx' and (property == 'e_TextureNormal0' or property == 'e_TextureDiffuse0'):
        return True
    if shader == 'Chroma_MaxC1.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'Alpha_MPLBumpA.fx' and (property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0' or property == 'e_TextureFallback0' or property == 'e_fCoverageScale0'):
        return True
    if shader == 'Opaque_MPLBlendNoBump.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureCoverage0' or property == 'e_TextureDiffuse1' or property == 'e_TextureFallback0' or property == 'e_fShininess0' or property == 'e_fCoverageScale0'):
        return True
    if shader == 'Opaque_MaxCBSG1_2UV.fx' and (property == 'e_TextureNormal0' or property == 'e_TextureSecond0' or property == 'e_fShininess0' or property == 'e_TextureDiffuse0'):
        return True
    if shader == 'Opaque_MPLFull2UV.fx' and (property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0'):
        return True
    if shader == 'Chroma_MaxCBSGE1.fx' and (property == 'e_fEnvMapStrength0' or property == 'e_TextureEnvironment0' or property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'OpaqueSModelCG1Max.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureGlow0'):
        return True
    if shader == 'Opaque_MPLSB2UV.fx' and (property == 'e_TextureCoverage0' or property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'Chroma_MPLBasicA.fx' and (property == 'e_TextureDiffuse0' or property == 'e_fShininess0' or property == 'e_TextureFallback0' or property == 'e_fCoverageScale0'):
        return True
    if shader == 'Chroma_MPLBumpA.fx' and (property == 'e_TextureCoverage0' or property == 'e_TextureFallback0' or property == 'e_fShininess0' or property == 'e_fCoverageScale0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'OpaqueRegionCBGG1Max.fx' and (property == 'e_fBumpiness0' or property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'OpaqueRegionCE1Max.fx' and (property == 'e_TextureEnvironment' or property == 'e_fGloss0' or property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_fEnvMapStrength0'):
        return True
    if shader == 'Chroma_MPLGBAT.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0' or property == 'e_TextureFallback0' or property == 'e_fCoverageScale0'):
        return True
    if shader == 'AddAlpha_MPLBumpA.fx' and (property == 'e_fCoverageScale0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0' or property == 'e_TextureFallback0'):
        return True
    if shader == 'Opaque_MaxCBST2_2UV.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureDiffuse1' or property == 'e_TextureNormal1' or property == 'e_TextureFallback0' or property == 'e_fShininess0' or property == 'e_fCoverageScale0'):
        return True
    if shader == 'Opaque_MPLBump.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0' or property == 'e_fCoverageScale0' or property == 'e_fShininess0'):
        return True
    if shader == 'AddAlpha_MaxC1.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'Opaque_MPLGB2UV.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0'):
        return True
    if shader == 'Opaque_MaxC1_2UV.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureSecond0' or property == 'e_fGloss0' or property == 'e_fShininess0'):
        return True
    if shader == 'Opaque_MPLBumpA.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_TextureCoverage0' or property == 'e_TextureFallback0' or property == 'e_fCoverageScale0'):
        return True
    if shader == 'Opaque_MaxSMLava2.fx' and (property == 'e_TextureNormal0' or property == 'e_TextureDiffuse1' or property == 'e_TextureNormal1' or property == 'e_fSlide1Y' or property == 'e_fSlide2Y' or property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_fSlide1X' or property == 'e_fSlide2X'):
        return True
    if shader == 'Opaque_OpaqueSkinMeshCBGG1Max.fx' and (property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0' or property == 'e_fBumpiness0' or property == 'e_fShininess0'):
        return True
    if shader == 'Opaque_MaxLava2.fx' and (property == 'e_fSlide2X' or property == 'e_fSlide2Y' or property == 'e_TextureNormal0' or property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureDiffuse1' or property == 'e_TextureNormal1' or property == 'e_fSlide1X' or property == 'e_fSlide1Y'):
        return True
    if shader == 'Opaque_OpaqueSModelCBGG1Max.fx' and (property == 'e_fBumpiness0' or property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'OpaqueSModelCBGG1Max.fx' and (property == 'e_fBumpiness0' or property == 'e_fShininess0' or property == 'e_TextureDiffuse0' or property == 'e_TextureNormal0'):
        return True
    if shader == 'AddAlpha_MPLBasicA.fx' and (property == 'e_TextureDiffuse0'):
        return True



class MATERIAL_OT_add_default_eqgmatdef(bpy.types.Operator):
    """Add default EQG Material Def properties to the selected material"""
    bl_idname = "material.add_default_eqgmatdef"
    bl_label = "Add Default EQG MatDef"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_material

    def execute(self, context):
        material = context.object.active_material
        if not material:
            return {'CANCELLED'}

        # 🔹 Tag as EQG material
        material['quaildef'] = 'eqgmaterialdef'

        props = material.quail_eqgmaterialdef

        # 🔹 Prevent repeated shader rebuild spam
        # (temporarily disable update callbacks)
        def suppress_updates(prop_group):
            for attr in dir(prop_group):
                try:
                    prop = getattr(type(prop_group), attr, None)
                    if hasattr(prop, "update"):
                        setattr(prop_group, attr, getattr(prop_group, attr))
                except:
                    pass

        # 🔹 Core defaults (correct types)
        props.shadertag = 'Opaque_MaxCB1.fx'
        props.e_fShininess0 = 0.0
        props.e_TextureDiffuse0 = ""
        props.e_TextureDiffuse0mapChannel = ""
        props.e_TextureDiffuse1 = ""
        props.e_TextureEnvironment = ""
        props.e_TextureEnvironment0 = ""
        props.e_TextureFallback = ""
        props.e_TextureFallback0 = ""
        props.e_TextureNormal0 = ""
        props.e_TextureNormal0mapChannel = ""
        props.e_TextureNormal1 = ""

        # 🔹 Numeric shader params (store as strings only if your pipeline truly requires it)
        props.e_fBumpiness0 = ""
        props.e_fCoverageScale0 = ""
        props.e_fEnvMapStrength0 = ""
        props.e_fFresnelBias = ""
        props.e_fFresnelPower = ""
        props.e_fGloss0 = ""
        props.e_fReflectionAmount = ""
        props.e_fReflectionColor = ""

        # 🔹 Scale / slide / misc
        for i in range(10):
            setattr(props, f"e_fScale{i}", "")
            setattr(props, f"e_fGrassDensity{i}", "")
            setattr(props, f"e_TextureDetail{i}", "")

        props.e_fSlide1X = ""
        props.e_fSlide1Y = ""
        props.e_fSlide2X = ""
        props.e_fSlide2Y = ""

        props.e_fWaterColor1 = ""
        props.e_fWaterColor2 = ""

        # 🔹 Texture extras
        props.e_TextureCoverage = ""
        props.e_TextureCoverage0 = ""
        props.e_TextureGlow0 = ""
        props.e_TexturePalette0 = ""
        props.e_TextureSecond0 = ""
        props.e_TextureSecond0mapChannel = ""

        # 🔹 Apply shader ONCE
        err = eqg_apply(material)
        if err:
            error(err)
            return {'CANCELLED'}

        return {'FINISHED'}


# Register classes
def register():
    # ignored, auto_load bpy.utils.register_class(QuailMaterialDefinitionProperties)
    # Add this line to register the operator
    # bpy.utils.register_class(MATERIAL_OT_add_default_quaildef)

    bpy.types.Material.quail_eqgmaterialdef = PointerProperty(
        type=QuailEqgMaterialDefinitionProperties)

    # Try multiple Surface panel variants (Blender 4.2.1 has different panels per render engine)
    try:
        # For Cycles render engine
        import _cycles
        bpy.types.CYCLES_MATERIAL_PT_surface.prepend(
            draw_eqgmaterialdefinition_in_transform)
    except (AttributeError, ImportError):
        pass

    try:
        # For Eevee render engine
        bpy.types.EEVEE_MATERIAL_PT_surface.prepend(
            draw_eqgmaterialdefinition_in_transform)
    except AttributeError:
        pass

    # Generic surface panel (fallback)
    try:
        bpy.types.MATERIAL_PT_surface.prepend(
            draw_eqgmaterialdefinition_in_transform)
    except AttributeError:
        # Last resort, use viewport panel
        print("Using viewport panel as fallback")
        # Keep your existing code as fallback
        bpy.types.MATERIAL_PT_viewport.prepend(
            draw_eqgmaterialdefinition_in_transform)


def unregister():
    # Add this line to unregister the operator
    # bpy.utils.unregister_class(MATERIAL_OT_add_default_quaildef)
    del bpy.types.Material.quail_eqgmaterialdef

    # Remove from all possible panels
    try:
        bpy.types.CYCLES_MATERIAL_PT_surface.remove(
            draw_eqgmaterialdefinition_in_transform)
    except AttributeError:
        pass

    try:
        bpy.types.EEVEE_MATERIAL_PT_surface.remove(
            draw_eqgmaterialdefinition_in_transform)
    except AttributeError:
        pass

    try:
        bpy.types.MATERIAL_PT_surface.remove(
            draw_eqgmaterialdefinition_in_transform)
    except AttributeError:
        pass

    try:
        bpy.types.MATERIAL_PT_viewport.remove(
            draw_eqgmaterialdefinition_in_transform)
    except AttributeError:
        pass
