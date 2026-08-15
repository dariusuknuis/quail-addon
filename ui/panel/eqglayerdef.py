# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
import os
from bpy.props import CollectionProperty, EnumProperty, IntProperty, PointerProperty, StringProperty
from bpy_extras.io_utils import ImportHelper
from ...common import state


def update_layer_diffuse(self, context):
	if state.QUAIL_UPDATING:
		return
	if self.diffuse:
		self.diffuse_filename = self.diffuse.name


def update_layer_normal(self, context):
	if state.QUAIL_UPDATING:
		return
	if self.normal:
		self.normal_filename = self.normal.name


class QuailEqgLayerProperties(bpy.types.PropertyGroup):
	material: StringProperty(name="Material")
	diffuse_filename: StringProperty(name="Diffuse Filename")
	normal_filename: StringProperty(name="Normal Filename")
	diffuse: PointerProperty(name="Diffuse", type=bpy.types.Image, update=update_layer_diffuse)
	normal: PointerProperty(name="Normal", type=bpy.types.Image, update=update_layer_normal)


class QuailEqgLayerDefProperties(bpy.types.PropertyGroup):
	tag: StringProperty(name="Tag")
	version: IntProperty(name="Version", min=0)
	layers: CollectionProperty(type=QuailEqgLayerProperties)


class COLLECTION_OT_load_eqg_layer_image(bpy.types.Operator, ImportHelper):
	bl_idname = "collection.load_eqg_layer_image"
	bl_label = "Load EQG Layer Image"
	bl_options = {'REGISTER', 'UNDO'}

	filter_glob: StringProperty(default="*.dds;*.bmp;*.png;*.tga", options={'HIDDEN'})
	collection_name: StringProperty(options={'HIDDEN'})
	layer_index: IntProperty(options={'HIDDEN'})
	texture_type: EnumProperty(items=[('DIFFUSE', "Diffuse", ""), ('NORMAL', "Normal", "")], options={'HIDDEN'})

	def execute(self, context):
		from ...common.image_loader import load_eqg_image

		collection = bpy.data.collections.get(self.collection_name)
		if not collection or collection.get("quaildef") != "eqglayerdef":
			self.report({'ERROR'}, f"EQGLAYERDEF collection not found: {self.collection_name}")
			return {'CANCELLED'}

		props = collection.quail_eqglayerdef
		if not 0 <= self.layer_index < len(props.layers):
			self.report({'ERROR'}, f"Invalid layer index: {self.layer_index}")
			return {'CANCELLED'}

		assets_path = os.path.dirname(self.filepath)
		filename = bpy.path.basename(self.filepath)
		loader_context = type("EqgLayerImageLoaderContext", (), {"parser": type("EqgLayerImageLoaderParser", (), {"assets_path": assets_path})()})()
		image, err = load_eqg_image(loader_context, filename, flip_tex=False)

		if err:
			self.report({'ERROR'}, err)
			return {'CANCELLED'}
		if image is None:
			self.report({'ERROR'}, f"Could not load image: {self.filepath}")
			return {'CANCELLED'}

		layer = props.layers[self.layer_index]
		if self.texture_type == 'DIFFUSE':
			layer.diffuse_filename = filename
			layer.diffuse = image
		else:
			layer.normal_filename = filename
			layer.normal = image

		return {'FINISHED'}


def draw_layer_image(box, collection, layer, index: int, texture_type: str):
	property_name = texture_type.lower()
	filename_name = f"{property_name}_filename"
	row = box.row(align=True)
	row.prop_search(layer, property_name, bpy.data, "images", text=texture_type.title())
	load = row.operator("collection.load_eqg_layer_image", text="", icon='FILE_FOLDER')
	load.collection_name = collection.name
	load.layer_index = index
	load.texture_type = texture_type

	if not getattr(layer, property_name) and getattr(layer, filename_name):
		row = box.row()
		row.label(text=f"Missing: {getattr(layer, filename_name)}", icon='ERROR')


def draw_eqglayerdef_in_visibility(self, context):
	collection = context.collection
	if not collection or collection.get("quaildef") != "eqglayerdef":
		return

	props = collection.quail_eqglayerdef
	layout = self.layout
	layout.separator()
	box = layout.box()
	box.label(text="EQGLAYERDEF")
	box.prop(props, "tag")
	box.prop(props, "version")
	box.label(text=f"Layers: {len(props.layers)}")

	for index, layer in enumerate(props.layers):
		layer_box = box.box()
		layer_box.label(text=f"Layer {index}")
		layer_box.prop(layer, "material")
		draw_layer_image(layer_box, collection, layer, index, 'DIFFUSE')
		draw_layer_image(layer_box, collection, layer, index, 'NORMAL')


def register():
	bpy.types.Collection.quail_eqglayerdef = PointerProperty(type=QuailEqgLayerDefProperties)
	bpy.types.COLLECTION_PT_collection_flags.prepend(draw_eqglayerdef_in_visibility)


def unregister():
	try:
		bpy.types.COLLECTION_PT_collection_flags.remove(draw_eqglayerdef_in_visibility)
	except ValueError:
		pass

	if hasattr(bpy.types.Collection, "quail_eqglayerdef"):
		del bpy.types.Collection.quail_eqglayerdef
