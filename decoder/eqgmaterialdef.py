# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportAttributeAccessIssue=false

import bpy
from ..wce.wce import wce
from ..wce.materialdefinition import materialdefinition
from .context import Context

def decode_eqgmaterialdef(ctx:Context, modelname:str, materialname:str, shadertag: str, hexoneflag: int, properties:list[tuple[str, int, str]], animsleep:int, textures:list[str]) -> str:
    matname = f"{modelname}_{materialname}"
    if matname in bpy.data.materials:
        return ""

    material = bpy.data.materials.new(matname)
    material['quaildef'] = 'eqgmaterialdef'
    material.quail_eqgmaterialdef.shadertag = shadertag
    for prop in properties:
        if prop[0] == "e_fShininess0":
            material.quail_eqgmaterialdef.e_fShininess0 = prop[2]
        elif prop[0] == "e_TextureDiffuse0":
            material.quail_eqgmaterialdef.e_TextureDiffuse0 = prop[2]
        elif prop[0] == "e_TextureDiffuse0mapChannel":
            material.quail_eqgmaterialdef.e_TextureDiffuse0mapChannel = prop[2]
        elif prop[0] == "e_TextureDiffuse1":
            material.quail_eqgmaterialdef.e_TextureDiffuse1 = prop[2]
        elif prop[0] == "e_TextureEnvironment":
            material.quail_eqgmaterialdef.e_TextureEnvironment = prop[2]
        elif prop[0] == "e_TextureEnvironment0":
            material.quail_eqgmaterialdef.e_TextureEnvironment0 = prop[2]
        elif prop[0] == "e_TextureFallback":
            material.quail_eqgmaterialdef.e_TextureFallback = prop[2]
        elif prop[0] == "e_TextureFallback0":
            material.quail_eqgmaterialdef.e_TextureFallback0 = prop[2]
        elif prop[0] == "e_TextureNormal0":
            material.quail_eqgmaterialdef.e_TextureNormal0 = prop[2]
        elif prop[0] == "e_TextureNormal0mapChannel":
            material.quail_eqgmaterialdef.e_TextureNormal0mapChannel = prop[2]
        elif prop[0] == "e_TextureNormal1":
            material.quail_eqgmaterialdef.e_TextureNormal1 = prop[2]
        elif prop[0] == "e_fBumpiness0":
            material.quail_eqgmaterialdef.e_fBumpiness0 = prop[2]
        elif prop[0] == "e_fCoverageScale0":
            material.quail_eqgmaterialdef.e_fCoverageScale0 = prop[2]
        elif prop[0] == "e_fEnvMapStrength0":
            material.quail_eqgmaterialdef.e_fEnvMapStrength0 = prop[2]
        elif prop[0] == "e_fFresnelBias":
            material.quail_eqgmaterialdef.e_fFresnelBias = prop[2]
        elif prop[0] == "e_fFresnelPower":
            material.quail_eqgmaterialdef.e_fFresnelPower = prop[2]
        elif prop[0] == "e_fGloss0":
            material.quail_eqgmaterialdef.e_fGloss0 = prop[2]
        elif prop[0] == "e_fGrassDensity0":
            material.quail_eqgmaterialdef.e_fGrassDensity0 = prop[2]
        elif prop[0] == "e_fGrassDensity1":
            material.quail_eqgmaterialdef.e_fGrassDensity1 = prop[2]
        elif prop[0] == "e_fGrassDensity2":
            material.quail_eqgmaterialdef.e_fGrassDensity2 = prop[2]
        elif prop[0] == "e_fGrassDensity3":
            material.quail_eqgmaterialdef.e_fGrassDensity3 = prop[2]
        elif prop[0] == "e_fGrassDensity4":
            material.quail_eqgmaterialdef.e_fGrassDensity4 = prop[2]
        elif prop[0] == "e_fGrassDensity5":
            material.quail_eqgmaterialdef.e_fGrassDensity5 = prop[2]
        elif prop[0] == "e_fGrassDensity6":
            material.quail_eqgmaterialdef.e_fGrassDensity6 = prop[2]
        elif prop[0] == "e_fGrassDensity7":
            material.quail_eqgmaterialdef.e_fGrassDensity7 = prop[2]
        elif prop[0] == "e_fGrassDensity8":
            material.quail_eqgmaterialdef.e_fGrassDensity8 = prop[2]
        elif prop[0] == "e_fGrassDensity9":
            material.quail_eqgmaterialdef.e_fGrassDensity9 = prop[2]
        elif prop[0] == "e_fReflectionAmount":
            material.quail_eqgmaterialdef.e_fReflectionAmount = prop[2]
        elif prop[0] == "e_fReflectionColor":
            material.quail_eqgmaterialdef.e_fReflectionColor = prop[2]
        elif prop[0] == "e_fScale0":
            material.quail_eqgmaterialdef.e_fScale0 = prop[2]
        elif prop[0] == "e_fScale1":
            material.quail_eqgmaterialdef.e_fScale1 = prop[2]
        elif prop[0] == "e_fScale2":
            material.quail_eqgmaterialdef.e_fScale2 = prop[2]
        elif prop[0] == "e_fScale3":
            material.quail_eqgmaterialdef.e_fScale3 = prop[2]
        elif prop[0] == "e_fScale4":
            material.quail_eqgmaterialdef.e_fScale4 = prop[2]
        elif prop[0] == "e_fScale5":
            material.quail_eqgmaterialdef.e_fScale5 = prop[2]
        elif prop[0] == "e_fScale6":
            material.quail_eqgmaterialdef.e_fScale6 = prop[2]
        elif prop[0] == "e_fScale7":
            material.quail_eqgmaterialdef.e_fScale7 = prop[2]
        elif prop[0] == "e_fScale8":
            material.quail_eqgmaterialdef.e_fScale8 = prop[2]
        elif prop[0] == "e_fScale9":
            material.quail_eqgmaterialdef.e_fScale9 = prop[2]
        elif prop[0] == "e_fSlide1X":
            material.quail_eqgmaterialdef.e_fSlide1X = prop[2]
        elif prop[0] == "e_fSlide1Y":
            material.quail_eqgmaterialdef.e_fSlide1Y = prop[2]
        elif prop[0] == "e_fSlide2X":
            material.quail_eqgmaterialdef.e_fSlide2X = prop[2]
        elif prop[0] == "e_fSlide2Y":
            material.quail_eqgmaterialdef.e_fSlide2Y = prop[2]
        elif prop[0] == "e_fWaterColor1":
            material.quail_eqgmaterialdef.e_fWaterColor1 = prop[2]
        elif prop[0] == "e_fWaterColor2":
            material.quail_eqgmaterialdef.e_fWaterColor2 = prop[2]
        elif prop[0] == "e_TextureCoverage":
            material.quail_eqgmaterialdef.e_TextureCoverage = prop[2]
        elif prop[0] == "e_TextureCoverage0":
            material.quail_eqgmaterialdef.e_TextureCoverage0 = prop[2]
        elif prop[0] == "e_TextureDetail0":
            material.quail_eqgmaterialdef.e_TextureDetail0 = prop[2]
        elif prop[0] == "e_TextureDetail1":
            material.quail_eqgmaterialdef.e_TextureDetail1 = prop[2]
        elif prop[0] == "e_TextureDetail2":
            material.quail_eqgmaterialdef.e_TextureDetail2 = prop[2]
        elif prop[0] == "e_TextureDetail3":
            material.quail_eqgmaterialdef.e_TextureDetail3 = prop[2]
        elif prop[0] == "e_TextureDetail4":
            material.quail_eqgmaterialdef.e_TextureDetail4 = prop[2]
        elif prop[0] == "e_TextureDetail5":
            material.quail_eqgmaterialdef.e_TextureDetail5 = prop[2]
        elif prop[0] == "e_TextureDetail6":
            material.quail_eqgmaterialdef.e_TextureDetail6 = prop[2]
        elif prop[0] == "e_TextureDetail7":
            material.quail_eqgmaterialdef.e_TextureDetail7 = prop[2]
        elif prop[0] == "e_TextureDetail8":
            material.quail_eqgmaterialdef.e_TextureDetail8 = prop[2]
        elif prop[0] == "e_TextureDetail9":
            material.quail_eqgmaterialdef.e_TextureDetail9 = prop[2]
        elif prop[0] == "e_TextureGlow0":
            material.quail_eqgmaterialdef.e_TextureGlow0 = prop[2]
        elif prop[0] == "e_TexturePalette0":
            material.quail_eqgmaterialdef.e_TexturePalette0 = prop[2]
        elif prop[0] == "e_TextureSecond0":
            material.quail_eqgmaterialdef.e_TextureSecond0 = prop[2]
        elif prop[0] == "e_TextureSecond0mapChannel":
            material.quail_eqgmaterialdef.e_TextureSecond0mapChannel = prop[2]
        else:
            return f"unsupported property {prop[0]}"

    # Add textures to the collection
    for texture in textures:
        tex_item = material.quail_eqgmaterialdef.textures.add()
        tex_item.texture_name = texture

    # Set flag
    material.quail_eqgmaterialdef.hexoneflag = (hexoneflag == 1)
    material.quail_eqgmaterialdef.animsleep = animsleep

    material.use_nodes = True
    return ""
