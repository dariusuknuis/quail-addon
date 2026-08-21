# pyright: basic, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import os

import bpy

from ..common import base_tag, state
from ..common.eqgshaders import SHADER_FAMILIES, eqg_apply, replace_shadertag_alpha_mode, replace_shadertag_shader
from ..common.rendermethod import create_rendermethod_nodegroup
from ..common.s3dmaterial import update_rendermethod_node, update_twosided
from ..decoder.simplespritedef import create_frame_nodegroup


class ConversionError(Exception):
	pass


class MaterialFormat(str, Enum):
	BLENDER = "blender"
	S3D = "materialdefinition"
	EQG = "eqgmaterialdef"


class SpriteLayout(str, Enum):
	NONE = "none"
	DEFAULT = "default"
	DETAIL = "detail"
	LAYER = "layer"
	PALETTE_TILED = "palette_tiled"


@dataclass
class TextureSource:
	property_name: str = ""
	image: Optional[bpy.types.Image] = None
	filename: str = ""
	scale: float = 1.0
	blend: float = 0.0
	palette_index: int = 0


@dataclass
class MaterialSource:
	source_format: MaterialFormat
	original_name: str
	alpha_mode: str = "Opaque"
	shader_family: str = ""
	transparent: bool = False
	textures: dict[str, TextureSource] = field(default_factory=dict)
	values: dict[str, object] = field(default_factory=dict)


@dataclass
class S3DMaterialPlan:
	userdefined_index: int = 2
	transparent: bool = False
	sprite_layout: SpriteLayout = SpriteLayout.DEFAULT
	base_texture: Optional[TextureSource] = None
	detail_texture: Optional[TextureSource] = None
	detail_scale: float = 1.0
	palette_texture: Optional[TextureSource] = None
	tiled_textures: list[TextureSource] = field(default_factory=list)


EQG_ALPHA_TO_S3D_USERDEFINED = {
	"Opaque": 2,
	"Chroma": 8,
	"Alpha": 6,
	"AddAlpha": 12,
}


EQG_FAMILY_TO_S3D_LAYOUT = {
	"C1": SpriteLayout.DEFAULT,
	"C1_2UV": SpriteLayout.DETAIL,
	"CB1": SpriteLayout.DEFAULT,
	"CB1_2UV": SpriteLayout.DETAIL,
	"CBS1": SpriteLayout.DEFAULT,
	"CBSG1": SpriteLayout.DEFAULT,
	"CBSG1_2UV": SpriteLayout.DETAIL,
	"CBGG1": SpriteLayout.DEFAULT,
	"CBSGE1": SpriteLayout.DEFAULT,
	"CBGGE1": SpriteLayout.DEFAULT,
	"CE1": SpriteLayout.DEFAULT,
	"CG1": SpriteLayout.DEFAULT,
	"CSG1": SpriteLayout.DEFAULT,
	"C1DTP": SpriteLayout.PALETTE_TILED,
	"CBST2_2UV": SpriteLayout.DETAIL,
	"MPLBasic": SpriteLayout.DEFAULT,
	"MPLBasicA": SpriteLayout.DEFAULT,
	"MPLBasicAT": SpriteLayout.DEFAULT,
	"MPLBump": SpriteLayout.DETAIL,
	"MPLBumpA": SpriteLayout.DETAIL,
	"MPLBumpAT": SpriteLayout.DETAIL,
	"MPLBump2UV": SpriteLayout.DETAIL,
	"MPLBlend": SpriteLayout.DETAIL,
	"MPLBlendNoBump": SpriteLayout.DETAIL,
	"MPLFull": SpriteLayout.DETAIL,
	"MPLFull2UV": SpriteLayout.DETAIL,
	"MPLRB": SpriteLayout.DETAIL,
	"MPLRB2UV": SpriteLayout.DETAIL,
	"MPLGB": SpriteLayout.DETAIL,
	"MPLGB2UV": SpriteLayout.DETAIL,
	"MPLSB": SpriteLayout.DETAIL,
	"MPLSB2UV": SpriteLayout.DETAIL,
	"Terrain": SpriteLayout.DETAIL,
	"Water": SpriteLayout.DEFAULT,
	"WaterFall": SpriteLayout.DEFAULT,
	"Lava": SpriteLayout.DEFAULT,
	"Lava2": SpriteLayout.DEFAULT,
}

S3D_LAYOUT_TO_EQG_FAMILY = {
	SpriteLayout.DEFAULT: "C1",
	SpriteLayout.DETAIL: "C1_2UV",
	SpriteLayout.LAYER: "C1_2UV",
	SpriteLayout.PALETTE_TILED: "C1DTP",
}


# These are deliberately explicit. They select the EQG texture used as the
# second file of an S3D DETAIL SimpleSprite. Update individual entries here if
# a different source property is preferred for a particular shader family.
EQG_DETAIL_TEXTURE_PROPERTIES = {
	"C1_2UV": ("e_TextureSecond0",),
	"CB1_2UV": ("e_TextureSecond0",),
	"CBSG1_2UV": ("e_TextureSecond0",),
	"CBST2_2UV": ("e_TextureDiffuse1", "e_TextureSecond0"),
	"MPLBump": ("e_TextureCoverage0",),
	"MPLBumpA": ("e_TextureCoverage0",),
	"MPLBumpAT": ("e_TextureCoverage0",),
	"MPLBump2UV": ("e_TextureCoverage0",),
	"MPLBlend": ("e_TextureDiffuse1", "e_TextureCoverage0"),
	"MPLBlendNoBump": ("e_TextureCoverage0",),
	"MPLFull": ("e_TextureCoverage0",),
	"MPLFull2UV": ("e_TextureCoverage0",),
	"MPLRB": ("e_TextureCoverage0",),
	"MPLRB2UV": ("e_TextureCoverage0",),
	"MPLGB": ("e_TextureCoverage0",),
	"MPLGB2UV": ("e_TextureCoverage0",),
	"MPLSB": ("e_TextureCoverage0",),
	"MPLSB2UV": ("e_TextureCoverage0",),
	"Terrain": ("e_TextureDetail1", "e_TextureDetail2"),
}


EQG_BASE_TEXTURE_PROPERTIES = {
	"Terrain": ("e_TextureFallback", "e_TextureDiffuse0"),
}


def material_format(material: bpy.types.Material) -> MaterialFormat:
	qdef = material.get("quaildef")

	if qdef == "materialdefinition":
		return MaterialFormat.S3D

	if qdef == "eqgmaterialdef":
		return MaterialFormat.EQG

	return MaterialFormat.BLENDER


def image_filename(image: Optional[bpy.types.Image]) -> str:
	if image is None:
		return ""

	source_name = image.get("quail_source_name", "")

	if source_name:
		return os.path.basename(str(source_name)).lower()

	if image.filepath:
		filename = os.path.basename(bpy.path.abspath(image.filepath))

		if filename:
			return filename.lower()

	return os.path.basename(image.name).lower()


def first_image_texture(material: bpy.types.Material):
	if not material.use_nodes or not material.node_tree:
		return None

	for node in material.node_tree.nodes:
		if node.type == 'TEX_IMAGE' and node.image:
			return node.image

	return None


def _texture_source(property_name: str, image):
	if not isinstance(image, bpy.types.Image):
		return None

	return TextureSource(
		property_name=property_name,
		image=image,
		filename=image_filename(image),
	)


def _eqg_property_value(material: bpy.types.Material, property_name: str):
	props = material.quail_eqgmaterialdef

	if hasattr(props, property_name):
		return getattr(props, property_name)

	return None


def is_failsafe_material(material: bpy.types.Material) -> bool:
	"""Return whether this is the untagged EQG FailsafeShader placeholder."""

	return material.name.strip().casefold() == "failsafeshader"


def inspect_blender_material(material: bpy.types.Material) -> MaterialSource:
	source = MaterialSource(
		source_format=MaterialFormat.BLENDER,
		original_name=material.name,
	)

	image = first_image_texture(material)

	if image:
		source.textures["base"] = TextureSource(
			property_name="base",
			image=image,
			filename=image_filename(image),
		)

	return source


def inspect_eqg_material(material: bpy.types.Material) -> MaterialSource:
	props = material.quail_eqgmaterialdef

	alpha_mode = props.alpha_mode
	shader_family = props.shader

	if shader_family not in SHADER_FAMILIES:
		raise ConversionError(
			f"Unsupported EQG shader family: {shader_family}"
		)

	source = MaterialSource(
		source_format=MaterialFormat.EQG,
		original_name=material.name,
		alpha_mode=alpha_mode,
		shader_family=shader_family,
	)
	for row in getattr(props, "property_rows", []):
		property_name = getattr(row, "property_name", "")

		if not property_name:
			continue

		value = _eqg_property_value(material, property_name)
		source.values[property_name] = value
		texture = _texture_source(property_name, value)

		if texture:
			source.textures[property_name] = texture

	return source


def inspect_material(material: bpy.types.Material) -> MaterialSource:
	# FailsafeShader is an untagged placeholder inserted into an EQG mesh when
	# a face has the special -1/FailsafeShader material reference. Treat it as
	# transparent before classifying ordinary unformatted Blender materials.
	if is_failsafe_material(material):
		return MaterialSource(
			source_format=MaterialFormat.BLENDER,
			original_name=material.name,
			transparent=True,
		)

	source_format = material_format(material)

	if source_format == MaterialFormat.BLENDER:
		return inspect_blender_material(material)

	if source_format == MaterialFormat.EQG:
		return inspect_eqg_material(material)

	raise ConversionError(
		f"{material.name} is already a MATERIALDEFINITION"
	)


def _first_texture(source: MaterialSource, property_names):
	for property_name in property_names:
		texture = source.textures.get(property_name)

		if texture:
			return texture

	return None


def _float_value(source: MaterialSource, property_names, default=1.0):
	for property_name in property_names:
		value = source.values.get(property_name)

		if isinstance(value, (int, float)):
			return float(value)

	return float(default)


def make_s3d_plan(source: MaterialSource) -> S3DMaterialPlan:
	if source.transparent:
		return S3DMaterialPlan(
			transparent=True,
			sprite_layout=SpriteLayout.NONE,
		)

	if source.source_format == MaterialFormat.BLENDER:
		return S3DMaterialPlan(
			userdefined_index=2,
			sprite_layout=SpriteLayout.DEFAULT,
			base_texture=source.textures.get("base"),
		)

	if source.source_format != MaterialFormat.EQG:
		raise ConversionError("Unsupported source material format")

	userdefined_index = EQG_ALPHA_TO_S3D_USERDEFINED.get(
		source.alpha_mode
	)

	if userdefined_index is None:
		raise ConversionError(
			f"Unsupported EQG alpha mode: {source.alpha_mode}"
		)

	layout = EQG_FAMILY_TO_S3D_LAYOUT.get(source.shader_family)

	if layout is None:
		raise ConversionError(
			f"Unsupported EQG shader family: {source.shader_family}"
		)

	base_properties = EQG_BASE_TEXTURE_PROPERTIES.get(
		source.shader_family,
		("e_TextureDiffuse0",),
	)
	plan = S3DMaterialPlan(
		userdefined_index=userdefined_index,
		sprite_layout=layout,
		base_texture=_first_texture(source, base_properties),
	)

	if layout == SpriteLayout.DETAIL:
		plan.detail_texture = _first_texture(
			source,
			EQG_DETAIL_TEXTURE_PROPERTIES.get(
				source.shader_family,
				("e_TextureSecond0", "e_TextureCoverage0"),
			),
		)
		plan.detail_scale = _float_value(
			source,
			("e_fCoverageScale0", "e_fCoverageScale"),
			1.0,
		)

	elif layout == SpriteLayout.PALETTE_TILED:
		plan.palette_texture = source.textures.get("e_TexturePalette0")

		for index in range(10):
			texture = source.textures.get(f"e_TextureDetail{index}")

			if not texture:
				continue

			texture.scale = _float_value(
				source,
				(f"e_fScale{index}",),
				1.0,
			)
			texture.blend = _float_value(
				source,
				(f"e_fGrassDensity{index}",),
				0.0,
			)
			texture.palette_index = index + 1
			plan.tiled_textures.append(texture)

	return plan


def _simplesprite_tag(texture: TextureSource) -> str:
	filename = texture.filename

	if not filename and texture.image:
		filename = image_filename(texture.image)

	stem = os.path.splitext(os.path.basename(filename))[0]
	return stem.upper()


def _add_frame_file(
	frame,
	texture: TextureSource,
	texture_mode: str,
	file_index: int,
):
	file = frame.files.add()
	file.file_index = file_index
	file.file_name = texture.filename
	file.image_name = texture.image.name if texture.image else ""
	file.raw_string = texture.filename
	file.texture_mode = texture_mode
	file.palette_index = texture.palette_index
	file.scale = texture.scale
	file.blend = texture.blend
	return file


def create_s3d_simplesprite(
	plan: S3DMaterialPlan,
) -> tuple[str, str]:
	if plan.base_texture is None:
		return "", ""

	requested_tag = _simplesprite_tag(plan.base_texture)
	sprite = bpy.data.node_groups.new(requested_tag, 'ShaderNodeTree')
	sprite["quaildef"] = "simplespritedef"
	previous_updating = state.QUAIL_UPDATING
	state.QUAIL_UPDATING = True

	try:
		sprite.interface.new_socket(
			name="sRGB Texture",
			in_out='OUTPUT',
			socket_type="NodeSocketColor",
		)
		sprite.interface.new_socket(
			name="Alpha",
			in_out='OUTPUT',
			socket_type="NodeSocketFloat",
		)
		nodes = sprite.nodes
		links = sprite.links
		group_output = nodes.new("NodeGroupOutput")
		group_output.location = (600, 0)
		props = sprite.quail_simplesprite
		props.skipframes = False
		props.has_sleep = False
		props.sleep = 0
		props.has_current_frame = False
		props.current_frame = 0
		props.frames.clear()
		frame = props.frames.add()
		frame.frame_id = 0
		frame.frame_name = f"{sprite.name}_FRAME_0"
		frame.files.clear()
		_add_frame_file(frame, plan.base_texture, 'BASE', 0)

		if (
			plan.sprite_layout == SpriteLayout.DETAIL
			and plan.detail_texture
			and plan.detail_texture.image
		):
			plan.detail_texture.scale = plan.detail_scale
			_add_frame_file(frame, plan.detail_texture, 'DETAIL', 1)

		elif (
			plan.sprite_layout == SpriteLayout.PALETTE_TILED
			and plan.palette_texture
			and plan.palette_texture.image
		):
			_add_frame_file(frame, plan.palette_texture, 'PALETTE', 1)

			for texture in plan.tiled_textures:
				_add_frame_file(
					frame,
					texture,
					'TILED',
					len(frame.files),
				)

		frame.numfiles = len(frame.files)
		frame_group = create_frame_nodegroup(
			None,
			frame,
			sprite.name,
			force_rebuild=False,
		)

		if not frame_group:
			raise ConversionError(
				f"Unable to create frame group for {sprite.name}"
			)

		frame.frame_node_name = frame_group.name
		frame_node = nodes.new("ShaderNodeGroup")
		frame_node.node_tree = frame_group
		frame_node.location = (0, 0)
		frame_node["frame_id"] = 0

		for socket in frame_node.inputs:
			socket.hide = True

		links.new(
			frame_node.outputs["Color"],
			group_output.inputs["sRGB Texture"],
		)
		links.new(
			frame_node.outputs["Alpha"],
			group_output.inputs["Alpha"],
		)
		props.numframes = 1
		props.active_frame = 0

	except Exception as exception:
		bpy.data.node_groups.remove(sprite)
		return "", str(exception)

	finally:
		state.QUAIL_UPDATING = previous_updating

	return sprite.name, ""


def _build_materialdefinition_nodes(material: bpy.types.Material):
	material.use_nodes = True

	if not material.node_tree:
		raise ConversionError("Unable to create material node tree")

	nodes = material.node_tree.nodes
	links = material.node_tree.links
	nodes.clear()
	group_tree = create_rendermethod_nodegroup()
	group_node = nodes.new("ShaderNodeGroup")
	group_node.node_tree = group_tree
	group_node.location = (0, 0)
	output = nodes.new("ShaderNodeOutputMaterial")
	output.location = (300, 0)
	links.new(group_node.outputs["Shader"], output.inputs["Surface"])

	hide_inputs = {
		"PassableDisplay",
		"Masked",
		"AlphaBlend",
		"Additive",
		"Opacity",
		"Drawstyle",
		"TextureIndex",
		"Transparent Blit",
		"Particle Tint",
	}

	for socket in group_node.inputs:
		if socket.name in hide_inputs:
			socket.hide = True


def apply_s3d_plan(
	material: bpy.types.Material,
	source: MaterialSource,
	plan: S3DMaterialPlan,
	context,
):
	sprite_tag, err = create_s3d_simplesprite(plan)

	if err:
		raise ConversionError(err)

	base_name = source.original_name.upper()

	if not base_name.endswith("_MDF"):
		base_name = f"{base_name}_MDF"

	material.name = base_name
	material["quaildef"] = "materialdefinition"
	props = material.quail_materialdefinition
	# Set the mode only after the new RENDERMETHOD node exists. Otherwise the
	# property's update callback would modify the source EQG node tree just
	# before that tree is replaced.
	props.transparent_override = False
	props.use_userdefined = False
	props.userdefined_index = plan.userdefined_index
	props.variation = False
	props.rgbpen = (1.0, 1.0, 1.0)
	props.brightness = 1
	props.scaledambient = 1
	props.simplespritehaveskipframes = False
	props.simplespriteskipframes = False
	props.has_uvshiftperms = True
	props.uvshiftperms = (0.0, 0.0)
	props.twosided = False
	_build_materialdefinition_nodes(material)

	if plan.transparent:
		props.transparent_override = True
	else:
		# Enabling this invokes update_userdefined after the RENDERMETHOD node exists.
		props.use_userdefined = True
		update_rendermethod_node(props, context)

	props.simplespritetag = sprite_tag if sprite_tag else "NONE"
	update_twosided(props, context)


def eqg_alpha_mode_from_s3d(material: bpy.types.Material) -> Optional[str]:
	"""Return the EQG alpha mode represented by the effective S3D flags."""

	if material_format(material) != MaterialFormat.S3D:
		raise ConversionError(
			f"{material.name} is not a MATERIALDEFINITION"
		)

	props = material.quail_materialdefinition

	if props.transparent_override:
		return None

	# Precedence is intentional: additive > alpha blend > chroma/masked.
	if props.additive:
		return "AddAlpha"

	if props.alphablend:
		return "Alpha"

	if props.masked:
		return "Chroma"

	return "Opaque"


def eqg_settings_from_s3d(
	material: bpy.types.Material,
	shader_family: str = "C1",
) -> tuple[Optional[str], Optional[str]]:
	"""Return (alpha_mode, shader) without consulting USERDEFINED."""

	alpha_mode = eqg_alpha_mode_from_s3d(material)

	if alpha_mode is None:
		return None, None

	if shader_family not in SHADER_FAMILIES:
		raise ConversionError(
			f"Unsupported EQG shader family: {shader_family}"
		)

	return alpha_mode, shader_family


def convert_to_materialdefinition(
	material: bpy.types.Material,
	context,
) -> str:
	if material is None:
		return "Material is None"

	if material_format(material) == MaterialFormat.S3D:
		return ""

	try:
		source = inspect_material(material)
		plan = make_s3d_plan(source)
		apply_s3d_plan(material, source, plan, context)
		return ""

	except ConversionError as exception:
		return str(exception)

	except Exception as exception:
		return f"Material conversion failed: {exception}"


def _simplesprite_file_image(file):
	if not file.image_name:
		return None

	return bpy.data.images.get(file.image_name)


def inspect_s3d_simplesprite(material: bpy.types.Material):
	"""Inspect only the first frame of the material's SimpleSprite."""

	props = material.quail_materialdefinition
	sprite_tag = props.simplespritetag

	result = {
		"layout": SpriteLayout.DEFAULT,
		"base": None,
		"second": None,
		"palette": None,
		"tiled": [],
	}

	if not sprite_tag or sprite_tag == "NONE":
		return result

	sprite = bpy.data.node_groups.get(sprite_tag)

	if sprite is None:
		raise ConversionError(
			f"SimpleSprite {sprite_tag} not found"
		)

	if sprite.get("quaildef") != "simplespritedef":
		raise ConversionError(
			f"{sprite_tag} is not a SIMPLESPRITEDEF"
		)

	sprite_props = sprite.quail_simplesprite

	if not sprite_props.frames:
		return result

	# EQG materials cannot represent S3D frame animation.
	# Only the first frame is converted.
	frame = sprite_props.frames[0]

	if not frame.files:
		return result

	result["base"] = _simplesprite_file_image(frame.files[0])

	if len(frame.files) < 2:
		return result

	second_file = frame.files[1]
	second_mode = second_file.texture_mode

	if second_mode == 'DETAIL':
		result["layout"] = SpriteLayout.DETAIL
		result["second"] = _simplesprite_file_image(second_file)

	elif second_mode == 'LAYER':
		result["layout"] = SpriteLayout.LAYER
		result["second"] = _simplesprite_file_image(second_file)

	elif second_mode == 'PALETTE':
		result["layout"] = SpriteLayout.PALETTE_TILED
		result["palette"] = _simplesprite_file_image(second_file)

		for file in frame.files[2:]:
			if file.texture_mode != 'TILED':
				continue

			image = _simplesprite_file_image(file)

			if image is None:
				continue

			result["tiled"].append((
				image,
				float(file.scale),
			))

	return result


def _add_eqg_property(props, property_name: str, value):
	"""Set an EQG property and add it to the exported property rows."""

	setattr(props, property_name, value)

	row = props.property_rows.add()
	row.property_name = property_name


def _apply_eqg_material(material: bpy.types.Material, alpha_mode: str, shader: str, properties) -> str:
	if shader not in SHADER_FAMILIES:
		return f"Unsupported EQG shader family: {shader}"

	shadertag = replace_shadertag_shader(
		"Opaque_MaxC1.fx",
		shader,
	)
	shadertag = replace_shadertag_alpha_mode(
		shadertag,
		alpha_mode,
	)

	previous_updating = state.QUAIL_UPDATING
	state.QUAIL_UPDATING = True

	try:
		material["quaildef"] = "eqgmaterialdef"
		props = material.quail_eqgmaterialdef
		props.shadertag = shadertag
		props.alpha_mode = alpha_mode
		props.shader = shader
		props.property_rows.clear()

		for property_name, value in properties:
			if value is None:
				continue

			_add_eqg_property(
				props,
				property_name,
				value,
			)

	finally:
		state.QUAIL_UPDATING = previous_updating

	return eqg_apply(material)


def _convert_to_failsafe_material(material: bpy.types.Material) -> str:
	existing = bpy.data.materials.get("FailsafeShader")

	if existing is not None and existing != material:
		return (
			"FailsafeShader already exists; replace the material slot "
			"with the existing FailsafeShader material"
		)

	if "quaildef" in material:
		del material["quaildef"]

	material.name = "FailsafeShader"
	return ""


def _prefix_eqg_material_name(
	material: bpy.types.Material,
	context,
) -> str:
	model_name = _eqg_model_name(context)

	if not model_name:
		return "Unable to determine the EQG model name"

	prefix = f"{model_name}_"

	if not material.name.casefold().startswith(prefix.casefold()):
		material.name = f"{prefix}{material.name}"

	return ""


def _eqg_model_name(context) -> str:
	obj = getattr(context, "object", None)

	if obj is None:
		return ""

	model_name = base_tag(obj.name)
	suffix = "_dmspritedef"

	if model_name.casefold().endswith(suffix):
		model_name = model_name[:-len(suffix)]

	return model_name


def convert_to_eqgmaterialdef(material: bpy.types.Material, context) -> str:
	if material is None:
		return "Material is None"

	source_format = material_format(material)

	if source_format == MaterialFormat.EQG:
		return ""

	if is_failsafe_material(material):
		return ""

	# ------------------------------------------------
	# Ordinary Blender material → default EQG material
	# ------------------------------------------------
	if source_format == MaterialFormat.BLENDER:
		image = first_image_texture(material)
		properties = []

		if image is not None:
			properties.append(("e_TextureDiffuse0", image))

		err = _prefix_eqg_material_name(material, context)

		if err:
			return err

		return _apply_eqg_material(material, "Opaque", "C1", properties)

	if material.name.casefold().endswith("_mdf"):
		material.name = material.name[:-4]

	err = _prefix_eqg_material_name(
		material,
		context,
	)

	if err:
		return err

	# ------------------------------------------------
	# S3D Transparent → FailsafeShader
	# ------------------------------------------------
	alpha_mode = eqg_alpha_mode_from_s3d(material)

	if alpha_mode is None:
		return _convert_to_failsafe_material(material)

	# ------------------------------------------------
	# Inspect the first SimpleSprite frame
	# ------------------------------------------------
	try:
		sprite = inspect_s3d_simplesprite(material)
	except ConversionError as exception:
		return str(exception)

	layout = sprite["layout"]
	shader = S3D_LAYOUT_TO_EQG_FAMILY.get(layout)

	if shader is None:
		return f"No EQG mapping for SimpleSprite layout {layout.value}"

	properties = []
	base_image = sprite["base"]

	if base_image is not None:
		properties.append((
			"e_TextureDiffuse0",
			base_image,
		))

	# DETAIL and LAYER both currently become C1_2UV.
	if layout in {SpriteLayout.DETAIL, SpriteLayout.LAYER}:
		second_image = sprite["second"]
		if second_image is not None:
			properties.append((
				"e_TextureSecond0",
				second_image,
			))

	elif layout == SpriteLayout.PALETTE_TILED:
		palette_image = sprite["palette"]

		if palette_image is not None:
			properties.append((
				"e_TexturePalette0",
				palette_image,
			))

		for index, (image, scale) in enumerate(
			sprite["tiled"][:10]
		):
			properties.append((
				f"e_TextureDetail{index}",
				image,
			))
			properties.append((
				f"e_fScale{index}",
				scale,
			))

			# file.blend is intentionally not converted because
			# EQG grass density is not equivalent to S3D blend.

	return _apply_eqg_material(material, alpha_mode, shader, properties)


def convert_material(
	material: bpy.types.Material,
	target_format: MaterialFormat | str,
	context,
) -> str:
	try:
		target = MaterialFormat(target_format)
	except ValueError:
		return f"Unsupported material target: {target_format}"

	if target == MaterialFormat.S3D:
		return convert_to_materialdefinition(material, context)

	if target == MaterialFormat.EQG:
		return convert_to_eqgmaterialdef(material, context)

	return f"Unsupported material target: {target.value}"
