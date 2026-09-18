# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy, mathutils
from bpy.props import EnumProperty, PointerProperty, StringProperty
from ...common import state


def find_armature(obj):
	if obj.parent and obj.parent.type == 'ARMATURE':
		return obj.parent

	for constraint in obj.constraints:
		if constraint.type == 'CHILD_OF' and constraint.target and constraint.target.type == 'ARMATURE':
			return constraint.target

	return None


def find_particlepointdef_armature(collection):
	tag = str(collection.get("tag", "")).strip()

	if not tag:
		return None

	armature = bpy.data.objects.get(f"{tag}_armature")

	if armature is not None and armature.type == 'ARMATURE':
		return armature

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


class OBJECT_OT_add_eqg_particlepoint(bpy.types.Operator):
	bl_idname = "object.add_eqg_particlepoint"
	bl_label = "Add Particle Point"
	bl_description = "Add a particle point using the armature's first bone"
	bl_options = {'REGISTER', 'UNDO'}

	collection_name: StringProperty(
		options={'HIDDEN'},
	)

	@classmethod
	def poll(cls, context):
		collection = context.collection

		return (
			collection is not None
			and collection.get("quaildef") == "eqgparticlepointdef"
		)

	def execute(self, context):
		collection = bpy.data.collections.get(self.collection_name)

		if collection is None:
			self.report(
				{'ERROR'},
				"Particle-point collection not found",
			)
			return {'CANCELLED'}

		tag = str(collection.get("tag", "")).strip()

		if not tag:
			self.report(
				{'ERROR'},
				f"Collection {collection.name} has no model tag",
			)
			return {'CANCELLED'}

		armature_name = f"{tag}_armature"
		armature = bpy.data.objects.get(armature_name)

		if armature is None:
			self.report(
				{'ERROR'},
				f"Armature object {armature_name} not found",
			)
			return {'CANCELLED'}

		if armature.type != 'ARMATURE':
			self.report(
				{'ERROR'},
				f"Object {armature_name} is not an armature",
			)
			return {'CANCELLED'}

		if not armature.data.bones:
			self.report(
				{'ERROR'},
				f"Armature {armature.name} has no bones",
			)
			return {'CANCELLED'}

		bone_name = armature.data.bones[0].name

		obj = bpy.data.objects.new(
			f"{tag}_PARTICLEPOINT",
			None,
		)
		obj.empty_display_type = 'PLAIN_AXES'
		obj.empty_display_size = 0.25
		obj["quaildef"] = "eqgparticlepointdef"

		collection.objects.link(obj)

		obj.parent = armature
		obj.matrix_parent_inverse = mathutils.Matrix.Identity(4)
		obj.location = (0.0, 0.0, 0.0)
		obj.rotation_mode = 'XYZ'
		obj.rotation_euler = (0.0, 0.0, 0.0)
		obj.scale = (1.0, 1.0, 1.0)

		was_updating = state.QUAIL_UPDATING
		state.QUAIL_UPDATING = True

		try:
			obj.quail_eqgparticlepoint.bonename = bone_name
		finally:
			state.QUAIL_UPDATING = was_updating

		constraint = obj.constraints.new(type='CHILD_OF')
		constraint.name = bone_name
		constraint.target = armature
		constraint.subtarget = bone_name
		constraint.owner_space = 'LOCAL'
		constraint.target_space = 'POSE'
		constraint.inverse_matrix = mathutils.Matrix.Identity(4)

		for selected_obj in context.selected_objects:
			selected_obj.select_set(False)

		obj.select_set(True)
		context.view_layer.objects.active = obj

		self.report(
			{'INFO'},
			f"Added {obj.name} on bone {bone_name}",
		)

		return {'FINISHED'}


def draw_eqgparticlepointdef_in_visibility(self, context):
	collection = context.collection

	if not collection or collection.get("quaildef") != "eqgparticlepointdef":
		return

	layout = self.layout
	layout.separator()

	box = layout.box()
	box.label(text="EQGPARTICLEPOINTDEF")
	box.prop(collection.quail_eqgparticlepointdef, "version")
	operator = box.operator(
		"object.add_eqg_particlepoint",
		text="Add Particle Point",
		icon='ADD',
	)
	operator.collection_name = collection.name


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
