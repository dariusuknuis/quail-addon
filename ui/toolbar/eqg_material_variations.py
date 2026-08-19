# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import os
import re
import bpy
from bpy.props import CollectionProperty, EnumProperty, IntProperty, PointerProperty
from ...common import state
from ...common.eqgshaders import eqg_apply


LAYER_MATERIAL_REGEX = re.compile(r"^([CA])_(.+)_S(\d+)_M(\d+)$", re.IGNORECASE)
BLENDER_NUMBER_SUFFIX_REGEX = re.compile(r"\.\d{3}$")
EQG_MODEL_QDEFS = {"eqgmodeldef", "eqgskinnedmodeldef"}


def clean_model_tag(name: str):
	return BLENDER_NUMBER_SUFFIX_REGEX.sub("", name).casefold()


def parse_layer_material(name: str):
	match = LAYER_MATERIAL_REGEX.match(name.strip())
	if not match:
		return None

	return {
		"kind": match.group(1).upper(),
		"family": match.group(2).casefold(),
		"variation": int(match.group(3)),
		"material_number": int(match.group(4)),
	}


def iter_layer_entries():
	for collection in bpy.data.collections:
		if collection.get("quaildef") != "eqglayerdef":
			continue
		if not hasattr(collection, "quail_eqglayerdef"):
			continue
		for layer in collection.quail_eqglayerdef.layers:
			parsed = parse_layer_material(layer.material)
			if parsed:
				yield layer, parsed


def attachment_family_candidates(model_tag: str):
	candidates = {model_tag}
	root_body_suffix = "_root_body"
	if model_tag.endswith(root_body_suffix):
		candidates.add(model_tag[:-len(root_body_suffix)])

	for candidate in tuple(candidates):
		if candidate.endswith("_00"):
			candidates.add(candidate[:-3])

	return candidates


def matching_layers(obj, variation: int):
	model_tag = model_tag_for_object(obj)
	entries = list(iter_layer_entries())
	a_candidates = attachment_family_candidates(model_tag)
	a_families = {
		parsed["family"]
		for _layer, parsed in entries
		if parsed["kind"] == "A" and parsed["family"] in a_candidates
	}
	a_family = max(a_families, key=len) if a_families else None
	result = {}

	for layer, parsed in entries:
		if parsed["variation"] != variation:
			continue

		if parsed["kind"] == "C":
			family = parsed["family"]
			if family != model_tag and not family.startswith(f"{model_tag}_"):
				continue
		elif parsed["kind"] == "A":
			if a_family is None or parsed["family"] != a_family:
				continue
		else:
			continue

		result[parsed["material_number"]] = layer

	return result


def is_failsafe_material(material):
	if material is None:
		return True
	name = material.name.casefold()
	return name == "failsafeshader" or name.endswith("_failsafeshader")


def eligible_material_slots(obj):
	return [
		index
		for index, slot in enumerate(obj.material_slots)
		if slot.material and not is_failsafe_material(slot.material)
	]


def layer_texture_overrides(layer):
	images_by_type = {"C": [], "N": [], "E": []}

	for texture in sorted(layer.textures, key=lambda item: item.texture_index):
		filename = texture.filename or (texture.image.name if texture.image else "")
		stem = os.path.splitext(os.path.basename(filename))[0]
		if not stem:
			continue

		texture_type = stem[-1].upper()
		if texture_type not in images_by_type:
			continue

		image = texture.image
		if image is None:
			image = bpy.data.images.get(filename)
		if image is None:
			image = bpy.data.images.get(os.path.basename(filename))
		if image is not None:
			images_by_type[texture_type].append(image)

	overrides = {"e_fShininess0": layer.shininess}

	for index, image in enumerate(images_by_type["C"][:2]):
		overrides[f"e_TextureDiffuse{index}"] = image
	for index, image in enumerate(images_by_type["N"][:2]):
		overrides[f"e_TextureNormal{index}"] = image
	for index, image in enumerate(images_by_type["E"][:2]):
		property_name = "e_TextureEnvironment0" if index == 0 else "e_TextureEnvironment"
		overrides[property_name] = image

	return overrides


def model_tag_for_object(obj):
	if obj.get("quaildef") != "eqgskinnedmodeldef":
		return clean_model_tag(obj.name)

	armature = obj.parent if obj.parent and obj.parent.type == 'ARMATURE' else None

	if armature is None:
		for modifier in obj.modifiers:
			if modifier.type == 'ARMATURE' and modifier.object:
				armature = modifier.object
				break

	name = armature.name if armature else obj.name
	name = name[:-9] if name.casefold().endswith("_armature") else name
	return clean_model_tag(name)


class QuailEqgVariationSlot(bpy.types.PropertyGroup):
	slot_index: IntProperty(default=-1)
	original_link: EnumProperty(items=[('DATA', "Data", ""), ('OBJECT', "Object", "")], default='DATA')
	original_material: PointerProperty(type=bpy.types.Material)
	preview_material: PointerProperty(type=bpy.types.Material)


def restore_eqg_material_variation(obj):
	if not hasattr(obj, "quail_eqg_material_variation"):
		return

	props = obj.quail_eqg_material_variation
	previews = []

	for saved in props.slots:
		if not 0 <= saved.slot_index < len(obj.material_slots):
			continue

		slot = obj.material_slots[saved.slot_index]
		if saved.original_link == 'OBJECT':
			slot.link = 'OBJECT'
			slot.material = saved.original_material
		else:
			slot.link = 'DATA'

		if saved.preview_material:
			previews.append(saved.preview_material)

	props.slots.clear()

	for material in previews:
		if material.users == 0:
			bpy.data.materials.remove(material)


def apply_eqg_material_variation(obj, variation: int):
	restore_eqg_material_variation(obj)
	if variation == 0:
		obj.data.update()
		return ""

	layers = matching_layers(obj, variation)
	if not layers:
		return f"No EQGLAYERDEF entries match {obj.name} variation S{variation:02d}"

	eligible_slots = eligible_material_slots(obj)
	props = obj.quail_eqg_material_variation

	for material_number, layer in sorted(layers.items()):
		ordinal = material_number - 1
		if not 0 <= ordinal < len(eligible_slots):
			continue

		slot_index = eligible_slots[ordinal]
		slot = obj.material_slots[slot_index]
		original = slot.material
		if original is None or original.get("quaildef") != "eqgmaterialdef":
			continue

		preview = original.copy()
		preview.name = f"{original.name}__LAYER_S{variation:02d}_M{material_number:02d}"
		preview["quail_layer_preview"] = True
		preview["quail_layer_source"] = original.name

		err = eqg_apply(preview, overrides=layer_texture_overrides(layer))
		if err:
			bpy.data.materials.remove(preview)
			restore_eqg_material_variation(obj)
			return err

		saved = props.slots.add()
		saved.slot_index = slot_index
		saved.original_link = slot.link
		saved.original_material = original
		saved.preview_material = preview

		slot.link = 'OBJECT'
		slot.material = preview

	obj.data.update()
	return ""


def update_eqg_material_variation(self, context):
	if state.QUAIL_UPDATING:
		return

	obj = self.id_data
	if not obj or obj.type != 'MESH' or obj.get("quaildef") not in EQG_MODEL_QDEFS:
		return

	err = apply_eqg_material_variation(obj, self.material_index)
	if err:
		print(f"EQG material variation: {err}")

	from ...handlers import particle_renderer_main_model, refresh_particle_renderer
	for renderer in bpy.data.objects:
		if renderer.get("quaildef") != "eqgparticlerender":
			continue
		if particle_renderer_main_model(renderer) == obj:
			refresh_particle_renderer(renderer, context.scene if context else None)


class QuailEqgMaterialVariationProperties(bpy.types.PropertyGroup):
	material_index: IntProperty(name="Material", default=0, min=0, max=99, update=update_eqg_material_variation)
	slots: CollectionProperty(type=QuailEqgVariationSlot)


class VIEW3D_PT_quail_eqg_material_variations(bpy.types.Panel):
	bl_label = "Material Variations"
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'UI'
	bl_category = "Quail"

	@classmethod
	def poll(cls, context):
		obj = context.object
		return bool(obj and obj.type == 'MESH' and obj.get("quaildef") in EQG_MODEL_QDEFS and context.mode in {'OBJECT', 'EDIT_MESH'})

	def draw(self, context):
		row = self.layout.row(align=True)
		row.prop(context.object.quail_eqg_material_variation, "material_index")


def register():
	bpy.types.Object.quail_eqg_material_variation = PointerProperty(type=QuailEqgMaterialVariationProperties)


def unregister():
	for obj in bpy.data.objects:
		if hasattr(obj, "quail_eqg_material_variation"):
			restore_eqg_material_variation(obj)

	if hasattr(bpy.types.Object, "quail_eqg_material_variation"):
		del bpy.types.Object.quail_eqg_material_variation
