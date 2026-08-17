# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils

from ..common.armature import ensure_pivot, apply_pivot_shapes
from ..common.mesh import get_vertex_normal_nodegroup
from ..wce.eqganidef import eqganidef
from ..wce.eqgskinnedmodeldef import eqgskinnedmodeldef
from .eqganidef import decode_eqganidef
from .eqgmaterialdef import decode_eqgmaterialdef
from .context import Context
from ..ui.panel.eqgface import set_face_property


def _build_parent_map(model_bones) -> dict[str, str]:
	"""Build child-name -> parent-name from CHILDINDEX/NEXT chains."""

	parent_map: dict[str, str] = {}

	for parent_bone in model_bones:
		if parent_bone.children <= 0 or parent_bone.childindex < 0:
			continue

		child_index = parent_bone.childindex

		for _ in range(parent_bone.children):
			if child_index < 0 or child_index >= len(model_bones):
				break

			child = model_bones[child_index]
			parent_map[child.bone] = parent_bone.bone
			child_index = child.next

	return parent_map


def _create_armature(
	ctx: Context,
	modeldef: eqgskinnedmodeldef,
	location: mathutils.Vector,
) -> bpy.types.Object:
	"""Create the single skeleton shared by every MODEL piece."""

	ensure_pivot()

	armature_name = f"{modeldef.tag}_armature"
	armature = bpy.data.armatures.new(armature_name)
	armature_obj = bpy.data.objects.new(armature_name, armature)
	armature_obj["quaildef"] = "eqgmodarmature"
	ctx.collection.objects.link(armature_obj)
	armature_obj.location = location

	bpy.ops.object.select_all(action='DESELECT')
	bpy.context.view_layer.objects.active = armature_obj
	armature_obj.select_set(True)
	bpy.ops.object.mode_set(mode='EDIT')

	edit_bones = armature.edit_bones
	bones = {}
	bone_matrices = {}
	tail_length = 1.0

	for source_bone in modeldef.bones:
		bone = edit_bones.new(source_bone.bone)
		bone.head = (0.0, 0.0, 0.0)
		bone.tail = (0.0, tail_length, 0.0)
		bone.use_connect = False
		bones[source_bone.bone] = bone

	parent_map = _build_parent_map(modeldef.bones)
	ordered_bones = []
	added_bones = set()

	while len(ordered_bones) < len(modeldef.bones):
		added_this_pass = False

		for source_bone in modeldef.bones:
			name = source_bone.bone

			if name in added_bones:
				continue

			parent_name = parent_map.get(name)

			if parent_name is None or parent_name in added_bones:
				ordered_bones.append(source_bone)
				added_bones.add(name)
				added_this_pass = True

		if added_this_pass:
			continue

		# A cycle or invalid parent reference should not hang the importer.
		for source_bone in modeldef.bones:
			if source_bone.bone not in added_bones:
				ordered_bones.append(source_bone)
				added_bones.add(source_bone.bone)
		break

	for source_bone in ordered_bones:
		bone = bones[source_bone.bone]
		location_matrix = mathutils.Matrix.Translation(
			mathutils.Vector(source_bone.pivot)
		)
		rotation = mathutils.Quaternion((
			-source_bone.quaternion[3],
			source_bone.quaternion[0],
			source_bone.quaternion[1],
			source_bone.quaternion[2],
		))
		local_matrix = location_matrix @ rotation.to_matrix().to_4x4()

		parent_name = parent_map.get(source_bone.bone)
		parent_matrix = bone_matrices.get(
			parent_name,
			mathutils.Matrix.Identity(4),
		)
		world_matrix = parent_matrix @ local_matrix
		bone_matrices[source_bone.bone] = world_matrix
		bone.matrix = world_matrix
		bone.length = tail_length

	for child_name, parent_name in parent_map.items():
		child = bones.get(child_name)
		parent = bones.get(parent_name)

		if child is not None and parent is not None:
			child.parent = parent

	bpy.ops.object.mode_set(mode='OBJECT')
	apply_pivot_shapes(armature_obj)
	return armature_obj


def _decode_model_pose(
	ctx: Context,
	modeldef: eqgskinnedmodeldef,
) -> str:
	"""Create the model's one-frame POS animation through the ANI decoder."""

	action_tag = f"POS_{modeldef.tag}"
	existing_action = bpy.data.actions.get(action_tag)

	if (
		existing_action is not None
		and existing_action.get("quaildef") == "eqganidef"
	):
		return ""

	ani = eqganidef()
	ani.tag = action_tag
	ani.version = modeldef.version
	ani.strict = False
	ani.bones = []

	for source_bone in modeldef.bones:
		ani_bone = type(ani).bone()
		ani_bone.bone = source_bone.bone
		ani_bone.frames = []

		frame = type(ani_bone).frame()
		frame.milliseconds = 0
		frame.translation = tuple(source_bone.pivot)
		frame.rotation = tuple(source_bone.quaternion)
		frame.scale = tuple(source_bone.scale)

		ani_bone.frames.append(frame)
		ani.bones.append(ani_bone)

	return decode_eqganidef(ctx, ani)


def _add_skinning_data(
	obj: bpy.types.Object,
	modeldef: eqgskinnedmodeldef,
	model: eqgskinnedmodeldef.model,
) -> None:
	"""Create vertex groups and assign the weights stored on this piece."""

	for source_bone in modeldef.bones:
		obj.vertex_groups.new(name=source_bone.bone)

	for vertex_index, vertex in enumerate(model.vertices):
		for source_weight in vertex.weights:
			bone_index, value = source_weight.weight

			if bone_index < 0 or bone_index >= len(modeldef.bones):
				continue

			bone_name = modeldef.bones[bone_index].bone
			group = obj.vertex_groups.get(bone_name)

			if group is not None:
				group.add([vertex_index], value, 'ADD')


def decode_eqgskinnedmodeldef(
	ctx: Context,
	modeldef: eqgskinnedmodeldef,
	location: mathutils.Vector,
) -> str:
	"""Decode an EQG skinned model with one skeleton and multiple mesh pieces."""

	armature_obj = _create_armature(ctx, modeldef, location)

	err = _decode_model_pose(ctx, modeldef)

	if err:
		return f"decode POS_{modeldef.tag}: {err}"

	for model in modeldef.models:
		object_name = model.model or modeldef.tag

		if len(modeldef.models) > 1 and object_name == modeldef.tag:
			object_name = f"{modeldef.tag}_piece"

		mesh = bpy.data.meshes.new(object_name)
		obj = bpy.data.objects.new(object_name, mesh)
		ctx.collection.objects.link(obj)
		obj["quaildef"] = "eqgskinnedmodeldef"

		for material in modeldef.materials:
			properties = [
				(prop.property[0], prop.property[1], prop.property[2])
				for prop in material.properties
			]
			textures = [texture.texture for texture in material.animtextures]
			err = decode_eqgmaterialdef(
				ctx,
				mesh,
				modeldef.tag,
				material.materialtag,
				material.shadertag,
				properties,
				material.animsleep,
				textures,
				False,
			)

			if err:
				return f"decode {model.model}: decode {material.materialtag}: {err}"

		vertices = [mathutils.Vector(vertex.xyz) for vertex in model.vertices]
		faces = [face.triangle for face in model.faces]
		mesh.from_pydata(vertices, [], faces)
		mesh.update()

		normal_attribute = mesh.attributes.new(
			name="vertex_normals",
			type='FLOAT_VECTOR',
			domain='POINT',
		)

		for index, vertex in enumerate(model.vertices):
			normal_attribute.data[index].vector = vertex.normal

		color_attribute = mesh.color_attributes.new(
			name="vertex_colors",
			domain='POINT',
			type='FLOAT_COLOR',
		)

		for index, vertex in enumerate(model.vertices):
			color_attribute.data[index].color = (
				vertex.tint[0] / 255.0,
				vertex.tint[1] / 255.0,
				vertex.tint[2] / 255.0,
				vertex.tint[3] / 255.0,
			)

		uv_layer = mesh.uv_layers.new(name="UVMap")
		uv2_layer = mesh.uv_layers.new(name="UVMap2")

		for polygon in mesh.polygons:
			for corner, vertex_index in enumerate(polygon.vertices):
				source_vertex = model.vertices[vertex_index]
				loop_index = polygon.loop_indices[corner]
				uv_layer.data[loop_index].uv = source_vertex.uv
				uv2_layer.data[loop_index].uv = source_vertex.uv2

		for index, source_face in enumerate(model.faces):
			polygon = mesh.polygons[index]
			material_name = f"{modeldef.tag}_{source_face.material}"
			polygon.material_index = mesh.materials.find(material_name)

			if polygon.material_index == -1:
				return f"decode {model.model}: Material {material_name} not found"

			set_face_property(mesh, index, "passable", source_face.passable)
			set_face_property(
				mesh,
				index,
				"collisionrequired",
				source_face.collisionrequired,
			)
			set_face_property(mesh, index, "transparent", source_face.transparent)
			set_face_property(mesh, index, "culled", source_face.culled)
			set_face_property(mesh, index, "degenerate", source_face.degenerate)

		_add_skinning_data(obj, modeldef, model)

		armature_modifier = obj.modifiers.new("Armature", 'ARMATURE')
		armature_modifier.object = armature_obj
		obj.parent = armature_obj
		obj.location = (0.0, 0.0, 0.0)

		normal_modifier = obj.modifiers.new("VertexNormals", 'NODES')
		normal_modifier.node_group = get_vertex_normal_nodegroup()

		mesh.update()

	return ""
