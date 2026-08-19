# pyright: basic, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false, reportOptionalSubscript=false

import os
import bpy

from ..wce.eqglayerdef import eqglayerdef


def _image_filename(image):
	if image is None:
		return ""

	source_name = image.get("quail_source_name", "")

	if source_name:
		return os.path.basename(str(source_name))

	if image.filepath:
		return os.path.basename(bpy.path.abspath(image.filepath))

	return os.path.basename(image.name)


def encode_eqglayerdef(parser, collection: bpy.types.Collection) -> str:
	if collection.get("quaildef") != "eqglayerdef":
		return ""

	if not hasattr(collection, "quail_eqglayerdef"):
		return f"EQGLAYERDEF collection {collection.name} has no layer properties"

	props = collection.quail_eqglayerdef
	result = eqglayerdef()
	result.tag = collection.name[:-9] if collection.name.casefold().endswith("_layerdef") else collection.name
	result.version = int(props.version)
	result.layers = []

	for layer_index, source_layer in enumerate(props.layers):
		layer = eqglayerdef.layer()
		layer.material = source_layer.material
		layer.texture0 = ""
		layer.texture1 = ""
		layer.texture2 = ""
		layer.texture3 = ""
		layer.texture4 = ""
		layer.shininess = float(source_layer.shininess)
		layer.rendertype = float(source_layer.rendertype)
		used_indices = set()

		for source_texture in source_layer.textures:
			texture_index = int(source_texture.texture_index)

			if texture_index < 0 or texture_index > 4:
				return (
					f"EQGLAYERDEF {result.tag} layer {layer_index} has "
					f"invalid texture index {texture_index}"
				)

			if texture_index in used_indices:
				return (
					f"EQGLAYERDEF {result.tag} layer {layer_index} has "
					f"duplicate texture index {texture_index}"
				)

			used_indices.add(texture_index)
			filename = source_texture.filename.strip()

			if not filename:
				filename = _image_filename(source_texture.image)

			setattr(layer, f"texture{texture_index}", filename)

		result.layers.append(layer)

	if not hasattr(parser, "eqglayerdefs"):
		return "Parser has no eqglayerdefs collection"

	parser.eqglayerdefs[result.tag] = result
	return ""
