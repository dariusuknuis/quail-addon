# pyright: basic, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false, reportOptionalSubscript=false

import math

import bpy

from ..wce.eqgparticlepointdef import eqgparticlepointdef


def _definition_tag(collection: bpy.types.Collection) -> str:
	name = collection.name
	return name[:-17] if name.casefold().endswith("_particlepointdef") else name


def _bone_name(obj: bpy.types.Object) -> str:
	if hasattr(obj, "quail_eqgparticlepoint"):
		bone_name = obj.quail_eqgparticlepoint.bonename.strip()

		if bone_name:
			return bone_name

	for constraint in obj.constraints:
		if constraint.type == 'CHILD_OF' and constraint.subtarget:
			return constraint.subtarget

	return ""


def encode_eqgparticlepointdef(parser, collection: bpy.types.Collection) -> str:
	if collection.get("quaildef") != "eqgparticlepointdef":
		return ""

	if not hasattr(collection, "quail_eqgparticlepointdef"):
		return f"EQGPARTICLEPOINTDEF collection {collection.name} has no definition properties"

	result = eqgparticlepointdef()
	result.tag = _definition_tag(collection)
	result.version = int(collection.quail_eqgparticlepointdef.version)
	result.points = []
	armature_name = f"{result.tag}_armature"
	armature_obj = bpy.data.objects.get(armature_name)

	if armature_obj is None:
		return f"Armature {armature_name} not found for EQGPARTICLEPOINTDEF {result.tag}"

	if armature_obj.type != 'ARMATURE':
		return f"Object {armature_name} is not an armature"

	rotation_scale = 512.0 / (2.0 * math.pi)

	for obj in collection.objects:
		if obj.get("quaildef") != "eqgparticlepointdef":
			continue

		if obj.type != 'EMPTY':
			return f"Particle point {obj.name} is not an empty"

		bone_name = _bone_name(obj)

		if not bone_name:
			return f"Particle point {obj.name} has no bone name"

		if armature_obj.data.bones.get(bone_name) is None:
			return f"Particle point {obj.name}: bone {bone_name} not found in armature {armature_name}"

		rotation = obj.matrix_basis.to_quaternion().to_euler('XYZ')
		point = eqgparticlepointdef.point()
		point.point = obj.name
		point.bonename = bone_name
		point.translation = (float(obj.location.x), float(obj.location.y), float(obj.location.z))
		point.rotation = (
			float(rotation.x * rotation_scale),
			float(rotation.y * rotation_scale),
			float(rotation.z * rotation_scale),
		)
		point.scale = (float(obj.scale.x), float(obj.scale.y), float(obj.scale.z))
		result.points.append(point)

	if not hasattr(parser, "eqgparticlepointdefs"):
		return "Parser has no eqgparticlepointdefs collection"

	parser.eqgparticlepointdefs[result.tag] = result
	return ""
