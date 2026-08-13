# pyright: basic, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false

import math

import bpy
import mathutils

from .context import Context
from ..common import state
from ..wce.eqgparticlepointdef import eqgparticlepointdef


def ensure_particlepoint_collection(parent_collection, tag: str):
	collection_name = f"{tag}_PARTICLEPOINTDEF"
	particlepoint_collection = parent_collection.children.get(collection_name)
	if particlepoint_collection:
		return particlepoint_collection

	particlepoint_collection = bpy.data.collections.get(collection_name)
	if not particlepoint_collection:
		particlepoint_collection = bpy.data.collections.new(collection_name)

	parent_collection.children.link(particlepoint_collection)
	return particlepoint_collection


def decode_eqgparticlepointdef(
	ctx: Context,
	particlepointdef: eqgparticlepointdef,
) -> str:
	# ------------------------------------------------
	# Find the corresponding armature
	# ------------------------------------------------
	armature_name = f"{particlepointdef.tag}_armature"
	armature_obj = bpy.data.objects.get(armature_name)

	if armature_obj is None:
		return f"Armature {armature_name} not found"

	if armature_obj.type != 'ARMATURE':
		return f"Object {armature_name} is not an armature"

	# Validate every reference before creating the collection or any empties.
	for point in particlepointdef.points:
		if not armature_obj.data.bones.get(point.bonename):
			return (
				f"Particle point {point.point}: "
				f"bone {point.bonename} not found in "
				f"armature {armature_name}"
			)

	# ------------------------------------------------
	# Create the particle-point collection beneath the collection containing
	# the corresponding armature.
	# ------------------------------------------------
	if not armature_obj.users_collection:
		return f"Armature {armature_name} does not belong to a collection"

	armature_collection = armature_obj.users_collection[0]

	particlepoint_collection = ensure_particlepoint_collection(
		armature_collection,
		particlepointdef.tag,
	)
	particlepoint_collection["quaildef"] = "eqgparticlepointdef"
	particlepoint_collection["tag"] = particlepointdef.tag

	was_updating = state.QUAIL_UPDATING
	state.QUAIL_UPDATING = True
	try:
		particlepoint_collection.quail_eqgparticlepointdef.version = particlepointdef.version
	finally:
		state.QUAIL_UPDATING = was_updating

	# ------------------------------------------------
	# Create particle-point empties
	# ------------------------------------------------
	for point in particlepointdef.points:
		obj = bpy.data.objects.new(point.point, None)

		obj.empty_display_type = 'PLAIN_AXES'
		obj.empty_display_size = 0.25
		obj['quaildef'] = 'eqgparticlepointdef'

		was_updating = state.QUAIL_UPDATING
		state.QUAIL_UPDATING = True
		try:
			obj.quail_eqgparticlepoint.bonename = point.bonename
		finally:
			state.QUAIL_UPDATING = was_updating

		# Parent the object beneath the armature while retaining membership in
		# the dedicated PARTICLEPOINTDEF collection.
		obj.parent = armature_obj
		obj.matrix_parent_inverse = mathutils.Matrix.Identity(4)

		# ------------------------------------------------
		# Apply point-local transform
		# ------------------------------------------------
		obj.location = (
			float(point.translation[0]),
			float(point.translation[1]),
			float(point.translation[2]),
		)

		obj.rotation_mode = 'XYZ'
		obj.rotation_euler = (
			float(point.rotation[0]) * (2.0 * math.pi / 512.0),
			float(point.rotation[1]) * (2.0 * math.pi / 512.0),
			float(point.rotation[2]) * (2.0 * math.pi / 512.0),
		)

		obj.scale = (
			float(point.scale[0]),
			float(point.scale[1]),
			float(point.scale[2]),
		)

		# ------------------------------------------------
		# Follow the specified armature bone
		# ------------------------------------------------
		constraint = obj.constraints.new(type='CHILD_OF')
		constraint.name = point.bonename
		constraint.target = armature_obj
		constraint.subtarget = point.bonename
		constraint.owner_space = 'LOCAL'
		constraint.target_space = 'POSE'
		constraint.inverse_matrix = mathutils.Matrix.Identity(4)

		particlepoint_collection.objects.link(obj)

	return ""
