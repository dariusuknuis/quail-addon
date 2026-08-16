# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
import os
from bpy.props import CollectionProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty, StringProperty
from bpy_extras.io_utils import ImportHelper
from ...common import state


def update_layer_texture(self, context):
	if state.QUAIL_UPDATING:
		return
	if self.image:
		self.filename = self.image.name


class QuailEqgLayerTextureProperties(bpy.types.PropertyGroup):
	texture_index: IntProperty(name="Texture Index", min=0, max=4)
	filename: StringProperty(name="Filename")
	image: PointerProperty(name="Image", type=bpy.types.Image, update=update_layer_texture)


class QuailEqgLayerProperties(bpy.types.PropertyGroup):
	material: StringProperty(name="Material")
	textures: CollectionProperty(type=QuailEqgLayerTextureProperties)
	shininess: FloatProperty(name="Shininess", default=12.0)
	rendertype: FloatProperty(name="Render Type", default=1.0)


class QuailEqgLayerDefProperties(bpy.types.PropertyGroup):
	version: EnumProperty(
		name="Version",
		items=(
			("1", "1", ""),
			("2", "2", ""),
			("3", "3", ""),
			("4", "4", ""),
		),
		default="4",
	)
	layers: CollectionProperty(type=QuailEqgLayerProperties)


class COLLECTION_OT_load_eqg_layer_image(bpy.types.Operator, ImportHelper):
	bl_idname = "collection.load_eqg_layer_image"
	bl_label = "Load EQG Layer Image"
	bl_options = {'REGISTER', 'UNDO'}

	filter_glob: StringProperty(default="*.dds;*.bmp;*.png;*.tga", options={'HIDDEN'})
	collection_name: StringProperty(options={'HIDDEN'})
	layer_index: IntProperty(options={'HIDDEN'})
	texture_row_index: IntProperty(options={'HIDDEN'})

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

		layer = props.layers[self.layer_index]
		if not 0 <= self.texture_row_index < len(layer.textures):
			self.report({'ERROR'}, f"Invalid texture row index: {self.texture_row_index}")
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

		texture = layer.textures[self.texture_row_index]
		texture.filename = filename
		texture.image = image

		return {'FINISHED'}


class COLLECTION_OT_add_eqg_layer_texture(bpy.types.Operator):
	bl_idname = "collection.add_eqg_layer_texture"
	bl_label = "Add EQG Layer Texture"
	bl_options = {'REGISTER', 'UNDO'}

	collection_name: StringProperty(options={'HIDDEN'})
	layer_index: IntProperty(options={'HIDDEN'})

	def execute(self, context):
		collection = bpy.data.collections.get(self.collection_name)
		if not collection or collection.get("quaildef") != "eqglayerdef":
			self.report({'ERROR'}, f"EQGLAYERDEF collection not found: {self.collection_name}")
			return {'CANCELLED'}

		props = collection.quail_eqglayerdef
		if not 0 <= self.layer_index < len(props.layers):
			self.report({'ERROR'}, f"Invalid layer index: {self.layer_index}")
			return {'CANCELLED'}

		layer = props.layers[self.layer_index]
		used_indices = {texture.texture_index for texture in layer.textures}

		for texture_index in range(5):
			if texture_index in used_indices:
				continue

			texture = layer.textures.add()
			texture.texture_index = texture_index
			return {'FINISHED'}

		self.report({'WARNING'}, "All five texture slots are already present")
		return {'CANCELLED'}


class COLLECTION_OT_remove_eqg_layer_texture(bpy.types.Operator):
	bl_idname = "collection.remove_eqg_layer_texture"
	bl_label = "Remove EQG Layer Texture"
	bl_options = {'REGISTER', 'UNDO'}

	collection_name: StringProperty(options={'HIDDEN'})
	layer_index: IntProperty(options={'HIDDEN'})
	texture_row_index: IntProperty(options={'HIDDEN'})

	def execute(self, context):
		collection = bpy.data.collections.get(self.collection_name)
		if not collection or collection.get("quaildef") != "eqglayerdef":
			self.report({'ERROR'}, f"EQGLAYERDEF collection not found: {self.collection_name}")
			return {'CANCELLED'}

		props = collection.quail_eqglayerdef
		if not 0 <= self.layer_index < len(props.layers):
			self.report({'ERROR'}, f"Invalid layer index: {self.layer_index}")
			return {'CANCELLED'}

		layer = props.layers[self.layer_index]
		if not 0 <= self.texture_row_index < len(layer.textures):
			self.report({'ERROR'}, f"Invalid texture row index: {self.texture_row_index}")
			return {'CANCELLED'}

		layer.textures.remove(self.texture_row_index)
		return {'FINISHED'}


def draw_layer_image(box, collection, layer, layer_index: int, texture_row_index: int):
	texture = layer.textures[texture_row_index]
	row = box.row(align=True)
	row.prop_search(texture, "image", bpy.data, "images", text=f"Texture {texture.texture_index}")

	load = row.operator("collection.load_eqg_layer_image", text="", icon='FILE_FOLDER')
	load.collection_name = collection.name
	load.layer_index = layer_index
	load.texture_row_index = texture_row_index

	remove = row.operator("collection.remove_eqg_layer_texture", text="", icon='X')
	remove.collection_name = collection.name
	remove.layer_index = layer_index
	remove.texture_row_index = texture_row_index

	if not texture.image and texture.filename:
		row = box.row()
		row.label(text=f"Missing: {texture.filename}", icon='ERROR')


def draw_eqglayerdef_in_visibility(self, context):
	collection = context.collection
	if not collection or collection.get("quaildef") != "eqglayerdef":
		return

	props = collection.quail_eqglayerdef
	layout = self.layout
	layout.separator()
	box = layout.box()
	box.label(text="EQGLAYERDEF")
	box.prop(props, "version")
	box.label(text=f"Layers: {len(props.layers)}")

	for layer_index, layer in enumerate(props.layers):
		layer_box = box.box()
		layer_box.label(text=f"Layer {layer_index}")
		layer_box.prop(layer, "material")
		layer_box.prop(layer, "shininess")
		layer_box.prop(layer, "rendertype")

		for texture_row_index in range(len(layer.textures)):
			draw_layer_image(layer_box, collection, layer, layer_index, texture_row_index)

		if len(layer.textures) < 5:
			add = layer_box.operator("collection.add_eqg_layer_texture", text="Add Texture", icon='ADD')
			add.collection_name = collection.name
			add.layer_index = layer_index


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