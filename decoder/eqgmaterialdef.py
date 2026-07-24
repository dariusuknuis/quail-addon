# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportAttributeAccessIssue=false

import bpy, os
from bpy.types import Mesh
from ..wce.wce import wce
from .context import Context
from ..ui.panel.eqgmaterialdef import eqg_apply
from ..common.eqgshaders import parse_shader_tag
from ..common.image_loader import load_eqg_image

def decode_eqgmaterialdef(ctx:Context, mesh:Mesh, modelname:str, materialname:str, shadertag: str, properties:list[tuple[str, int, str]], animsleep:int, textures:list[str], flip_tex: bool = False) -> str:
    matname = f"{modelname}_{materialname}"
    if matname in bpy.data.materials:
        if mesh.materials.get(matname) is None:
            mesh.materials.append(bpy.data.materials[matname])
        return ""

    material = bpy.data.materials.new(matname)
    mesh.materials.append(material)
    material['quaildef'] = 'eqgmaterialdef'

    props = material.quail_eqgmaterialdef

    props.shadertag = shadertag

    alpha_mode, shader = parse_shader_tag(shadertag)

    props.alpha_mode = alpha_mode
    props.shader = shader

    props.property_rows.clear()
    for prop in properties:
        if prop[0] == "e_fShininess0":
            props.e_fShininess0 = float(prop[2])
        elif prop[0] == "e_TextureDiffuse0":
            props.e_TextureDiffuse0 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureDiffuse0mapChannel":
            props.e_TextureDiffuse0mapChannel = prop[2]
        elif prop[0] == "e_TextureDiffuse1":
            props.e_TextureDiffuse1 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureEnvironment":
            props.e_TextureEnvironment = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureEnvironment0":
            props.e_TextureEnvironment0 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureFallback":
            props.e_TextureFallback = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureFallback0":
            props.e_TextureFallback0 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureNormal0":
            props.e_TextureNormal0 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureNormal0mapChannel":
            props.e_TextureNormal0mapChannel = prop[2]
        elif prop[0] == "e_TextureNormal1":
            props.e_TextureNormal1 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_fBumpiness0":
            props.e_fBumpiness0 = float(prop[2])
        elif prop[0] == "e_fCoverageScale0":
            props.e_fCoverageScale0 = float(prop[2])
        elif prop[0] == "e_fEnvMapStrength0":
            props.e_fEnvMapStrength0 = float(prop[2])
        elif prop[0] == "e_fFresnelBias":
            props.e_fFresnelBias = float(prop[2])
        elif prop[0] == "e_fFresnelPower":
            props.e_fFresnelPower = float(prop[2])
        elif prop[0] == "e_fGloss0":
            props.e_fGloss0 = float(prop[2])
        elif prop[0] == "e_fGrassDensity0":
            props.e_fGrassDensity0 = float(prop[2])
        elif prop[0] == "e_fGrassDensity1":
            props.e_fGrassDensity1 = float(prop[2])
        elif prop[0] == "e_fGrassDensity2":
            props.e_fGrassDensity2 = float(prop[2])
        elif prop[0] == "e_fGrassDensity3":
            props.e_fGrassDensity3 = float(prop[2])
        elif prop[0] == "e_fGrassDensity4":
            props.e_fGrassDensity4 = float(prop[2])
        elif prop[0] == "e_fGrassDensity5":
            props.e_fGrassDensity5 = float(prop[2])
        elif prop[0] == "e_fGrassDensity6":
            props.e_fGrassDensity6 = float(prop[2])
        elif prop[0] == "e_fGrassDensity7":
            props.e_fGrassDensity7 = float(prop[2])
        elif prop[0] == "e_fGrassDensity8":
            props.e_fGrassDensity8 = float(prop[2])
        elif prop[0] == "e_fGrassDensity9":
            props.e_fGrassDensity9 = float(prop[2])
        elif prop[0] == "e_fReflectionAmount":
            props.e_fReflectionAmount = float(prop[2])
        elif prop[0] == "e_fReflectionColor":
            values = [float(x) / 255.0 for x in prop[2].split()]
            if len(values) == 4:
                a, r, g, b = values
                props.e_fReflectionColor = (r, g, b, a)
        elif prop[0] == "e_fScale0":
            props.e_fScale0 = float(prop[2])
        elif prop[0] == "e_fScale1":
            props.e_fScale1 = float(prop[2])
        elif prop[0] == "e_fScale2":
            props.e_fScale2 = float(prop[2])
        elif prop[0] == "e_fScale3":
            props.e_fScale3 = float(prop[2])
        elif prop[0] == "e_fScale4":
            props.e_fScale4 = float(prop[2])
        elif prop[0] == "e_fScale5":
            props.e_fScale5 = float(prop[2])
        elif prop[0] == "e_fScale6":
            props.e_fScale6 = float(prop[2])
        elif prop[0] == "e_fScale7":
            props.e_fScale7 = float(prop[2])
        elif prop[0] == "e_fScale8":
            props.e_fScale8 = float(prop[2])
        elif prop[0] == "e_fScale9":
            props.e_fScale9 = float(prop[2])
        elif prop[0] == "e_fSlide1X":
            props.e_fSlide1X = float(prop[2])
        elif prop[0] == "e_fSlide1Y":
            props.e_fSlide1Y = float(prop[2])
        elif prop[0] == "e_fSlide2X":
            props.e_fSlide2X = float(prop[2])
        elif prop[0] == "e_fSlide2Y":
            props.e_fSlide2Y = float(prop[2])
        elif prop[0] == "e_fWaterColor1":
            values = [float(x) / 255.0 for x in prop[2].split()]
            if len(values) == 4:
                a, r, g, b = values
                props.e_fWaterColor1 = (r, g, b, a)
        elif prop[0] == "e_fWaterColor2":
            values = [float(x) / 255.0 for x in prop[2].split()]
            if len(values) == 4:
                a, r, g, b = values
                props.e_fWaterColor2 = (r, g, b, a)
        elif prop[0] == "e_TextureCoverage":
            props.e_TextureCoverage = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureCoverage0":
            props.e_TextureCoverage0 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureDetail0":
            props.e_TextureDetail0 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureDetail1":
            props.e_TextureDetail1 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureDetail2":
            props.e_TextureDetail2 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureDetail3":
            props.e_TextureDetail3 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureDetail4":
            props.e_TextureDetail4 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureDetail5":
            props.e_TextureDetail5 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureDetail6":
            props.e_TextureDetail6 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureDetail7":
            props.e_TextureDetail7 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureDetail8":
            props.e_TextureDetail8 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureDetail9":
            props.e_TextureDetail9 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureGlow0":
            props.e_TextureGlow0 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TexturePalette0":
            props.e_TexturePalette0 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureSecond0":
            props.e_TextureSecond0 = prop[2]
            err = load_eqg_image(ctx, prop[2], flip_tex=flip_tex)
            if err:
                return f"load {prop[0]}: {err}"
        elif prop[0] == "e_TextureSecond0mapChannel":
            props.e_TextureSecond0mapChannel = prop[2]
        else:
            return f"unsupported property {prop[0]}"

        property_row = props.property_rows.add()
        property_row.property_name = prop[0]

    # Add textures to the collection
    for texture in textures:
        tex_item = props.textures.add()
        tex_item.texture_name = texture

    # Set flag
    props.animsleep = animsleep


    err =  eqg_apply(material)
    if err:
        return f"eqg_apply: {err}"

    return ""