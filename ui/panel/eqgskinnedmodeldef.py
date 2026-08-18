# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
import bmesh

from bpy.props import PointerProperty, EnumProperty, BoolProperty
from .eqgface import ensure_face_layers, get_face_property, FACE_PROPS


class QuailEqgSkinnedModelDefProperties(bpy.types.PropertyGroup):
	version: EnumProperty(
		name="Version",
		description="Version of the Skinned Model",
		items=[
			('1', "1", "First version"),
		],
		default='1',
	)

	mainpiece: BoolProperty(
		name="Main Piece",
		description="Mark this mesh as the main model piece",
		default=False,
	)


class OBJECT_OT_add_quail_eqgskinnedmodeldef(bpy.types.Operator):
	"""Create a new EQGSKINNEDMODELDEF mesh piece."""

	bl_idname = "object.add_quail_eqgskinnedmodeldef"
	bl_label = "EqgSkinnedModelDef"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		mesh = bpy.data.meshes.new("EqgSkinnedModelDefMesh")
		obj = bpy.data.objects.new("EqgSkinnedModelDef", mesh)
		obj["quaildef"] = "eqgskinnedmodeldef"
		context.collection.objects.link(obj)

		bpy.ops.object.select_all(action='DESELECT')
		obj.select_set(True)
		context.view_layer.objects.active = obj
		return {'FINISHED'}


def _is_skinned_armature(obj):
	if obj.type != 'ARMATURE' or obj.get("quaildef") != "eqgmodarmature":
		return False

	return any(
		child.get("quaildef") == "eqgskinnedmodeldef"
		for child in obj.children
	)


def draw_eqgskinnedmodeldef_in_transform(self, context):
	obj = context.object

	if not obj:
		return

	is_mesh_piece = (
		obj.type == 'MESH'
		and obj.get("quaildef") == "eqgskinnedmodeldef"
	)

	if not is_mesh_piece and not _is_skinned_armature(obj):
		return

	layout = self.layout
	box = layout.box()
	box.label(text="EQGSKINNEDMODELDEF")

	if obj.type == 'ARMATURE':
		box.prop(obj.quail_eqgskinnedmodeldef, "version")
		return

	box.prop(obj.quail_eqgskinnedmodeldef, "mainpiece")

	if context.mode != 'EDIT_MESH':
		return

	mesh = obj.data

	try:
		ensure_face_layers(mesh)
		bm = bmesh.from_edit_mesh(mesh)
		bm.faces.ensure_lookup_table()
		selected_faces = [face for face in bm.faces if face.select]

		if len(selected_faces) != 1:
			info_box = layout.box()
			info_box.label(
				text="Select exactly one face to edit its properties.",
				icon='INFO',
			)
			return

		face = selected_faces[0]
		face_index = face.index
		face_box = layout.box()
		face_box.label(text=f"Face Properties ({face_index})")

		for prop_name in FACE_PROPS:
			prop_value = get_face_property(mesh, face_index, prop_name)
			icon = 'CHECKBOX_HLT' if prop_value else 'CHECKBOX_DEHLT'
			operator = face_box.operator(
				"mesh.quail_toggle_face_property",
				text=prop_name,
				icon=icon,
			)
			operator.face_index = face_index
			operator.prop_name = prop_name
			operator.new_value = not prop_value

	except Exception as error:
		error_box = layout.box()
		error_box.label(
			text=f"Error processing face data: {error}",
			icon='ERROR',
		)


def register():
	if not hasattr(bpy.types.Object, "quail_eqgskinnedmodeldef"):
		bpy.types.Object.quail_eqgskinnedmodeldef = PointerProperty(
			type=QuailEqgSkinnedModelDefProperties
		)

	bpy.types.OBJECT_PT_transform.prepend(
		draw_eqgskinnedmodeldef_in_transform
	)


def unregister():
	try:
		bpy.types.OBJECT_PT_transform.remove(
			draw_eqgskinnedmodeldef_in_transform
		)
	except ValueError:
		pass

	if hasattr(bpy.types.Object, "quail_eqgskinnedmodeldef"):
		del bpy.types.Object.quail_eqgskinnedmodeldef
