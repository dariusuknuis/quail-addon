# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils

from ..wce.eqganidef import eqganidef


def _action_fcurves(action, armature_obj):
	"""Return an Action's F-curves across Blender Action APIs."""

	# Legacy Blender Actions expose F-curves directly.
	if hasattr(action, "fcurves"):
		return list(action.fcurves)

	curves = []
	action_slot = None

	if armature_obj.animation_data is not None:
		action_slot = getattr(
			armature_obj.animation_data,
			"action_slot",
			None,
		)

	for layer in getattr(action, "layers", []):
		for strip in getattr(layer, "strips", []):
			channel_bags = []

			if action_slot is not None and hasattr(strip, "channelbag"):
				try:
					channel_bag = strip.channelbag(
						action_slot,
						ensure=False,
					)

					if channel_bag is not None:
						channel_bags.append(channel_bag)

				except (RuntimeError, TypeError):
					pass

			if not channel_bags:
				channel_bags.extend(
					getattr(strip, "channelbags", [])
				)

			for channel_bag in channel_bags:
				curves.extend(channel_bag.fcurves)

	return curves


def _action_group_channels(action, armature_obj, bone_name: str):
	"""Return the F-curves belonging to one pose bone."""

	escaped_name = bpy.utils.escape_identifier(bone_name)
	prefix = f'pose.bones["{escaped_name}"].'

	return [
		curve
		for curve in _action_fcurves(action, armature_obj)
		if curve.data_path.startswith(prefix)
	]


def _channel_frames(channels):
	"""Collect every keyed Blender frame used by a bone's channels."""

	frames = set()

	for curve in channels:
		for point in curve.keyframe_points:
			frames.add(float(point.co.x))

	return sorted(frames)


def _evaluate_pose_basis(channels, frame_number: float):
	"""Evaluate location, quaternion, and scale from a bone's F-curves."""

	location = [0.0, 0.0, 0.0]
	rotation = [1.0, 0.0, 0.0, 0.0]
	scale = [1.0, 1.0, 1.0]

	for curve in channels:
		value = float(curve.evaluate(frame_number))
		path = curve.data_path
		index = curve.array_index

		if path.endswith("location") and 0 <= index < 3:
			location[index] = value

		elif path.endswith("rotation_quaternion") and 0 <= index < 4:
			rotation[index] = value

		elif path.endswith("scale") and 0 <= index < 3:
			scale[index] = value

	quaternion = mathutils.Quaternion(rotation)

	if quaternion.magnitude == 0.0:
		quaternion = mathutils.Quaternion((1.0, 0.0, 0.0, 0.0))
	else:
		quaternion.normalize()

	translation_matrix = mathutils.Matrix.Translation(
		mathutils.Vector(location)
	)
	rotation_matrix = quaternion.to_matrix().to_4x4()
	scale_matrix = mathutils.Matrix.Diagonal((
		float(scale[0]),
		float(scale[1]),
		float(scale[2]),
		1.0,
	))

	return translation_matrix @ rotation_matrix @ scale_matrix


def _bone_rest_matrix(bone: bpy.types.Bone):
	"""Return the same parent-relative rest matrix used by the decoder."""

	rest_matrix = bone.matrix_local.copy()

	if bone.parent is not None:
		rest_matrix = bone.parent.matrix_local.inverted() @ rest_matrix

	return rest_matrix


def encode_eqganidef(
	parser,
	action: bpy.types.Action,
	armature_obj: bpy.types.Object,
) -> str:
	"""Encode one Blender EQG action into an EQGANIDEF."""

	if action is None:
		return "EQGANIDEF action is None"

	if action.get("quaildef") != "eqganidef":
		return ""

	if armature_obj is None or armature_obj.type != 'ARMATURE':
		return f"EQGANIDEF {action.name} requires armature"

	if not hasattr(action, "quail_eqganidef"):
		return f"EQGANIDEF {action.name} has no EQG animation properties"

	fps_base = float(bpy.context.scene.render.fps_base)

	if fps_base == 0.0:
		return "Scene FPS base cannot be zero"

	fps = float(bpy.context.scene.render.fps) / fps_base

	if fps <= 0.0:
		return "Scene FPS must be greater than zero"

	result = eqganidef()
	result.tag = action.name
	result.version = int(action.quail_eqganidef.version)
	result.strict = 1 if action.quail_eqganidef.strict else 0
	result.bones = []

	for bone in armature_obj.data.bones:
		channels = _action_group_channels(
			action,
			armature_obj,
			bone.name,
		)
		frames = _channel_frames(channels)

		if not frames:
			continue

		encoded_bone = eqganidef.bone()
		encoded_bone.bone = bone.name
		encoded_bone.frames = []

		rest_matrix = _bone_rest_matrix(bone)
		first_frame = frames[0]
		previous_rotation = None

		for frame_number in frames:
			pose_matrix = _evaluate_pose_basis(
				channels,
				frame_number,
			)
			local_animation = rest_matrix @ pose_matrix

			translation, rotation, scale = local_animation.decompose()
			rotation.normalize()

			if (
				previous_rotation is not None
				and previous_rotation.dot(rotation) < 0.0
			):
				rotation.negate()

			previous_rotation = rotation.copy()

			encoded_frame = eqganidef.bone.frame()
			encoded_frame.milliseconds = int(round(
				((frame_number - first_frame) / fps) * 1000.0
			))
			encoded_frame.translation = (
				float(translation.x),
				float(translation.y),
				float(translation.z),
			)
			encoded_frame.rotation = (
				float(rotation.x),
				float(rotation.y),
				float(rotation.z),
				float(-rotation.w),
			)
			encoded_frame.scale = (
				float(scale.x),
				float(scale.y),
				float(scale.z),
			)

			encoded_bone.frames.append(encoded_frame)

		result.bones.append(encoded_bone)

	if not hasattr(parser, "eqganidefs"):
		return "Parser has no eqganidefs collection"

	parser.eqganidefs[result.tag] = result
	return ""