# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import EnumProperty, PointerProperty, StringProperty
from ...common import state


def find_armature(obj):
	if obj.parent and obj.parent.type == 'ARMATURE':
		return obj.parent

	for constraint in obj.constraints:
		if constraint.type == 'CHILD_OF' and constraint.target and constraint.target.type == 'ARMATURE':
			return constraint.target

	return None


def find_bone_constraint(obj):
	for constraint in obj.constraints:
		if constraint.type == 'CHILD_OF' and constraint.target and constraint.target.type == 'ARMATURE':
			return constraint
	return None


def update_particlepoint_bone(self, context):
	if state.QUAIL_UPDATING:
		return

	obj = self.id_data
	if not obj or obj.get("quaildef") != "eqgparticlepointdef":
		return

	armature = find_armature(obj)
	if not armature:
		print(f"Particle point {obj.name}: armature not found")
		return

	bone_name = self.bonename.strip()
	if not armature.data.bones.get(bone_name):
		print(
			f"Particle point {obj.name}: bone {bone_name} not found in "
			f"armature {armature.name}"
		)
		return

	constraint = find_bone_constraint(obj)
	if not constraint:
		constraint = obj.constraints.new(type='CHILD_OF')
		constraint.target = armature
		constraint.owner_space = 'LOCAL'
		constraint.target_space = 'POSE'

	constraint.name = bone_name
	constraint.target = armature
	constraint.subtarget = bone_name


class QuailEqgParticlePointDefProperties(bpy.types.PropertyGroup):
	version: EnumProperty(name="Version", items=[('1', "1", "")], default='1')


class QuailEqgParticlePointProperties(bpy.types.PropertyGroup):
	bonename: StringProperty(
		name="Bone",
		description="Armature bone followed by this particle point",
		update=update_particlepoint_bone,
	)


def draw_eqgparticlepointdef_in_visibility(self, context):
	collection = context.collection
	if not collection or collection.get("quaildef") != "eqgparticlepointdef":
		return

	layout = self.layout
	layout.separator()
	box = layout.box()
	box.label(text="EQGPARTICLEPOINTDEF")
	box.prop(collection.quail_eqgparticlepointdef, "version")


def draw_eqgparticlepoint_in_transform(self, context):
	obj = context.object
	if not obj or obj.get("quaildef") != "eqgparticlepointdef":
		return

	box = self.layout.box()
	box.label(text="EQGPARTICLEPOINT")
	box.prop(obj.quail_eqgparticlepoint, "bonename")


def register():
	bpy.types.Collection.quail_eqgparticlepointdef = PointerProperty(
		type=QuailEqgParticlePointDefProperties
	)
	bpy.types.Object.quail_eqgparticlepoint = PointerProperty(
		type=QuailEqgParticlePointProperties
	)
	bpy.types.COLLECTION_PT_collection_flags.prepend(
		draw_eqgparticlepointdef_in_visibility
	)
	bpy.types.OBJECT_PT_transform.prepend(
		draw_eqgparticlepoint_in_transform
	)


def unregister():
	bpy.types.COLLECTION_PT_collection_flags.remove(
		draw_eqgparticlepointdef_in_visibility
	)
	bpy.types.OBJECT_PT_transform.remove(
		draw_eqgparticlepoint_in_transform
	)
	del bpy.types.Object.quail_eqgparticlepoint
	del bpy.types.Collection.quail_eqgparticlepointdef
