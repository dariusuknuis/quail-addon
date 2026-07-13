# eqg_shaders.py

from dataclasses import dataclass
from typing import Dict, List


# =========================================================
# Shader Techniques
# =========================================================

TECHNIQUES = [
    "Opaque",
    "Alpha",
    "AddAlpha",
    "Chroma",
]


# =========================================================
# Shader Groups
#
# Used only to organize the UI.
# =========================================================

SHADER_GROUPS = [
    "Basic",
    "Bump",
    "Glow",
    "Gloss",
    "Environment",
    "Terrain",
    "Water",
    "Lava",
    "Blend",
    "Special",
]


# =========================================================
# Shader Family Definition
# =========================================================

@dataclass(frozen=True)
class ShaderFamily:

    name: str

    #
    # Which UI group this belongs under.
    #
    group: str

    #
    # Techniques allowed for this shader.
    #
    techniques: List[str]

    #
    # All filename aliases that map to this family.
    #
    aliases: List[str]

    #
    # Property names supported by this family.
    #
    properties: List[str]


# =========================================================
# Shader Families
# =========================================================

SHADER_FAMILIES: Dict[str, ShaderFamily] = {

    #
    # -----------------------------------------------------
    # Basic
    # -----------------------------------------------------
    #

    "C1": ShaderFamily(
        name="C1",
        group="Basic",
        techniques=TECHNIQUES,
        aliases=[
            "MaxC1",
            "MPLBasic",
        ],
        properties=[
            "e_TextureDiffuse0",
        ],
    ),

    "CB1": ShaderFamily(
        name="CB1",
        group="Bump",
        techniques=TECHNIQUES,
        aliases=[
            "MaxCB1",
            "MPLBump",
            "OpaqueRegionCB1",
            "OpaqueSModelCB1",
            "AlphaSModelCB1",
        ],
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
        ],
    ),

    "CBS1": ShaderFamily(
        name="CBS1",
        group="Gloss",
        techniques=TECHNIQUES,
        aliases=[
            "MaxCBS1",
        ],
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_fShininess0",
        ],
    ),

    "CBSG1": ShaderFamily(
        name="CBSG1",
        group="Glow",
        techniques=TECHNIQUES,
        aliases=[
            "MaxCBSG1",
        ],
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_fShininess0",
        ],
    ),

    "CBSGE1": ShaderFamily(
        name="CBSGE1",
        group="Environment",
        techniques=TECHNIQUES,
        aliases=[
            "MaxCBSGE1",
        ],
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_fShininess0",
            "e_TextureEnvironment0",
            "e_fEnvMapStrength0",
        ],
    ),

    "CE1": ShaderFamily(
        name="CE1",
        group="Environment",
        techniques=TECHNIQUES,
        aliases=[
            "MaxCE1",
            "RegionCE1",
        ],
        properties=[
            "e_TextureDiffuse0",
            "e_TextureEnvironment",
            "e_fEnvMapStrength0",
            "e_fGloss0",
            "e_fShininess0",
        ],
    ),

    "CG1": ShaderFamily(
        name="CG1",
        group="Glow",
        techniques=TECHNIQUES,
        aliases=[
            "MaxCG1",
            "SModelCG1",
        ],
        properties=[
            "e_TextureDiffuse0",
            "e_TextureGlow0",
        ],
    ),

    "CSG1": ShaderFamily(
        name="CSG1",
        group="Glow",
        techniques=["Opaque"],
        aliases=[
            "MaxCSG1",
        ],
        properties=[
            "e_TextureDiffuse0",
            "e_TextureGlow0",
            "e_fShininess0",
        ],
    ),

    #
    # -----------------------------------------------------
    # Multipass Lighting
    # -----------------------------------------------------
    #

    "BasicA": ShaderFamily(
        name="BasicA",
        group="Blend",
        techniques=TECHNIQUES,
        aliases=[
            "MPLBasicA",
        ],
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureCoverage0",
            "e_TextureFallback0",
            "e_fCoverageScale0",
            "e_fShininess0",
        ],
    ),

    "BasicAT": ShaderFamily(
        name="BasicAT",
        group="Blend",
        techniques=TECHNIQUES,
        aliases=[
            "MPLBasicAT",
        ],
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureCoverage0",
            "e_TextureFallback0",
            "e_fCoverageScale0",
            "e_fShininess0",
        ],
    ),

    "BumpA": ShaderFamily(
        name="BumpA",
        group="Blend",
        techniques=TECHNIQUES,
        aliases=[
            "MPLBumpA",
        ],
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureCoverage0",
            "e_TextureFallback0",
            "e_fCoverageScale0",
            "e_fShininess0",
        ],
    ),

    "BumpAT": ShaderFamily(
        name="BumpAT",
        group="Blend",
        techniques=TECHNIQUES,
        aliases=[
            "MPLBumpAT",
        ],
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureCoverage0",
            "e_TextureFallback0",
            "e_fCoverageScale0",
            "e_fShininess0",
        ],
    ),

    "Blend": ShaderFamily(
        name="Blend",
        group="Blend",
        techniques=["Opaque"],
        aliases=[
            "MPLBlend",
            "MPLBlendNoBump",
        ],
        properties=[
            "e_TextureDiffuse0",
            "e_TextureDiffuse1",
            "e_TextureNormal0",
            "e_TextureNormal1",
            "e_TextureCoverage0",
            "e_TextureFallback0",
            "e_fCoverageScale0",
            "e_fShininess0",
        ],
    ),

    #
    # -----------------------------------------------------
    # Terrain
    # -----------------------------------------------------
    #

    "Terrain": ShaderFamily(
        name="Terrain",
        group="Terrain",
        techniques=["Opaque"],
        aliases=[
            "MaxTerrain",
        ],
        properties=[
            "e_TextureCoverage",
            "e_TextureFallback",
            "e_TextureDetail1",
            "e_TextureDetail2",
            "e_fCoverageScale0",
        ],
    ),

    #
    # -----------------------------------------------------
    # Water
    # -----------------------------------------------------
    #

    "Water": ShaderFamily(
        name="Water",
        group="Water",
        techniques=["Opaque"],
        aliases=[
            "MaxWater",
        ],
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureEnvironment0",
            "e_fReflectionAmount",
            "e_fReflectionColor",
            "e_fFresnelBias",
            "e_fFresnelPower",
            "e_fWaterColor1",
            "e_fWaterColor2",
            "e_fSlide1X",
            "e_fSlide1Y",
            "e_fSlide2X",
            "e_fSlide2Y",
        ],
    ),

    "WaterFall": ShaderFamily(
        name="WaterFall",
        group="Water",
        techniques=["Opaque"],
        aliases=[
            "MaxWaterFall",
        ],
        properties=[
            "e_TextureDiffuse0",
            "e_fSlide1X",
            "e_fSlide1Y",
            "e_fSlide2X",
            "e_fSlide2Y",
        ],
    ),

    #
    # -----------------------------------------------------
    # Lava
    # -----------------------------------------------------
    #

    "Lava": ShaderFamily(
        name="Lava",
        group="Lava",
        techniques=["Opaque"],
        aliases=[
            "MaxLava",
            "MaxLava2",
            "MaxSMLava2",
        ],
        properties=[
            "e_TextureDiffuse0",
            "e_TextureDiffuse1",
            "e_TextureNormal0",
            "e_TextureNormal1",
            "e_fSlide1X",
            "e_fSlide1Y",
            "e_fSlide2X",
            "e_fSlide2Y",
            "e_fShininess0",
        ],
    ),

}


# =========================================================
# Alias Lookup
# =========================================================

ALIAS_LOOKUP: Dict[str, str] = {}

for family in SHADER_FAMILIES.values():
    for alias in family.aliases:
        ALIAS_LOOKUP[alias.lower()] = family.name