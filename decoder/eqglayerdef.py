# pyright: basic, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false

import bpy

from .context import Context
from ..common import state
from ..common.image_loader import load_eqg_image
from ..wce.eqglayerdef import eqglayerdef


def ensure_layerdef_collection(parent_collection, tag: str):
	name = f"{tag}_LAYERDEF"
	collection = parent_collection.children.get(name)

	if collection:
		return collection

	collection = bpy.data.collections.get(name)
	if not collection:
		collection = bpy.data.collections.new(name)

	parent_collection.children.link(collection)
	return collection


def load_layer_image(ctx: Context, filename: str):
	if not filename:
		return None

	image, err = load_eqg_image(ctx, filename, flip_tex=False)
	if err:
		print(f"Unable to load EQGLAYERDEF texture {filename}: {err}")
		return None

	return image


def find_layerdef_parent_collection(tag: str):
	prefix = tag[:3].casefold()
	matching_armatures = []

	for obj in bpy.data.objects:
		if obj.type != 'ARMATURE':
			continue
		if obj.name[:3].casefold() != prefix:
			continue
		matching_armatures.append(obj)

	if not matching_armatures:
		return None, f"Armature beginning with {tag[:3]} not found for EQGLAYERDEF {tag}"

	if len(matching_armatures) > 1:
		names = ", ".join(obj.name for obj in matching_armatures)
		return None, f"Multiple armatures beginning with {tag[:3]} found for EQGLAYERDEF {tag}: {names}"

	armature = matching_armatures[0]
	if not armature.users_collection:
		return None, f"Armature {armature.name} does not belong to a collection"

	return armature.users_collection[0], ""


def decode_eqglayerdef(ctx: Context, layerdef: eqglayerdef) -> str:
	parent_collection, err = find_layerdef_parent_collection(layerdef.tag)
	if err:
		return err

	collection = ensure_layerdef_collection(parent_collection, layerdef.tag)
	collection["quaildef"] = "eqglayerdef"

	props = collection.quail_eqglayerdef
	was_updating = state.QUAIL_UPDATING
	state.QUAIL_UPDATING = True

	try:
		props.tag = layerdef.tag
		props.version = layerdef.version
		props.layers.clear()

		for source_layer in layerdef.layers:
			layer = props.layers.add()
			layer.material = source_layer.material
			layer.diffuse_filename = source_layer.diffuse
			layer.normal_filename = source_layer.normal
			layer.diffuse = load_layer_image(ctx, source_layer.diffuse)
			layer.normal = load_layer_image(ctx, source_layer.normal)
	finally:
		state.QUAIL_UPDATING = was_updating

	return ""
