# eqg_shaders.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import math, bpy
import os
from typing import Any, Callable, Optional
from bpy.types import Image, Material, Node, NodeSocket, NodeTree
from . import state

DEFAULT_UV_SCALE = 1.0
CHROMA_CUTOFF = 0.5
VERTEX_COLOR_ATTRIBUTE = "vertex_colors"
SPHERE_MAP_GROUP_NAME = "EQG Sphere Map"
PALETTE_MASK_GROUP_NAME = "EQG Palette Mask"
PALETTE_MASK_GROUP_VERSION = 2

ALPHA_MODES = [
    "Opaque",
    "Alpha",
    "AddAlpha",
    "Chroma",
]

SHADER_GROUPS = [
    "Basic",
    "Basic_2UV",
    "Bump",
    "Bump_2UV",
    "Bump/Shine",
    "Glow",
    "Bump/Shine/Glow",
    "Bump/Shine/Glow_2UV",
    "Bump/Shine/Glow/Environment",
    "Environment",
    "Detail Palette",
    "CBST2_2UV",
    "MPLBump",
    "MPLBump2UV",
    "MPLBlend",
    "MPLBlendNoBump",
    "MPLFull",
    "MPLFull2UV",
    "MPLReflection",
    "MPLReflection2UV",
    "MPLGlow",
    "MPLGlow2UV",
    "MPLShine",
    "MPLShine2UV",
    "Terrain",
    "Water",
    "Lava",
    "Lava2",
]

SHADERS_BY_MODE = {
    "Alpha": [
        "C1",
        "CB1",
        "CBS1",
        "CBSG1",
        "CG1",
        "CE1",
        "CBSGE1",
        "MPLBasic",
        "MPLBump",
    ],

    "AddAlpha": [
        "C1",
        "CG1",
        "CE1",
        "CB1",
        "CBS1",
        "CBSG1",
        "CBSGE1",
    ],

    "Chroma": [
        "C1",
        "CG1",
        "CE1",
        "CB1",
        "CBS1",
        "CBSG1",
        "CBSGE1",
        "MPLBasic",
        "MPLBump",
    ],
}

@dataclass(frozen=True)
class ShaderFamily:

    # Drives node arrangement.
    group: str

    # Property names supported by this shader family.
    properties: tuple[str]


SHADER_FAMILIES: Dict[str, ShaderFamily] = {


    "C1": ShaderFamily(group="Basic", properties=["e_TextureDiffuse0"]),
    "C1_2UV": ShaderFamily(group="Basic_2UV", properties=["e_TextureDiffuse0", "e_TextureSecond0"]),
    "CB1": ShaderFamily(group="Bump", properties=["e_TextureDiffuse0", "e_TextureNormal0"]),

    "CB1_2UV": ShaderFamily(
        group="Bump_2UV",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureSecond0",
        ],
    ),

    "CBS1": ShaderFamily(
        group="Bump/Shine",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_fShininess0",
        ],
    ),

    "CBSG1": ShaderFamily(
        group="Bump/Shine/Glow",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_fShininess0",
        ],
    ),

    "CBSG1_2UV": ShaderFamily(
        group="Bump/Shine/Glow_2UV",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureSecond0",
            "e_fShininess0",
        ],
    ),

    "CBGG1": ShaderFamily(
        group="Bump/Shine/Glow",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_fShininess0",
            "e_fBumpiness0",
        ],
    ),

    "CBSGE1": ShaderFamily(
        group="Bump/Shine/Glow/Environment",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureEnvironment0",
            "e_fEnvMapStrength0",
            "e_fShininess0",
        ],
    ),

    "CBGGE1": ShaderFamily(
        group="Bump/Shine/Glow/Environment",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureEnvironment0",
            "e_fEnvMapStrength0",
            "e_fShininess0",
        ],
    ),

    "CE1": ShaderFamily(
        group="Environment",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureEnvironment",
            "e_fEnvMapStrength0",
        ],
    ),

    "CG1": ShaderFamily(group="Glow", properties=["e_TextureDiffuse0", "e_TextureGlow0"]),
    "CSG1": ShaderFamily(group="Basic", properties=["e_TextureDiffuse0"]),

    "C1DTP": ShaderFamily(
        group="Detail Palette",
        properties=[
            "e_TexturePalette0",
            "e_TextureDiffuse0",
            "e_TextureDetail0",
            "e_fScale0",
            "e_fGrassDensity0",
            "e_TextureDetail1",
            "e_fScale1",
            "e_fGrassDensity1",
            "e_TextureDetail2",
            "e_fScale2",
            "e_fGrassDensity2",
            "e_TextureDetail3",
            "e_fScale3",
            "e_fGrassDensity3",
            "e_TextureDetail4",
            "e_fScale4",
            "e_fGrassDensity4",
            "e_TextureDetail5",
            "e_fScale5",
            "e_fGrassDensity5",
            "e_TextureDetail6",
            "e_fScale6",
            "e_fGrassDensity6",
            "e_TextureDetail7",
            "e_fScale7",
            "e_fGrassDensity7",
            "e_TextureDetail8",
            "e_fScale8",
            "e_fGrassDensity8",
            "e_TextureDetail9",
            "e_fScale9",
            "e_fGrassDensity9",
        ],
    ),

    "CBST2_2UV": ShaderFamily(
        group="CBST2_2UV",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureDiffuse1",
            "e_TextureNormal1",
            "e_fShininess0",
        ],
    ),

    "MPLBasic": ShaderFamily(group="Basic", properties=["e_TextureDiffuse0"]),
    "MPLBasicA": ShaderFamily(group="Basic", properties=["e_TextureDiffuse0"]),
    "MPLBasicAT": ShaderFamily(group="Basic", properties=["e_TextureDiffuse0"]),

    "MPLBump": ShaderFamily(
        group="MPLBump",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureCoverage0",
            "e_fCoverageScale0",
        ],
    ),

    "MPLBumpA": ShaderFamily(
        group="MPLBump",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureCoverage0",
            "e_fCoverageScale0",
        ],
    ),

    "MPLBumpAT": ShaderFamily(
        group="MPLBump",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureCoverage0",
            "e_fCoverageScale0",
        ],
    ),

    "MPLBump2UV": ShaderFamily(
        group="MPLBump2UV",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureCoverage0",
        ],
    ),

    "MPLBlend": ShaderFamily(
        group="MPLBlend",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureDiffuse1",
            "e_TextureNormal0",
            "e_TextureNormal1",
            "e_TextureCoverage0",
            "e_fCoverageScale0",
            "e_fShininess0",
        ],
    ),

    "MPLBlendNoBump": ShaderFamily(
        group="MPLBlendNoBump",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureCoverage0",
            "e_fCoverageScale0",
            "e_fShininess0",
        ],
    ),

    "MPLFull": ShaderFamily(
        group="MPLFull",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureCoverage0",
            "e_fCoverageScale0",
        ],
    ),

    "MPLFull2UV": ShaderFamily(
        group="MPLFull2UV",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureCoverage0",
        ],
    ),

    "MPLRB": ShaderFamily(
        group="MPLReflection",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureCoverage0",
            "e_fCoverageScale0",
            "e_TextureEnvironment0",
            "e_fEnvMapStrength0",
        ],
    ),

    "MPLRB2UV": ShaderFamily(
        group="MPLReflection2UV",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureNormal0",
            "e_TextureCoverage0",
            "e_fCoverageScale0",
            "e_TextureEnvironment0",
            "e_fEnvMapStrength0",
        ],
    ),

    "MPLGB": ShaderFamily(
        group="MPLGlow",
        properties=[
            "e_TextureNormal0",
            "e_TextureCoverage0",
            "e_fCoverageScale0",
            "e_TextureDiffuse0",
        ],
    ),

    "MPLGB2UV": ShaderFamily(
        group="MPLGlow2UV",
        properties=[
            "e_TextureNormal0",
            "e_TextureCoverage0",
            "e_fCoverageScale0",
            "e_TextureDiffuse0",
        ],
    ),

    "MPLSB": ShaderFamily(
        group="MPLShine",
        properties=[
            "e_TextureNormal0",
            "e_TextureCoverage0",
            "e_fCoverageScale0",
            "e_TextureDiffuse0",
            "e_fShininess0",
        ],
    ),

    "MPLSB2UV": ShaderFamily(
        group="MPLShine2UV",
        properties=[
            "e_TextureNormal0",
            "e_TextureCoverage0",
            "e_fCoverageScale0",
            "e_TextureDiffuse0",
            "e_fShininess0",
        ],
    ),

    "Terrain": ShaderFamily(
        group="Terrain",
        properties=[
            "e_TextureCoverage",
            "e_fCoverageScale",
            "e_TextureFallback",
            "e_TextureDetail1",
            "e_TextureDetail2",
        ],
    ),

    "Water": ShaderFamily(
        group="Water",
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
        group="Waterfall",
        properties=[
            "e_TextureDiffuse0",
            "e_fSlide1X",
            "e_fSlide1Y",
            "e_fSlide2X",
            "e_fSlide2Y",
        ],
    ),

    "Lava": ShaderFamily(
        group="Lava",
        properties=[
            "e_TextureDiffuse0",
            "e_TextureDiffuse1",
            "e_TextureNormal0",
            "e_fSlide1X",
            "e_fSlide1Y",
            "e_fSlide2X",
            "e_fSlide2Y",
        ],
    ),

    "Lava2": ShaderFamily(
        group="Lava2",
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

@dataclass(frozen=True, slots=True)
class ParsedShaderTag:
    alpha_mode: str
    shader: str


# These bypass ordinary alpha/shader classification.
# Overlapping names must be checked longest first.
SPECIAL_SHADER_RULES: tuple[tuple[str, str], ...] = (
    ("WaterFall", "WaterFall"),
    ("Water", "Water"),
    ("Terrain", "Terrain"),
    ("Lava2", "Lava2"),
    ("Lava", "Lava"),
    ("C1DTP", "C1DTP"),
)


OPAQUE_SHADER_RULES: tuple[tuple[str, str], ...] = (
    # Longer overlapping names first.
    ("CBST2_2UV", "CBST2_2UV"),
    ("CBSG1_2UV", "CBSG1_2UV"),
    ("CB1_2UV", "CB1_2UV"),
    ("C1_2UV", "C1_2UV"),
    ("CBS_2UV", "CBS_2UV"),

    ("MPLBlendNoBump", "MPLBlendNoBump"),
    ("MPLFull2UV", "MPLFull2UV"),
    ("MPLBump2UV", "MPLBump2UV"),
    ("MPLSB2UV", "MPLSB2UV"),
    ("MPLGB2UV", "MPLGB2UV"),
    ("MPLRB2UV", "MPLRB2UV"),

    ("MPLBasic", "MPLBasic"),
    ("MPLBlend", "MPLBlend"),
    ("MPLFull", "MPLFull"),
    ("MPLBump", "MPLBump"),
    ("MPLSB", "MPLSB"),
    ("MPLGB", "MPLGB"),
    ("MPLRB", "MPLRB"),

    # Aliases used by the same client shader classification.
    ("CBSGE1", "CBSGE1"),
    ("CBGGE1", "CBSGE1"),
    ("CBSE1", "CBSGE1"),
    ("CBE1", "CBSGE1"),

    ("CBSG1", "CBSG1"),
    ("CBGG1", "CBSG1"),

    ("VSB", "VSB"),
    ("CBS1", "CBS1"),
    ("CB1", "CB1"),
    ("CE1", "CE1"),
    ("CG1", "CG1"),
)


CHROMA_SHADER_RULES: tuple[tuple[str, str], ...] = (
    ("MPLBasic", "MPLBasic"),
    ("MPLBump", "MPLBump"),

    ("CBSGE1", "CBSGE1"),
    ("CBGGE1", "CBSGE1"),
    ("CBSE1", "CBSGE1"),
    ("CBE1", "CBSGE1"),

    ("CBSG1", "CBSG1"),
    ("CBGG1", "CBSG1"),

    ("VSB", "VSB"),
    ("CBS1", "CBS1"),
    ("CB1", "CB1"),
    ("CE1", "CE1"),
    ("CG1", "CG1"),
)


ALPHA_SHADER_RULES: tuple[tuple[str, str], ...] = (
    ("MPLBasic", "MPLBasic"),
    ("MPLBump", "MPLBump"),

    ("CBSGE1", "CBSGE1"),
    ("CBGGE1", "CBSGE1"),
    ("CBSE1", "CBSGE1"),
    ("CBE1", "CBSGE1"),

    ("CBSG1", "CBSG1"),
    ("CBGG1", "CBSG1"),

    ("CBS1", "CBS1"),
    ("CB1", "CB1"),
    ("CE1", "CE1"),
    ("CG1", "CG1"),
)


ADD_ALPHA_SHADER_RULES: tuple[tuple[str, str], ...] = (
    ("CBSGE1", "CBSGE1"),
    ("CBGGE1", "CBSGE1"),
    ("CBSE1", "CBSGE1"),
    ("CBE1", "CBSGE1"),

    ("CBSG1", "CBSG1"),
    ("CBGG1", "CBSG1"),

    ("CBS1", "CBS1"),
    ("CB1", "CB1"),
    ("CE1", "CE1"),
    ("CG1", "CG1"),
)


SHADER_RULES_BY_ALPHA_MODE = {
    "Opaque": OPAQUE_SHADER_RULES,
    "Alpha": ALPHA_SHADER_RULES,
    "AddAlpha": ADD_ALPHA_SHADER_RULES,
    "Chroma": CHROMA_SHADER_RULES,
}


def parse_shader_tag(shadertag: str) -> tuple[str, str]:
    """Return (alpha_mode, shader) using client-style precedence."""

    special_shader: str | None = None

    # Special shader classification takes priority over ordinary shaders.
    for marker, shader in SPECIAL_SHADER_RULES:
        if marker in shadertag:
            special_shader = shader
            break

    # Alpha mode is classified independently.
    if "AddAlpha" in shadertag:
        alpha_mode = "AddAlpha"
    elif "Alpha" in shadertag:
        alpha_mode = "Alpha"
    elif "Chroma" in shadertag:
        alpha_mode = "Chroma"
    else:
        alpha_mode = "Opaque"

    if special_shader is not None:
        return alpha_mode, special_shader

    for marker, shader in SHADER_RULES_BY_ALPHA_MODE[alpha_mode]:
        if marker in shadertag:
            return alpha_mode, shader

    return alpha_mode, "C1"

@dataclass
class BuildResult:
    """Sockets produced by a shader-group builder."""

    color: NodeSocket
    alpha: Optional[NodeSocket] = None
    emission_color: Optional[NodeSocket] = None
    emission_strength: Optional[NodeSocket] = None


class MaterialNodeBuilder:
    """Small, Blender-API-oriented helper used by the group recipes."""

    def __init__(
        self,
        material: Material,
        shader: str,
        uv_scale: float = DEFAULT_UV_SCALE,
    ) -> None:
        if material.node_tree is None:
            raise ValueError("Material has no node tree")

        self.material = material
        self.shader = shader
        self.uv_scale = uv_scale
        self.tree: NodeTree = material.node_tree
        self.nodes = self.tree.nodes
        self.links = self.tree.links
        self.properties = material.quail_eqgmaterialdef

        self.bsdf = self.nodes.new("ShaderNodeBsdfPrincipled")
        self.bsdf.name = "Principled BSDF"
        self.bsdf.label = "Principled BSDF"
        self.bsdf.location = (700, 100)

        self.output = self.nodes.new("ShaderNodeOutputMaterial")
        self.output.name = "Material Output"
        self.output.location = (1050, 100)

        self._uv_sockets: dict[tuple[str, float], NodeSocket] = {}
        self._vertex_color_node: Optional[Node] = None
        self._next_texture_y = 500

    # ------------------------------------------------------------------
    # Material values and images
    # ------------------------------------------------------------------

    def value(self, name: str, default: Any = None) -> Any:
        value = getattr(self.properties, name, default)
        if value in (None, ""):
            return default
        return value

    def float_value(self, name: str, default: float = 0.0) -> float:
        value = self.value(name, default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def value_node(self, label: str, value: float, location=(-900, -700)) -> NodeSocket:
        node = self.nodes.new("ShaderNodeValue")
        node.label = label
        node.name = self.unique_name(label)
        node.location = location
        node.outputs[0].default_value = value
        return node.outputs[0]

    def find_or_load_image(self, property_name: str) -> Image:
        texture_path = self.value(property_name)
        if not texture_path:
            raise ValueError(f"{property_name} has no texture path")

        if isinstance(texture_path, Image):
            return texture_path

        texture_path = str(texture_path)
        image = bpy.data.images.get(texture_path)
        if image is None:
            image = bpy.data.images.get(os.path.basename(texture_path))
        if image is None:
            image = bpy.data.images.load(texture_path, check_existing=True)

        return image

    def texture(
        self,
        property_name: str,
        label: str,
        vector: Optional[NodeSocket] = None,
        *,
        non_color: bool = False,
        interpolation: str = "Linear",
    ) -> Node:
        node = self.nodes.new("ShaderNodeTexImage")
        node.name = self.unique_name(label)
        node.label = label
        node.location = (-950, self._next_texture_y)
        self._next_texture_y -= 260
        node.image = self.find_or_load_image(property_name)
        node.interpolation = interpolation
        node.extension = "REPEAT"

        if non_color and node.image is not None:
            try:
                node.image.colorspace_settings.name = "Non-Color"
            except TypeError:
                pass

        if vector is not None:
            self.links.new(vector, node.inputs["Vector"])
        return node

    # ------------------------------------------------------------------
    # Coordinates and attributes
    # ------------------------------------------------------------------

    def uv(self, layer_name: str, scale: Optional[float] = None) -> NodeSocket:
        if scale is None:
            scale = self.uv_scale

        key = (layer_name, float(scale))
        cached = self._uv_sockets.get(key)
        if cached is not None:
            return cached

        uv_node = self.nodes.new("ShaderNodeUVMap")
        uv_node.name = self.unique_name(layer_name)
        uv_node.label = layer_name
        uv_node.uv_map = layer_name
        uv_node.location = (-1500, 500 - len(self._uv_sockets) * 220)

        if math.isclose(scale, 1.0):
            result = uv_node.outputs["UV"]
        else:
            scale_node = self.nodes.new("ShaderNodeVectorMath")
            scale_node.name = self.unique_name(f"{layer_name} Scale")
            scale_node.label = f"{layer_name} × {scale:g}"
            scale_node.operation = "SCALE"
            scale_node.location = (-1280, uv_node.location.y)
            scale_node.inputs[3].default_value = scale
            self.links.new(uv_node.outputs["UV"], scale_node.inputs[0])
            result = scale_node.outputs["Vector"]

        self._uv_sockets[key] = result
        return result

    def scaled_vector(
        self,
        vector: NodeSocket,
        scale: float | NodeSocket,
        label: str,
    ) -> NodeSocket:
        node = self.nodes.new("ShaderNodeVectorMath")
        node.name = self.unique_name(label)
        node.label = label
        node.operation = "SCALE"
        self.links.new(vector, node.inputs[0])
        if isinstance(scale, NodeSocket):
            self.links.new(scale, node.inputs[3])
        else:
            node.inputs[3].default_value = float(scale)
        return node.outputs["Vector"]

    def vertex_color(self) -> Node:
        if self._vertex_color_node is None:
            node = self.nodes.new("ShaderNodeVertexColor")
            node.name = "EQG Vertex Color"
            node.label = VERTEX_COLOR_ATTRIBUTE
            node.layer_name = VERTEX_COLOR_ATTRIBUTE
            node.location = (-950, -1050)
            self._vertex_color_node = node
        return self._vertex_color_node

    # ------------------------------------------------------------------
    # Color and scalar operations
    # ------------------------------------------------------------------

    def mix_color(
        self,
        a: NodeSocket,
        b: NodeSocket,
        factor: float | NodeSocket,
        label: str,
        *,
        clamp_factor: bool = False,
    ) -> NodeSocket:
        node = self.nodes.new("ShaderNodeMix")
        node.name = self.unique_name(label)
        node.label = label
        node.data_type = "RGBA"
        if hasattr(node, "clamp_factor"):
            node.clamp_factor = clamp_factor

        if isinstance(factor, NodeSocket):
            self.links.new(factor, node.inputs[0])
        else:
            node.inputs[0].default_value = float(factor)
        self.links.new(a, node.inputs[6])
        self.links.new(b, node.inputs[7])
        return node.outputs[2]

    def multiply_color(
        self,
        a: NodeSocket,
        b: NodeSocket,
        label: str,
        *,
        clamp: bool = False,
    ) -> NodeSocket:
        node = self.nodes.new("ShaderNodeMixRGB")
        node.name = self.unique_name(label)
        node.label = label
        node.blend_type = "MULTIPLY"
        node.inputs["Fac"].default_value = 1.0
        node.use_clamp = clamp
        self.links.new(a, node.inputs["Color1"])
        self.links.new(b, node.inputs["Color2"])
        return node.outputs["Color"]

    def add_color(self, a: NodeSocket, b: NodeSocket, label: str) -> NodeSocket:
        node = self.nodes.new("ShaderNodeMixRGB")
        node.name = self.unique_name(label)
        node.label = label
        node.blend_type = "ADD"
        node.inputs["Fac"].default_value = 1.0
        self.links.new(a, node.inputs["Color1"])
        self.links.new(b, node.inputs["Color2"])
        return node.outputs["Color"]

    def scale_color(
        self,
        color: NodeSocket,
        scale: float | NodeSocket,
        label: str,
        *,
        clamp: bool = False,
    ) -> NodeSocket:
        node = self.nodes.new("ShaderNodeMixRGB")
        node.name = self.unique_name(label)
        node.label = label
        node.blend_type = "MULTIPLY"
        node.inputs["Fac"].default_value = 1.0
        node.use_clamp = clamp
        self.links.new(color, node.inputs["Color1"])
        if isinstance(scale, NodeSocket):
            self.links.new(scale, node.inputs["Color2"])
        else:
            node.inputs["Color2"].default_value = (scale, scale, scale, 1.0)
        return node.outputs["Color"]

    def math(
        self,
        operation: str,
        a: float | NodeSocket,
        b: float | NodeSocket,
        label: str,
        *,
        clamp: bool = False,
    ) -> NodeSocket:
        node = self.nodes.new("ShaderNodeMath")
        node.name = self.unique_name(label)
        node.label = label
        node.operation = operation
        node.use_clamp = clamp
        for index, value in enumerate((a, b)):
            if isinstance(value, NodeSocket):
                self.links.new(value, node.inputs[index])
            else:
                node.inputs[index].default_value = float(value)
        return node.outputs[0]

    def clamp_value(self, value: NodeSocket, label: str) -> NodeSocket:
        node = self.nodes.new("ShaderNodeClamp")
        node.name = self.unique_name(label)
        node.label = label
        node.inputs["Min"].default_value = 0.0
        node.inputs["Max"].default_value = 1.0
        self.links.new(value, node.inputs["Value"])
        return node.outputs["Result"]

    def math_mix(
        self,
        a: NodeSocket,
        b: NodeSocket,
        factor: NodeSocket,
        label: str,
    ) -> NodeSocket:
        """Scalar lerp without clamping the factor."""

        one_minus = self.math("SUBTRACT", 1.0, factor, f"{label}: 1 - Factor")
        left = self.math("MULTIPLY", a, one_minus, f"{label}: A Weight")
        right = self.math("MULTIPLY", b, factor, f"{label}: B Weight")
        return self.math("ADD", left, right, label)

    def legacy_surface(
        self,
        diffuse: Node,
        coverage: Node,
        *,
        use_vertex_tint: bool = True,
    ) -> tuple[NodeSocket, NodeSocket]:
        """Reproduce saturate(2*D*C), then saturate(2*surface*tint)."""

        color = self.multiply_color(
            diffuse.outputs["Color"],
            coverage.outputs["Color"],
            "Diffuse × Coverage",
        )
        color = self.scale_color(color, 2.0, "Diffuse/Coverage × 2", clamp=True)

        alpha = self.math(
            "MULTIPLY",
            diffuse.outputs["Alpha"],
            coverage.outputs["Alpha"],
            "Diffuse Alpha × Coverage Alpha",
        )
        alpha = self.clamp_value(
            self.math("MULTIPLY", alpha, 2.0, "Surface Alpha × 2"),
            "Clamp Surface Alpha",
        )

        if use_vertex_tint:
            vertex_color = self.vertex_color()
            color = self.multiply_color(
                color,
                vertex_color.outputs["Color"],
                "Surface × Vertex RGB",
            )
            color = self.scale_color(color, 2.0, "Tinted Surface × 2", clamp=True)
            alpha = self.math(
                "MULTIPLY",
                alpha,
                vertex_color.outputs["Alpha"],
                "Surface Alpha × Vertex Alpha",
            )
            alpha = self.clamp_value(
                self.math("MULTIPLY", alpha, 2.0, "Tinted Alpha × 2"),
                "Clamp Tinted Alpha",
            )

        return color, alpha

    # ------------------------------------------------------------------
    # Normal, shine, environment and output helpers
    # ------------------------------------------------------------------

    def normal_map(self, color: NodeSocket, label: str = "Normal Map") -> Node:
        node = self.nodes.new("ShaderNodeNormalMap")
        node.name = self.unique_name(label)
        node.label = label
        node.space = "TANGENT"
        self.links.new(color, node.inputs["Color"])
        self.links.new(node.outputs["Normal"], self.bsdf.inputs["Normal"])
        return node

    def packed_normal_color(self, normal_texture: Node, encoded_z: float = 0.95) -> NodeSocket:
        """Use texture R/G as normal X/Y while reserving B for glow."""

        separate = self.nodes.new("ShaderNodeSeparateColor")
        separate.name = self.unique_name("Separate Packed Normal")
        separate.label = "Packed Normal: RG / Glow: B / Shine: A"
        self.links.new(normal_texture.outputs["Color"], separate.inputs["Color"])

        combine = self.nodes.new("ShaderNodeCombineColor")
        combine.name = self.unique_name("Combine Packed Normal")
        combine.label = f"Normal RG + encoded Z {encoded_z:g}"
        combine.inputs["Blue"].default_value = encoded_z
        self.links.new(separate.outputs["Red"], combine.inputs["Red"])
        self.links.new(separate.outputs["Green"], combine.inputs["Green"])
        return combine.outputs["Color"]

    def shininess_to_roughness(self, shininess: float | NodeSocket) -> NodeSocket:
        """Approximate a Blinn-Phong exponent as Principled roughness.

        roughness = sqrt(2 / (shininess + 2))
        """

        add = self.math("ADD", shininess, 2.0, "Shininess + 2")
        divide = self.math("DIVIDE", 2.0, add, "2 / (Shininess + 2)")
        sqrt_node = self.nodes.new("ShaderNodeMath")
        sqrt_node.name = self.unique_name("Shininess to Roughness")
        sqrt_node.label = "sqrt(2 / (Shininess + 2))"
        sqrt_node.operation = "SQRT"
        self.links.new(divide, sqrt_node.inputs[0])
        self.links.new(sqrt_node.outputs[0], self.bsdf.inputs["Roughness"])
        return sqrt_node.outputs[0]

    def sphere_map_vector(self) -> NodeSocket:
        group_tree = get_or_create_sphere_map_group()
        node = self.nodes.new("ShaderNodeGroup")
        node.name = self.unique_name(SPHERE_MAP_GROUP_NAME)
        node.label = SPHERE_MAP_GROUP_NAME
        node.node_tree = group_tree
        node.location = (-1280, -850)
        return node.outputs["Vector"]

    def connect_principled_inputs(self, result: BuildResult) -> None:
        self.links.new(result.color, self.bsdf.inputs["Base Color"])
        if result.emission_color is not None:
            self.links.new(result.emission_color, self.bsdf.inputs["Emission Color"])
        if result.emission_strength is not None:
            self.links.new(result.emission_strength, self.bsdf.inputs["Emission Strength"])

    def finish(self, result: BuildResult, alpha_mode: str, chroma_cutoff: float) -> None:
        self.connect_principled_inputs(result)
        alpha_mode = normalize_alpha_mode(alpha_mode)

        if alpha_mode == "ALPHA":
            if result.alpha is not None:
                self.links.new(result.alpha, self.bsdf.inputs["Alpha"])
            set_transparent_render_method(self.material, chroma=False)
            self.links.new(self.bsdf.outputs["BSDF"], self.output.inputs["Surface"])
            return

        if alpha_mode == "CHROMA":
            if result.alpha is not None:
                threshold = self.math(
                    "GREATER_THAN",
                    result.alpha,
                    chroma_cutoff,
                    "Chroma Alpha Test",
                )
                self.links.new(threshold, self.bsdf.inputs["Alpha"])
            set_transparent_render_method(self.material, chroma=True)
            self.links.new(self.bsdf.outputs["BSDF"], self.output.inputs["Surface"])
            return

        if alpha_mode == "ADDALPHA":
            # Blender has no portable Principled setting equivalent to the
            # legacy framebuffer blend SrcAlpha/One.  Transparent + premultiplied
            # Emission is the closest renderer-independent node approximation.
            emission = self.nodes.new("ShaderNodeEmission")
            emission.name = "AddAlpha Emission"
            emission.label = "AddAlpha approximation"
            self.links.new(result.color, emission.inputs["Color"])
            if result.alpha is not None:
                self.links.new(result.alpha, emission.inputs["Strength"])
            else:
                emission.inputs["Strength"].default_value = 1.0

            transparent = self.nodes.new("ShaderNodeBsdfTransparent")
            transparent.name = "AddAlpha Transparent"

            add_shader = self.nodes.new("ShaderNodeAddShader")
            add_shader.name = "AddAlpha"
            self.links.new(transparent.outputs[0], add_shader.inputs[0])
            self.links.new(emission.outputs[0], add_shader.inputs[1])
            self.links.new(add_shader.outputs[0], self.output.inputs["Surface"])
            set_transparent_render_method(self.material, chroma=False)
            return

        # Opaque and unknown modes remain opaque.
        self.bsdf.inputs["Alpha"].default_value = 1.0
        self.links.new(self.bsdf.outputs["BSDF"], self.output.inputs["Surface"])

    def unique_name(self, base: str) -> str:
        if self.nodes.get(base) is None:
            return base
        index = 2
        while self.nodes.get(f"{base} {index}") is not None:
            index += 1
        return f"{base} {index}"


# ======================================================================
# Shared node groups
# ======================================================================


def _new_group_socket(
    node_group: NodeTree,
    name: str,
    socket_type: str,
    in_out: str,
) -> None:
    node_group.interface.new_socket(name=name, in_out=in_out, socket_type=socket_type)


def get_or_create_sphere_map_group() -> NodeTree:
    existing = bpy.data.node_groups.get(SPHERE_MAP_GROUP_NAME)
    if existing is not None:
        return existing

    group = bpy.data.node_groups.new(SPHERE_MAP_GROUP_NAME, "ShaderNodeTree")
    _new_group_socket(group, "Vector", "NodeSocketVector", "OUTPUT")

    nodes = group.nodes
    links = group.links
    texcoord = nodes.new("ShaderNodeTexCoord")
    separate = nodes.new("ShaderNodeSeparateXYZ")
    add_y = nodes.new("ShaderNodeMath")
    sqrt_y = nodes.new("ShaderNodeMath")
    denominator = nodes.new("ShaderNodeMath")
    divide_x = nodes.new("ShaderNodeMath")
    divide_z = nodes.new("ShaderNodeMath")
    add_u = nodes.new("ShaderNodeMath")
    add_v = nodes.new("ShaderNodeMath")
    combine = nodes.new("ShaderNodeCombineXYZ")
    output = nodes.new("NodeGroupOutput")

    add_y.operation = "ADD"
    add_y.inputs[1].default_value = 1.0
    sqrt_y.operation = "SQRT"
    denominator.operation = "MULTIPLY"
    denominator.inputs[1].default_value = 2.828
    divide_x.operation = "DIVIDE"
    divide_z.operation = "DIVIDE"
    add_u.operation = "ADD"
    add_u.inputs[1].default_value = 0.5
    add_v.operation = "ADD"
    add_v.inputs[1].default_value = 0.5

    texcoord.location = (-900, 0)
    separate.location = (-700, 0)
    add_y.location = (-500, -80)
    sqrt_y.location = (-320, -80)
    denominator.location = (-140, -80)
    divide_x.location = (40, 120)
    divide_z.location = (40, -220)
    add_u.location = (220, 120)
    add_v.location = (220, -220)
    combine.location = (420, 0)
    output.location = (620, 0)

    links.new(texcoord.outputs["Reflection"], separate.inputs["Vector"])
    links.new(separate.outputs["Y"], add_y.inputs[0])
    links.new(add_y.outputs[0], sqrt_y.inputs[0])
    links.new(sqrt_y.outputs[0], denominator.inputs[0])
    links.new(separate.outputs["X"], divide_x.inputs[0])
    links.new(denominator.outputs[0], divide_x.inputs[1])
    links.new(separate.outputs["Z"], divide_z.inputs[0])
    links.new(denominator.outputs[0], divide_z.inputs[1])
    links.new(divide_x.outputs[0], add_u.inputs[0])
    links.new(divide_z.outputs[0], add_v.inputs[0])
    links.new(add_u.outputs[0], combine.inputs["X"])
    links.new(add_v.outputs[0], combine.inputs["Y"])
    links.new(combine.outputs["Vector"], output.inputs["Vector"])
    return group


def create_palette_mask_node_group(
    palette_mask_node_group: NodeTree,
    inner_tolerance: float = 0.002,
    outer_tolerance: float = 0.03,
) -> None:
    """Create a palette-region mask with smooth deterministic edges.

    This replaces UV white-noise jitter with a color-distance mask:

        mask = 1 - smoothstep(inner_tolerance, outer_tolerance,
                              distance(ClrPalette, NdxClr))

    Set the palette Image Texture to Linear interpolation for a soft boundary,
    or Closest for hard indexed regions.  The tolerances can be adjusted after
    inspecting the real palette image; unlike UV jitter, this is stable between
    frames and does not crawl during animation.
    """

    palette_mask_node_group.nodes.clear()
    palette_mask_node_group.interface.clear()
    palette_mask_node_group["eqg_palette_mask_version"] = PALETTE_MASK_GROUP_VERSION

    _new_group_socket(palette_mask_node_group, "ClrPalette", "NodeSocketColor", "INPUT")
    _new_group_socket(palette_mask_node_group, "NdxClr", "NodeSocketColor", "INPUT")
    _new_group_socket(palette_mask_node_group, "Mask", "NodeSocketFloat", "OUTPUT")

    nodes = palette_mask_node_group.nodes
    links = palette_mask_node_group.links
    group_input = nodes.new("NodeGroupInput")
    group_output = nodes.new("NodeGroupOutput")

    distance = nodes.new("ShaderNodeVectorMath")
    distance.operation = "DISTANCE"
    distance.label = "Palette color distance"

    mask = nodes.new("ShaderNodeMapRange")
    mask.interpolation_type = "SMOOTHERSTEP"
    mask.clamp = True
    mask.label = "Smooth palette boundary"
    mask.inputs["From Min"].default_value = inner_tolerance
    mask.inputs["From Max"].default_value = outer_tolerance
    mask.inputs["To Min"].default_value = 1.0
    mask.inputs["To Max"].default_value = 0.0

    group_input.location = (-600, 0)
    distance.location = (-380, 180)
    mask.location = (-160, 180)
    group_output.location = (100, 180)

    links.new(group_input.outputs["ClrPalette"], distance.inputs[0])
    links.new(group_input.outputs["NdxClr"], distance.inputs[1])
    links.new(distance.outputs["Value"], mask.inputs["Value"])
    links.new(mask.outputs["Result"], group_output.inputs["Mask"])


def get_or_create_palette_mask_group() -> NodeTree:
    group = bpy.data.node_groups.get(PALETTE_MASK_GROUP_NAME)
    if group is None:
        group = bpy.data.node_groups.new(PALETTE_MASK_GROUP_NAME, "ShaderNodeTree")
    if group.get("eqg_palette_mask_version") != PALETTE_MASK_GROUP_VERSION:
        create_palette_mask_node_group(group)
    return group


# ======================================================================
# Verified shader-group recipes
# ======================================================================


def _basic(builder: MaterialNodeBuilder) -> BuildResult:
    uv0 = builder.uv("UVMap")
    diffuse = builder.texture("e_TextureDiffuse0", "Diffuse 0", uv0)
    color = diffuse.outputs["Color"]

    # MPL vertex RGB is an explicit material tint.  The C-family vertex color
    # participates in legacy lighting instead and is left to Blender lighting.
    if builder.shader.startswith("MPL"):
        color = builder.multiply_color(
            color,
            builder.vertex_color().outputs["Color"],
            "Diffuse × Vertex RGB",
        )
    return BuildResult(color=color, alpha=diffuse.outputs["Alpha"])


def _basic_2uv(builder: MaterialNodeBuilder) -> BuildResult:
    uv0 = builder.uv("UVMap")
    uv1 = builder.uv("UVMap2")
    diffuse = builder.texture("e_TextureDiffuse0", "Diffuse 0", uv0)
    second = builder.texture("e_TextureSecond0", "Second 0", uv1)
    color = builder.multiply_color(
        diffuse.outputs["Color"], second.outputs["Color"], "Diffuse × Second"
    )
    alpha = builder.math(
        "MULTIPLY",
        diffuse.outputs["Alpha"],
        second.outputs["Alpha"],
        "Diffuse Alpha × Second Alpha",
    )
    return BuildResult(color=color, alpha=alpha)


def _bump(builder: MaterialNodeBuilder) -> BuildResult:
    uv0 = builder.uv("UVMap")
    diffuse = builder.texture("e_TextureDiffuse0", "Diffuse 0", uv0)
    normal = builder.texture("e_TextureNormal0", "Normal 0", uv0, non_color=True)
    builder.normal_map(normal.outputs["Color"])
    return BuildResult(diffuse.outputs["Color"], diffuse.outputs["Alpha"])


def _bump_2uv(builder: MaterialNodeBuilder) -> BuildResult:
    uv0 = builder.uv("UVMap")
    uv1 = builder.uv("UVMap2")
    diffuse = builder.texture("e_TextureDiffuse0", "Diffuse 0", uv0)
    second = builder.texture("e_TextureSecond0", "Second 0", uv1)
    normal = builder.texture("e_TextureNormal0", "Normal 0", uv0, non_color=True)
    builder.normal_map(normal.outputs["Color"])
    color = builder.multiply_color(
        diffuse.outputs["Color"], second.outputs["Color"], "Diffuse × Second"
    )
    alpha = builder.math(
        "MULTIPLY",
        diffuse.outputs["Alpha"],
        second.outputs["Alpha"],
        "Diffuse Alpha × Second Alpha",
    )
    return BuildResult(color, alpha)


def _bump_shine(builder: MaterialNodeBuilder) -> BuildResult:
    uv0 = builder.uv("UVMap")
    diffuse = builder.texture("e_TextureDiffuse0", "Diffuse 0", uv0)
    normal = builder.texture("e_TextureNormal0", "Normal/Shine 0", uv0, non_color=True)
    builder.normal_map(normal.outputs["Color"])
    builder.links.new(normal.outputs["Alpha"], builder.bsdf.inputs["Specular IOR Level"])
    builder.shininess_to_roughness(builder.float_value("e_fShininess0", 12.0))
    return BuildResult(diffuse.outputs["Color"], diffuse.outputs["Alpha"])


def _glow(builder: MaterialNodeBuilder) -> BuildResult:
    uv0 = builder.uv("UVMap")
    diffuse = builder.texture("e_TextureDiffuse0", "Diffuse 0", uv0)
    glow = builder.texture("e_TextureGlow0", "Glow 0", uv0)
    emission = builder.multiply_color(
        diffuse.outputs["Color"], glow.outputs["Color"], "Diffuse × Glow"
    )
    return BuildResult(
        color=diffuse.outputs["Color"],
        alpha=diffuse.outputs["Alpha"],
        emission_color=emission,
        emission_strength=builder.value_node("Emission Strength", 1.0),
    )


def _bump_shine_glow(builder: MaterialNodeBuilder, two_uv: bool = False) -> BuildResult:
    uv0 = builder.uv("UVMap")
    diffuse = builder.texture("e_TextureDiffuse0", "Diffuse 0", uv0)
    surface_color = diffuse.outputs["Color"]
    surface_alpha = diffuse.outputs["Alpha"]

    if two_uv:
        second = builder.texture("e_TextureSecond0", "Second 0", builder.uv("UVMap2"))
        surface_color = builder.multiply_color(
            surface_color, second.outputs["Color"], "Diffuse × Second"
        )
        surface_alpha = builder.math(
            "MULTIPLY",
            surface_alpha,
            second.outputs["Alpha"],
            "Diffuse Alpha × Second Alpha",
        )

    normal = builder.texture(
        "e_TextureNormal0", "Packed Normal/Glow/Shine", uv0, non_color=True
    )
    packed_normal = builder.packed_normal_color(normal, encoded_z=0.95)
    builder.normal_map(packed_normal)
    builder.links.new(normal.outputs["Alpha"], builder.bsdf.inputs["Specular IOR Level"])
    builder.shininess_to_roughness(builder.float_value("e_fShininess0", 12.0))

    separate = builder.nodes.new("ShaderNodeSeparateColor")
    separate.name = builder.unique_name("Separate Glow")
    separate.label = "Normal B = Glow"
    builder.links.new(normal.outputs["Color"], separate.inputs["Color"])

    return BuildResult(
        color=surface_color,
        alpha=surface_alpha,
        emission_color=surface_color,
        emission_strength=separate.outputs["Blue"],
    )


def _environment(builder: MaterialNodeBuilder) -> BuildResult:
    uv0 = builder.uv("UVMap")
    diffuse = builder.texture("e_TextureDiffuse0", "Diffuse 0", uv0)
    property_name = (
        "e_TextureEnvironment0"
        if builder.value("e_TextureEnvironment0")
        else "e_TextureEnvironment"
    )
    environment = builder.texture(
        property_name,
        "Environment",
        builder.sphere_map_vector(),
    )
    environment_scale = builder.float_value("e_fEnvMapStrength0", 1.0) * 0.25
    environment_color = builder.scale_color(
        environment.outputs["Color"], environment_scale, "Environment × Strength × 0.25"
    )
    color = builder.add_color(diffuse.outputs["Color"], environment_color, "Diffuse + Environment")
    return BuildResult(color, diffuse.outputs["Alpha"])


def _bump_shine_glow_environment(builder: MaterialNodeBuilder) -> BuildResult:
    uv0 = builder.uv("UVMap")
    diffuse = builder.texture("e_TextureDiffuse0", "Diffuse 0", uv0)
    normal = builder.texture(
        "e_TextureNormal0", "Packed Normal/Glow/Shine", uv0, non_color=True
    )
    property_name = (
        "e_TextureEnvironment0"
        if builder.value("e_TextureEnvironment0")
        else "e_TextureEnvironment"
    )
    environment = builder.texture(
        property_name,
        "Environment",
        builder.sphere_map_vector(),
    )

    environment_color = builder.scale_color(
        environment.outputs["Color"],
        builder.float_value("e_fEnvMapStrength0", 1.0) * 0.25,
        "Environment × Strength × 0.25",
    )
    color = builder.add_color(diffuse.outputs["Color"], environment_color, "Diffuse + Environment")

    builder.normal_map(builder.packed_normal_color(normal, encoded_z=0.95))
    builder.links.new(normal.outputs["Alpha"], builder.bsdf.inputs["Specular IOR Level"])
    builder.shininess_to_roughness(builder.float_value("e_fShininess0", 12.0))

    separate = builder.nodes.new("ShaderNodeSeparateColor")
    separate.name = builder.unique_name("Separate Glow")
    separate.label = "Normal B = Glow"
    builder.links.new(normal.outputs["Color"], separate.inputs["Color"])
    return BuildResult(
        color=color,
        alpha=diffuse.outputs["Alpha"],
        emission_color=color,
        emission_strength=separate.outputs["Blue"],
    )


def _cbst2_2uv(builder: MaterialNodeBuilder) -> BuildResult:
    # The supplied SkinMesh shader passes both UV sets through without a /256
    # operation.  This is also 1.0 for the already-normalized WCE importer.
    uv0 = builder.uv("UVMap", scale=1.0)
    uv1 = builder.uv("UVMap2", scale=1.0)
    diffuse0 = builder.texture("e_TextureDiffuse0", "Diffuse 0", uv0)
    diffuse1 = builder.texture("e_TextureDiffuse1", "Diffuse 1", uv1)
    normal0 = builder.texture("e_TextureNormal0", "Normal/Shine 0", uv0, non_color=True)
    normal1 = builder.texture("e_TextureNormal1", "Normal/Shine 1", uv1, non_color=True)
    factor = diffuse1.outputs["Alpha"]

    diffuse_mix = builder.mix_color(
        diffuse0.outputs["Color"],
        diffuse1.outputs["Color"],
        factor,
        "Diffuse 0/1 Layer",
        clamp_factor=False,
    )
    normal_mix = builder.mix_color(
        normal0.outputs["Color"],
        normal1.outputs["Color"],
        factor,
        "Normal 0/1 Layer",
        clamp_factor=False,
    )
    builder.normal_map(normal_mix)

    shine_mix = builder.math_mix(
        normal0.outputs["Alpha"], normal1.outputs["Alpha"], factor, "Shine 0/1 Layer"
    )
    builder.links.new(shine_mix, builder.bsdf.inputs["Specular IOR Level"])
    builder.shininess_to_roughness(builder.float_value("e_fShininess0", 12.0))
    return BuildResult(diffuse_mix, None)


def _detail_palette(builder: MaterialNodeBuilder) -> BuildResult:
    """Build the EQG detail-palette material using the S3D material recipe.

    The EQG property list has no explicit per-detail palette-index property.
    By default, ``e_TextureDetail0`` uses BMP palette entry 0, Detail1 uses
    entry 1, and so forth.  A material can override this by storing an integer
    array custom property named ``detail_palette_indices``.

    ``e_fGrassDensityN`` is intentionally not used by this surface material.
    It describes grass/detail placement rather than the sampled surface color.
    """

    uv0 = builder.uv("UVMap")
    diffuse = builder.texture("e_TextureDiffuse0", "Diffuse 0", uv0)
    palette = builder.texture(
        "e_TexturePalette0",
        "Palette Regions",
        uv0,
        non_color=True,
        interpolation="Linear",
    )

    if palette.image is None or "bmp_palette" not in palette.image:
        raise ValueError(
            "Detail Palette requires e_TexturePalette0 image['bmp_palette']"
        )

    bmp_palette = palette.image["bmp_palette"]
    palette_indices = builder.material.get("detail_palette_indices", [])
    palette_mask_group = get_or_create_palette_mask_group()
    accumulated_color: Optional[NodeSocket] = None
    accumulated_mask: Optional[NodeSocket] = None

    for detail_index in range(10):
        texture_property = f"e_TextureDetail{detail_index}"
        if not builder.value(texture_property):
            continue

        detail_scale = builder.float_value(f"e_fScale{detail_index}", 1.0)
        detail_uv = builder.scaled_vector(
            uv0,
            detail_scale * 10.0,
            f"Detail {detail_index} UV Scale",
        )
        detail = builder.texture(
            texture_property,
            f"Detail {detail_index}",
            detail_uv,
        )

        if detail_index < len(palette_indices):
            palette_index = int(palette_indices[detail_index])
        else:
            palette_index = detail_index

        if palette_index < 0 or palette_index >= len(bmp_palette):
            raise ValueError(
                f"Detail {detail_index} palette index {palette_index} is outside "
                f"the {len(bmp_palette)}-entry BMP palette"
            )

        red, green, blue = bmp_palette[palette_index]
        index_color = builder.nodes.new("ShaderNodeRGB")
        index_color.name = builder.unique_name(f"Detail {detail_index} Palette Color")
        index_color.label = f"Palette index {palette_index}"
        index_color.outputs[0].default_value = (
            red / 255.0,
            green / 255.0,
            blue / 255.0,
            1.0,
        )

        mask_node = builder.nodes.new("ShaderNodeGroup")
        mask_node.name = builder.unique_name(f"Detail {detail_index} Palette Mask")
        mask_node.label = f"Detail {detail_index} Palette Mask"
        mask_node.node_tree = palette_mask_group
        builder.links.new(palette.outputs["Color"], mask_node.inputs["ClrPalette"])
        builder.links.new(index_color.outputs["Color"], mask_node.inputs["NdxClr"])
        detail_mask = mask_node.outputs["Mask"]

        weighted_detail = builder.scaled_vector(
            detail.outputs["Color"],
            detail_mask,
            f"Detail {detail_index} × Palette Mask",
        )

        if accumulated_color is None:
            accumulated_color = weighted_detail
            accumulated_mask = detail_mask
        else:
            accumulated_color = builder.add_color(
                accumulated_color,
                weighted_detail,
                f"Accumulate Detail {detail_index}",
            )
            accumulated_mask = builder.math(
                "ADD",
                accumulated_mask,
                detail_mask,
                f"Accumulate Mask {detail_index}",
            )

    if accumulated_color is None or accumulated_mask is None:
        return BuildResult(diffuse.outputs["Color"], diffuse.outputs["Alpha"])

    # Smooth palette masks can overlap at region boundaries.  Normalize the
    # weighted color by the total mask so overlapping details crossfade without
    # creating bright seams or depending on the order in which they were added.
    safe_mask = builder.math(
        "MAXIMUM",
        accumulated_mask,
        0.0001,
        "Palette Mask Maximum",
    )
    inverse_mask = builder.math(
        "DIVIDE",
        1.0,
        safe_mask,
        "Palette Mask Reciprocal",
    )
    normalized_detail = builder.scaled_vector(
        accumulated_color,
        inverse_mask,
        "Normalize Palette Details",
    )

    detail_coverage = builder.clamp_value(
        accumulated_mask,
        "Palette Detail Coverage",
    )
    detail_factor = builder.math(
        "MULTIPLY",
        detail_coverage,
        0.5,
        "Palette Detail Strength",
    )

    # Preserve the S3D material's 50% detail strength, but only inside palette
    # regions.  Pixels outside every selected region retain the full base color.
    color = builder.mix_color(
        diffuse.outputs["Color"],
        normalized_detail,
        detail_factor,
        "Diffuse / Palette Detail",
    )
    return BuildResult(color, diffuse.outputs["Alpha"])


def _mpl_bump(builder: MaterialNodeBuilder, coverage_uses_uv2: bool = False) -> BuildResult:
    uv0 = builder.uv("UVMap")
    diffuse = builder.texture("e_TextureDiffuse0", "Diffuse 0", uv0)
    normal = builder.texture("e_TextureNormal0", "Normal 0", uv0, non_color=True)

    if coverage_uses_uv2:
        coverage_uv = builder.uv("UVMap2")
    else:
        coverage_scale = builder.value_node(
            "Coverage Scale", builder.float_value("e_fCoverageScale0", 1.0)
        )
        coverage_uv = builder.scaled_vector(uv0, coverage_scale, "Coverage UV Scale")

    coverage = builder.texture(
        "e_TextureCoverage0", "Coverage 0", coverage_uv, non_color=True
    )
    color, alpha = builder.legacy_surface(diffuse, coverage, use_vertex_tint=True)
    builder.normal_map(normal.outputs["Color"])
    return BuildResult(color, alpha)


def _mpl_blend(builder: MaterialNodeBuilder, use_normal: bool = True) -> BuildResult:
    uv0 = builder.uv("UVMap")
    uv1 = builder.uv("UVMap2")
    separate = builder.nodes.new("ShaderNodeSeparateXYZ")
    separate.name = "Separate UVMap2"
    separate.label = "UVMap2 X controls blend"
    builder.links.new(uv1, separate.inputs["Vector"])
    factor = builder.math("SUBTRACT", 1.0, separate.outputs["X"], "1 - UVMap2.X")

    diffuse0 = builder.texture("e_TextureDiffuse0", "Diffuse 0", uv0)
    diffuse1 = builder.texture("e_TextureDiffuse1", "Diffuse 1", uv0)
    diffuse_mix = builder.mix_color(
        diffuse0.outputs["Color"],
        diffuse1.outputs["Color"],
        factor,
        "Diffuse Layer Blend",
        clamp_factor=False,
    )

    coverage_scale = builder.value_node(
        "Coverage Scale", builder.float_value("e_fCoverageScale0", 1.0)
    )
    coverage_uv = builder.scaled_vector(uv0, coverage_scale, "Coverage UV Scale")
    coverage = builder.texture(
        "e_TextureCoverage0", "Coverage 0", coverage_uv, non_color=True
    )

    color = builder.multiply_color(
        diffuse_mix, coverage.outputs["Color"], "Blended Diffuse × Coverage"
    )
    color = builder.scale_color(color, 2.0, "Covered Diffuse × 2", clamp=True)
    color = builder.multiply_color(
        color,
        builder.vertex_color().outputs["Color"],
        "Surface × Vertex RGB",
    )
    color = builder.scale_color(color, 2.0, "Tinted Surface × 2", clamp=True)

    if use_normal:
        normal0 = builder.texture("e_TextureNormal0", "Normal 0", uv0, non_color=True)
        normal1 = builder.texture("e_TextureNormal1", "Normal 1", uv0, non_color=True)
        normal_mix = builder.mix_color(
            normal0.outputs["Color"],
            normal1.outputs["Color"],
            factor,
            "Normal Layer Blend",
            clamp_factor=False,
        )
        builder.normal_map(normal_mix)
        builder.links.new(
            builder.vertex_color().outputs["Alpha"],
            builder.bsdf.inputs["Specular IOR Level"],
        )
        builder.shininess_to_roughness(builder.float_value("e_fShininess0", 12.0))

    # Both reviewed Region_Blend pixel shaders force output alpha to 1.
    return BuildResult(color, None)


def _mpl_full(builder: MaterialNodeBuilder, coverage_uses_uv2: bool = False) -> BuildResult:
    uv0 = builder.uv("UVMap")
    diffuse = builder.texture("e_TextureDiffuse0", "Diffuse 0", uv0)
    normal = builder.texture("e_TextureNormal0", "Normal 0", uv0, non_color=True)

    if coverage_uses_uv2:
        coverage_uv = builder.uv("UVMap2")
    else:
        coverage_scale = builder.value_node(
            "Coverage Scale", builder.float_value("e_fCoverageScale0", 1.0)
        )
        coverage_uv = builder.scaled_vector(uv0, coverage_scale, "Coverage UV Scale")
    coverage = builder.texture(
        "e_TextureCoverage0", "Coverage 0", coverage_uv, non_color=True
    )

    color, alpha = builder.legacy_surface(diffuse, coverage, use_vertex_tint=True)
    builder.normal_map(normal.outputs["Color"])
    builder.bsdf.inputs["Roughness"].default_value = math.sqrt(2.0 / 14.0)
    builder.links.new(
        builder.vertex_color().outputs["Alpha"],
        builder.bsdf.inputs["Specular IOR Level"],
    )
    return BuildResult(color, alpha)


def _mpl_reflection(builder: MaterialNodeBuilder) -> BuildResult:
    uv0 = builder.uv("UVMap")
    diffuse = builder.texture("e_TextureDiffuse0", "Diffuse 0", uv0)
    normal = builder.texture("e_TextureNormal0", "Normal/Reflection Mask 0", uv0, non_color=True)
    coverage_scale = builder.value_node(
        "Coverage Scale", builder.float_value("e_fCoverageScale0", 1.0)
    )
    coverage_uv = builder.scaled_vector(uv0, coverage_scale, "Coverage UV Scale")
    coverage = builder.texture(
        "e_TextureCoverage0", "Coverage 0", coverage_uv, non_color=True
    )
    environment = builder.texture(
        "e_TextureEnvironment0",
        "Environment 0",
        builder.sphere_map_vector(),
    )

    surface, alpha = builder.legacy_surface(diffuse, coverage, use_vertex_tint=True)
    environment_color = builder.scale_color(
        environment.outputs["Color"],
        builder.float_value("e_fEnvMapStrength0", 1.0),
        "Environment × Strength",
    )
    environment_color = builder.scale_color(
        environment_color,
        normal.outputs["Alpha"],
        "Environment × Normal Alpha",
    )
    color = builder.add_color(surface, environment_color, "Surface + Reflection")
    builder.normal_map(normal.outputs["Color"])
    return BuildResult(color, alpha)


def _unsupported(builder: MaterialNodeBuilder) -> BuildResult:
    raise NotImplementedError(
        f"Shader group for {builder.shader!r} has not been verified yet"
    )


GROUP_BUILDERS: dict[str, Callable[[MaterialNodeBuilder], BuildResult]] = {
    "Basic": _basic,
    "Basic_2UV": _basic_2uv,
    "Bump": _bump,
    "Bump_2UV": _bump_2uv,
    "Bump/Shine": _bump_shine,
    "Glow": _glow,
    "Bump/Shine/Glow": lambda builder: _bump_shine_glow(builder, False),
    "Bump/Shine/Glow_2UV": lambda builder: _bump_shine_glow(builder, True),
    "Bump/Shine/Glow/Environment": _bump_shine_glow_environment,
    "Environment": _environment,
    "CBST2_2UV": _cbst2_2uv,
    "MPLBump": lambda builder: _mpl_bump(builder, False),
    "MPLBump2UV": lambda builder: _mpl_bump(builder, True),
    "MPLBlend": lambda builder: _mpl_blend(builder, True),
    "MPLBlendNoBump": lambda builder: _mpl_blend(builder, False),
    "MPLFull": lambda builder: _mpl_full(builder, False),
    "MPLFull2UV": lambda builder: _mpl_full(builder, True),
    "MPLReflection": _mpl_reflection,

    # These remain explicit so an unreviewed shader never silently receives a
    # plausible-looking but incorrect material.
    "Detail Palette": _detail_palette,
    "MPLReflection2UV": _unsupported,
    "MPLGlow": _unsupported,
    "MPLGlow2UV": _unsupported,
    "MPLShine": _unsupported,
    "MPLShine2UV": _unsupported,
    "Terrain": _unsupported,
    "Water": _unsupported,
    "Waterfall": _unsupported,
    "Lava": _unsupported,
    "Lava2": _unsupported,
}


# ======================================================================
# Public apply entry point and render modes
# ======================================================================


def normalize_alpha_mode(alpha_mode: Optional[str]) -> str:
    if not alpha_mode:
        return "OPAQUE"
    normalized = str(alpha_mode).replace("_", "").replace(" ", "").upper()
    aliases = {
        "NONE": "OPAQUE",
        "OPAQUE": "OPAQUE",
        "ALPHA": "ALPHA",
        "BLEND": "ALPHA",
        "CHROMA": "CHROMA",
        "CHROMAKEY": "CHROMA",
        "ALPHATEST": "CHROMA",
        "CLIP": "CHROMA",
        "ADD": "ADDALPHA",
        "ADDITIVE": "ADDALPHA",
        "ADDALPHA": "ADDALPHA",
    }
    return aliases.get(normalized, normalized)


def set_transparent_render_method(material: Material, *, chroma: bool) -> None:
    """Blender 5 plus a compatibility fallback for earlier Blender releases."""

    if hasattr(material, "surface_render_method"):
        try:
            material.surface_render_method = "DITHERED"
        except (TypeError, ValueError):
            pass
    if hasattr(material, "blend_method"):
        try:
            material.blend_method = "CLIP" if chroma else "BLEND"
        except (TypeError, ValueError):
            pass
    if chroma and hasattr(material, "alpha_threshold"):
        material.alpha_threshold = 0.5


def eqg_apply(material: Material) -> str:
    """Build a Blender 5 material from its parsed shader and shader group."""

    if material is None:
        return "Material is None"
    if material.get("quaildef") != "eqgmaterialdef":
        return f"{material.get('quaildef')} is not a valid eqgmaterialdef"

    try:
        shader = material.quail_eqgmaterialdef.shader
        family = SHADER_FAMILIES.get(shader)
        if family is None:
            return f"Unknown EQG shader: {shader}"

        group_name = family.group
        if group_name not in SHADER_GROUPS:
            return f"Shader {shader} references unknown shader group: {group_name}"

        build_group = GROUP_BUILDERS.get(group_name)
        if build_group is None:
            return f"No material node builder registered for group: {group_name}"
        if build_group is _unsupported:
            return f"Shader group {group_name!r} has not been verified yet"

        material.use_nodes = True
        if material.node_tree is None:
            return "Material node tree was not created"
        material.node_tree.nodes.clear()

        builder = MaterialNodeBuilder(material, shader)
        result = build_group(builder)
        builder.finish(
            result,
            material.quail_eqgmaterialdef.alpha_mode,
            CHROMA_CUTOFF,
        )
        return ""
    except NotImplementedError as error:
        return str(error)
    except (AttributeError, KeyError, OSError, RuntimeError, TypeError, ValueError) as error:
        return f"Could not build EQG material nodes: {error}"