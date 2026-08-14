# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
from bpy.props import BoolProperty, IntProperty, PointerProperty


class QuailWorldDefProperties(bpy.types.PropertyGroup):
	newworld: BoolProperty(name="New World", default=False)
	zone: BoolProperty(name="Zone", default=False)
	eqgzoneversion: IntProperty(name="EQG Zone Version", default=0)
	use_eqg: BoolProperty(name="EQG", default=False)
	eqgversion: IntProperty(name="EQG Version", default=0)


class QUAIL_OT_make_worlddef(bpy.types.Operator):
	bl_idname = "quail.make_worlddef"
	bl_label = "Make WORLDDEF"
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		col = context.collection
		return bool(col and not col.get("quaildef"))

	def execute(self, context):
		col = context.collection
		col["quaildef"] = "worlddef"
		return {'FINISHED'}


class QUAIL_PT_worlddef_collection(bpy.types.Panel):
	bl_label = "WORLDDEF"
	bl_idname = "QUAIL_PT_worlddef_collection"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "collection"

	@classmethod
	def poll(cls, context):
		col = context.collection
		if not col:
			return False

		quaildef = col.get("quaildef")
		return quaildef == "worlddef" or quaildef is None

	def draw(self, context):
		layout = self.layout
		col = context.collection

		if not col.get("quaildef"):
			layout.operator("quail.make_worlddef", icon='WORLD')
			return

		props = col.quail_worlddef
		box = layout.box()
		box.label(text="WORLDDEF")
		box.prop(props, "newworld")
		box.prop(props, "zone")
		box.prop(props, "use_eqg")

		if props.zone and props.use_eqg:
			box.prop(props, "eqgzoneversion")

		if props.use_eqg:
			box.prop(props, "eqgversion")


def register():
	bpy.types.Collection.quail_worlddef = PointerProperty(
		type=QuailWorldDefProperties
	)


def unregister():
	del bpy.types.Collection.quail_worlddef
