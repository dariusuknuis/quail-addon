# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportAttributeAccessIssue=false

import os
import bpy
import mathutils

from ..wce.eqgmodeldef import eqgmodeldef
from ..common.eqgmesh import eqg_piece_root
from ..ui.panel.eqgface import get_face_property
from .eqganidef import encode_eqganidef


def _source_material(material):
	if material is None:
		return None
	if not material.get("quail_layer_preview", False):
		return material
	source_name = material.get("quail_layer_source", "")
	return bpy.data.materials.get(source_name) or material


def _material_tag(model_tag: str, material):
	name = material.name
	prefix = f"{model_tag}_"
	if name.casefold().startswith(prefix.casefold()):
		return name[len(prefix):]
	return name


def _image_filename(image):
	if image is None:
		return ""

	source_name = image.get("quail_source_name", "")
	if source_name:
		return os.path.basename(str(source_name))

	if image.filepath:
		return os.path.basename(bpy.path.abspath(image.filepath))

	return image.name


def _property_value(properties, property_name: str):
	rna_property = properties.bl_rna.properties.get(property_name)
	if rna_property is None or not hasattr(properties, property_name):
		return None, f"Unsupported EQG material property: {property_name}"

	value = getattr(properties, property_name)

	if rna_property.type == 'POINTER' and rna_property.fixed_type.identifier == "Image":
		return (property_name, 2, _image_filename(value)), ""

	if rna_property.type == 'FLOAT':
		return (property_name, 0, format(float(value), ".8f")), ""

	if rna_property.type in {'INT', 'BOOLEAN'}:
		return (property_name, 1, str(int(value))), ""

	if rna_property.type == 'FLOAT_VECTOR':
		channels = [max(0, min(255, int(round(float(channel) * 255.0)))) for channel in value]
		return (property_name, 3, " ".join(str(channel) for channel in channels)), ""

	if rna_property.type in {'STRING', 'ENUM'}:
		return (property_name, 1, str(value)), ""

	return None, f"Unsupported EQG property type for {property_name}: {rna_property.type}"


def _encode_material(model_tag: str, material):
	source = _source_material(material)
	if source is None:
		return None, "Material is None"
	if source.get("quaildef") != "eqgmaterialdef":
		return None, f"Material {source.name} is not an eqgmaterialdef"

	properties = source.quail_eqgmaterialdef
	result = eqgmodeldef.materialtag()
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

		encoded = eqgmodeldef.materialtag.property()
		encoded.property = value
		result.properties.append(encoded)

	return result, ""


def _face_flag(mesh, polygon_index: int, name: str):
	try:
		return int(bool(get_face_property(mesh, polygon_index, name)))
	except (AttributeError, IndexError, KeyError, RuntimeError, TypeError, ValueError):
		return 0


def _point_normal(mesh, vertex_index: int):
	attribute = mesh.attributes.get("vertex_normals")
	if attribute and attribute.domain == 'POINT':
		return mathutils.Vector(attribute.data[vertex_index].vector)
	return mesh.vertices[vertex_index].normal.copy()


def _point_tint(mesh, vertex_index: int):
	attribute = mesh.color_attributes.get("vertex_colors")
	if attribute and attribute.domain == 'POINT':
		color = attribute.data[vertex_index].color
		return tuple(max(0, min(255, int(round(float(channel) * 255.0)))) for channel in color[:4])
	return (255, 255, 255, 255)


def _vertex_weights(obj, vertex_index: int, bone_indices):
	weights = []
	vertex = obj.data.vertices[vertex_index]

	for assignment in vertex.groups:
		if assignment.group < 0 or assignment.group >= len(obj.vertex_groups):
			continue
		group_name = obj.vertex_groups[assignment.group].name
		bone_index = bone_indices.get(group_name)
		if bone_index is None or assignment.weight <= 0.0:
			continue
		weights.append((bone_index, float(assignment.weight)))

	weights.sort(key=lambda item: (-item[1], item[0]))
	if len(weights) > 4:
		return None, f"Vertex {vertex_index} has {len(weights)} EQG bone weights; maximum is 4"

	return weights, ""


def _find_armature(obj):
	for modifier in obj.modifiers:
		if modifier.type == 'ARMATURE' and modifier.object:
			return modifier.object
	if obj.parent and obj.parent.type == 'ARMATURE':
		return obj.parent
	return None


def _armature_model_tag(armature_obj):
	name = armature_obj.name

	if name.casefold().endswith("_armature"):
		return name[:-9]

	return name


def _find_pos_action(armature_obj):
	action_tag = f"POS_{_armature_model_tag(armature_obj)}"
	action = bpy.data.actions.get(action_tag)

	if action is not None:
		return action

	tag_lower = action_tag.casefold()

	for candidate in bpy.data.actions:
		if candidate.name.casefold() == tag_lower:
			return candidate

	return None


def _encode_pos_animation(parser, armature_obj):
	if armature_obj is None:
		return None, ""

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


def _encode_bones(armature_obj, pose_animation, obj):
	if armature_obj is None:
		return [], {}, ""

	if pose_animation is None:
		return [], {}, f"EQG armature {armature_obj.name} has no POS animation"

	pose_frames = {}

	for animation_bone in pose_animation.bones:
		if animation_bone.frames:
			pose_frames[animation_bone.bone] = animation_bone.frames[0]

	armature_bones = list(armature_obj.data.bones)

	if not armature_bones:
		return [], {}, f"EQG armature {armature_obj.name} has no bones"

	race_tag = str(_armature_model_tag(armature_obj)).strip().casefold()
	model_tag = str(obj.name or "").strip().casefold()

	if model_tag == race_tag:
		attachment_root = "ROOT_BONE"
	else:
		attachment_root = eqg_piece_root(model_tag, race_tag)

	if attachment_root is not None:
		source_root = armature_obj.data.bones.get(attachment_root)

		if source_root is None:
			return [], {}, (
				f"EQGMODELDEF {obj.name} expects attachment bone "
				f"{attachment_root}, but it is not present in "
				f"{armature_obj.name}"
			)

		selected_bones = []

		for bone in armature_bones:
			current = bone

			while current is not None:
				if current == source_root:
					selected_bones.append(bone)
					break

				current = current.parent

	else:
		# Unrecognized models keep independent armatures, so encode
		# their complete skeleton.
		selected_bones = armature_bones
		root_bones = [bone for bone in selected_bones if bone.parent is None]

		if len(root_bones) != 1:
			root_names = ", ".join(bone.name for bone in root_bones)

			return [], {}, (
				f"EQGMODELDEF {obj.name} has {len(root_bones)} "
				f"armature roots: {root_names or 'none'}"
			)

		source_root = root_bones[0]

	selected_names = {bone.name for bone in selected_bones}
	bone_indices = {
		bone.name: index
		for index, bone in enumerate(selected_bones)
	}
	children = {bone.name: [] for bone in selected_bones}

	for bone in selected_bones:
		if bone.parent is not None and bone.parent.name in selected_names:
			children[bone.parent.name].append(bone)

	next_indices = {bone.name: -1 for bone in selected_bones}

	for siblings in children.values():
		for index, bone in enumerate(siblings[:-1]):
			next_indices[bone.name] = bone_indices[siblings[index + 1].name]

	def pose_matrix(bone_name):
		frame = pose_frames.get(bone_name)

		if frame is None:
			raise ValueError(
				f"EQGANIDEF {pose_animation.tag} has no frame "
				f"for bone {bone_name}"
			)

		translation = mathutils.Vector(frame.translation)
		scale = mathutils.Vector(frame.scale)
		source_rotation = frame.rotation

		rotation = mathutils.Quaternion((
			-source_rotation[3],
			source_rotation[0],
			source_rotation[1],
			source_rotation[2],
		))

		return mathutils.Matrix.LocRotScale(
			translation,
			rotation,
			scale,
		)

	accumulated_matrices = {}

	def accumulated_pose_matrix(bone):
		cached = accumulated_matrices.get(bone.name)

		if cached is not None:
			return cached

		local_matrix = pose_matrix(bone.name)

		if bone.parent is None:
			world_matrix = local_matrix
		else:
			world_matrix = (
				accumulated_pose_matrix(bone.parent)
				@ local_matrix
			)

		accumulated_matrices[bone.name] = world_matrix
		return world_matrix

	try:
		root_matrix = accumulated_pose_matrix(source_root)
	except ValueError as exception:
		return [], {}, str(exception)

	root_translation, root_rotation, root_scale = root_matrix.decompose()

	# Convert Blender's (w, x, y, z) quaternion back to the WCE
	# (x, y, z, w) convention used by the existing encoder/decoder.
	root_quaternion = (
		float(root_rotation.x),
		float(root_rotation.y),
		float(root_rotation.z),
		float(-root_rotation.w),
	)

	result = []

	for bone in selected_bones:
		pose_frame = pose_frames.get(bone.name)

		if pose_frame is None:
			return [], {}, (
				f"EQGANIDEF {pose_animation.tag} has no frame "
				f"for bone {bone.name}"
			)

		bone_children = children[bone.name]
		encoded = eqgmodeldef.bone()
		encoded.bone = "ROOT_BONE" if bone == source_root else bone.name
		encoded.next = next_indices[bone.name]
		encoded.children = len(bone_children)
		encoded.childindex = (
			bone_indices[bone_children[0].name]
			if bone_children
			else -1
		)

		if bone == source_root:
			encoded.pivot = tuple(float(value) for value in root_translation)
			encoded.quaternion = root_quaternion
			encoded.scale = tuple(float(value) for value in root_scale)
		else:
			encoded.pivot = tuple(float(value) for value in pose_frame.translation)
			encoded.quaternion = tuple(float(value) for value in pose_frame.rotation)
			encoded.scale = tuple(float(value) for value in pose_frame.scale)

		result.append(encoded)

	return result, bone_indices, ""


def _uv_layers(mesh):
	uv = mesh.uv_layers.get("UVMap")
	uv2 = mesh.uv_layers.get("UVMap2")

	if uv is None and len(mesh.uv_layers) > 0:
		uv = mesh.uv_layers[0]
	if uv2 is None and len(mesh.uv_layers) > 1:
		uv2 = mesh.uv_layers[1]

	return uv, uv2


def encode_eqgmodeldef(parser, obj) -> str:
	if obj.get("quaildef") != "eqgmodeldef":
		return ""
	if obj.type != 'MESH':
		return f"EQGMODELDEF {obj.name} is not a mesh"

	mesh = obj.data
	model_tag = obj.name
	result = eqgmodeldef()
	result.tag = model_tag
	result.version = int(obj.quail_eqgmodeldef.version)
	result.materials = []
	result.vertices = []
	result.faces = []

	for material in mesh.materials:
		encoded, err = _encode_material(model_tag, material)
		if err:
			return f"encode material: {err}"
		result.materials.append(encoded)

	armature_obj = _find_armature(obj)
	pose_animation, err = _encode_pos_animation(parser, armature_obj)

	if err:
		return f"encode {model_tag} bones: {err}"

	result.bones, bone_indices, err = _encode_bones(
		armature_obj,
		pose_animation,
		obj,
	)

	if err:
		return f"encode {model_tag} bones: {err}"
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
		encoded = eqgmodeldef.vertex()
		encoded.xyz = (float(source.co.x), float(source.co.y), float(source.co.z))
		encoded.uv = (float(uv[0]), float(uv[1]))
		encoded.uv2 = (float(uv2[0]), float(uv2[1]))
		encoded.normal = (float(normal.x), float(normal.y), float(normal.z))
		encoded.tint = tint
		encoded.weights = []

		for bone_index, value in weights:
			weight = eqgmodeldef.vertex.weight()
			weight.weight = (bone_index, value)
			encoded.weights.append(weight)

		index = len(result.vertices)
		result.vertices.append(encoded)
		vertex_lookup[key] = index
		used_source_vertices.add(source_index)
		return index, ""

	for polygon_index, polygon in enumerate(mesh.polygons):
		if len(polygon.vertices) != 3:
			return f"EQGMODELDEF {model_tag} face {polygon_index} is not a triangle"

		triangle = []
		for loop_index, source_index in zip(polygon.loop_indices, polygon.vertices):
			uv = uv_layer.data[loop_index].uv if uv_layer else (0.0, 0.0)
			uv2 = uv2_layer.data[loop_index].uv if uv2_layer else (0.0, 0.0)
			vertex_index, err = add_vertex(source_index, uv, uv2)
			if err:
				return err
			triangle.append(vertex_index)

		if polygon.material_index < 0 or polygon.material_index >= len(mesh.materials):
			return f"EQGMODELDEF {model_tag} face {polygon_index} has invalid material index {polygon.material_index}"

		material = _source_material(mesh.materials[polygon.material_index])
		face = eqgmodeldef.face()
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
			return err

	parser.eqgmodeldefs[result.tag] = result
	return ""
