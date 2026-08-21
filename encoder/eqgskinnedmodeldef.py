# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportAttributeAccessIssue=false

import bpy

from ..wce.eqgskinnedmodeldef import eqgskinnedmodeldef
from .eqganidef import encode_eqganidef
from .eqgmodeldef import (
	_armature_model_tag,
	_face_flag,
	_find_armature,
	_find_pos_action,
	_material_tag,
	_point_normal,
	_point_tint,
	_property_value,
	_source_material,
	_uv_layers,
	_vertex_weights,
)


def _encode_material(model_tag: str, material):
	source = _source_material(material)

	if source is None:
		return None, "Material is None"

	if source.get("quaildef") != "eqgmaterialdef":
		return None, f"Material {source.name} is not an eqgmaterialdef"

	properties = source.quail_eqgmaterialdef
	result = eqgskinnedmodeldef.materialtag()
	result.materialtag = _material_tag(model_tag, source)
	result.shadertag = properties.shadertag
	# result.animsleep = properties.animsleep
	result.properties = []
	# result.animtextures = []

	for row in properties.property_rows:
		property_name = row.property_name

		if not property_name:
			continue

		value, err = _property_value(properties, property_name)

		if err:
			return None, err

		encoded = eqgskinnedmodeldef.materialtag.property()
		encoded.property = value
		result.properties.append(encoded)

	return result, ""


def _encode_pos_animation(parser, armature_obj):
	action = _find_pos_action(armature_obj)

	if action is None:
		return None, (
			f"Missing POS_{_armature_model_tag(armature_obj)} "
			f"for armature {armature_obj.name}"
		)

	err = encode_eqganidef(parser, action, armature_obj)

	if err:
		return None, err

	animation = parser.eqganidefs.get(action.name)

	if animation is None:
		return None, f"EQGANIDEF {action.name} was not stored by the encoder"

	return animation, ""


def _encode_bones(armature_obj, pose_animation):
	pose_frames = {}

	for animation_bone in pose_animation.bones:
		if animation_bone.frames:
			pose_frames[animation_bone.bone] = animation_bone.frames[0]

	source_bones = list(armature_obj.data.bones)
	bone_indices = {bone.name: index for index, bone in enumerate(source_bones)}
	children = {bone.name: list(bone.children) for bone in source_bones}
	next_indices = {bone.name: -1 for bone in source_bones}

	for siblings in children.values():
		for index, bone in enumerate(siblings[:-1]):
			next_indices[bone.name] = bone_indices[siblings[index + 1].name]

	root_bones = [bone for bone in source_bones if bone.parent is None]

	for index, bone in enumerate(root_bones[:-1]):
		next_indices[bone.name] = bone_indices[root_bones[index + 1].name]

	result = []

	for bone in source_bones:
		pose_frame = pose_frames.get(bone.name)

		if pose_frame is None:
			return [], {}, (
				f"EQGANIDEF {pose_animation.tag} has no frame for bone {bone.name}"
			)

		encoded = eqgskinnedmodeldef.bone()
		encoded.bone = bone.name
		encoded.next = next_indices[bone.name]
		encoded.children = len(children[bone.name])
		encoded.childindex = (
			bone_indices[children[bone.name][0].name]
			if children[bone.name]
			else -1
		)
		encoded.pivot = tuple(float(value) for value in pose_frame.translation)
		encoded.quaternion = tuple(float(value) for value in pose_frame.rotation)
		encoded.scale = tuple(float(value) for value in pose_frame.scale)
		result.append(encoded)

	return result, bone_indices, ""


def _version(armature_obj, pose_animation):
	properties = getattr(armature_obj, "quail_eqgskinnedmodeldef", None)

	if properties is not None and hasattr(properties, "version"):
		return int(properties.version)

	return int(pose_animation.version)


def _mainpiece(obj):
	properties = getattr(obj, "quail_eqgskinnedmodeldef", None)

	if properties is not None and hasattr(properties, "mainpiece"):
		return int(properties.mainpiece)

	return 0


def _encode_model_piece(obj, model_tag: str, bone_indices):
	mesh = obj.data
	result = eqgskinnedmodeldef.model()
	result.model = obj.name
	result.mainpiece = _mainpiece(obj)
	result.vertices = []
	result.faces = []
	uv_layer, uv2_layer = _uv_layers(mesh)
	vertex_lookup = {}
	used_source_vertices = set()

	def add_vertex(source_index: int, uv, uv2):
		normal = _point_normal(mesh, source_index)
		tint = _point_tint(mesh, source_index)
		key = (source_index, tuple(uv), tuple(uv2), tuple(normal), tint)

		if key in vertex_lookup:
			return vertex_lookup[key], ""

		weights, err = _vertex_weights(obj, source_index, bone_indices)

		if err:
			return -1, err

		source = mesh.vertices[source_index]
		encoded = eqgskinnedmodeldef.model.vertex()
		encoded.xyz = (float(source.co.x), float(source.co.y), float(source.co.z))
		encoded.uv = (float(uv[0]), float(uv[1]))
		encoded.uv2 = (float(uv2[0]), float(uv2[1]))
		encoded.normal = (float(normal.x), float(normal.y), float(normal.z))
		encoded.tint = tint
		encoded.weights = []

		for bone_index, value in weights:
			weight = eqgskinnedmodeldef.model.vertex.weight()
			weight.weight = (bone_index, value)
			encoded.weights.append(weight)

		index = len(result.vertices)
		result.vertices.append(encoded)
		vertex_lookup[key] = index
		used_source_vertices.add(source_index)
		return index, ""

	for polygon_index, polygon in enumerate(mesh.polygons):
		if len(polygon.vertices) != 3:
			return None, (
				f"EQGSKINNEDMODELDEF {model_tag} model {obj.name} "
				f"face {polygon_index} is not a triangle"
			)

		triangle = []

		for loop_index, source_index in zip(polygon.loop_indices, polygon.vertices):
			uv = uv_layer.data[loop_index].uv if uv_layer else (0.0, 0.0)
			uv2 = uv2_layer.data[loop_index].uv if uv2_layer else (0.0, 0.0)
			vertex_index, err = add_vertex(source_index, uv, uv2)

			if err:
				return None, err

			triangle.append(vertex_index)

		if polygon.material_index < 0 or polygon.material_index >= len(mesh.materials):
			return None, (
				f"EQGSKINNEDMODELDEF {model_tag} model {obj.name} face "
				f"{polygon_index} has invalid material index {polygon.material_index}"
			)

		material = _source_material(mesh.materials[polygon.material_index])
		face = eqgskinnedmodeldef.model.face()
		face.triangle = tuple(triangle)
		face.material = _material_tag(model_tag, material)
		face.passable = _face_flag(mesh, polygon_index, "passable")
		face.transparent = _face_flag(mesh, polygon_index, "transparent")
		face.collisionrequired = _face_flag(mesh, polygon_index, "collisionrequired")
		face.culled = _face_flag(mesh, polygon_index, "culled")
		face.degenerate = _face_flag(mesh, polygon_index, "degenerate")
		result.faces.append(face)

	for source in mesh.vertices:
		if source.index in used_source_vertices:
			continue

		_, err = add_vertex(source.index, (0.0, 0.0), (0.0, 0.0))

		if err:
			return None, err

	return result, ""


def encode_eqgskinnedmodeldef(parser, obj) -> str:
	if obj.get("quaildef") != "eqgskinnedmodeldef":
		return ""

	if obj.type != 'MESH':
		return f"EQGSKINNEDMODELDEF {obj.name} is not a mesh"

	armature_obj = _find_armature(obj)

	if armature_obj is None:
		return f"EQGSKINNEDMODELDEF {obj.name} requires armature"

	model_tag = _armature_model_tag(armature_obj)
	pose_animation, err = _encode_pos_animation(parser, armature_obj)

	if err:
		return f"encode {model_tag} bones: {err}"

	result = parser.eqgskinnedmodeldefs.get(model_tag)

	if result is None:
		result = eqgskinnedmodeldef()
		result.tag = model_tag
		result.version = _version(armature_obj, pose_animation)
		result.materials = []
		result.bones, bone_indices, err = _encode_bones(
			armature_obj,
			pose_animation,
		)

		if err:
			return f"encode {model_tag} bones: {err}"

		result.models = []
		parser.eqgskinnedmodeldefs[result.tag] = result

	else:
		bone_indices = {
			bone.bone: index
			for index, bone in enumerate(result.bones)
		}

	material_tags = {material.materialtag for material in result.materials}

	for material in obj.data.materials:
		encoded, err = _encode_material(model_tag, material)

		if err:
			return f"encode {model_tag} material: {err}"

		if encoded.materialtag not in material_tags:
			result.materials.append(encoded)
			material_tags.add(encoded.materialtag)

	if any(model.model == obj.name for model in result.models):
		return f"EQGSKINNEDMODELDEF {model_tag} has duplicate model {obj.name}"

	model, err = _encode_model_piece(obj, model_tag, bone_indices)

	if err:
		return err

	result.models.append(model)
	return ""
