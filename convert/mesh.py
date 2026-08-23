# pyright: basic, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false

from enum import Enum

import bmesh
import bpy
from mathutils import Vector

from ..common import state
from ..common.mesh import (
	get_vertex_normal_nodegroup,
	merge_verts_by_attrs,
	split_vertices_by_uv,
)
from ..common.s3dobject import (
	apply_bounding_box_geo,
	apply_bounding_radius_geo,
)


class MeshConversionError(Exception):
	pass


class MeshFormat(str, Enum):
	BLENDER = "blender"
	DMSPRITEDEF2 = "dmspritedef2"
	DMSPRITEDEFINITION = "dmspritedefinition"
	EQGMODELDEF = "eqgmodeldef"
	EQGSKINNEDMODELDEF = "eqgskinnedmodeldef"
	EQGTERDEF = "eqgterdef"


EQG_FACE_ATTRIBUTES = (
	"quail_passable",
	"quail_collisionrequired",
	"quail_transparent",
	"quail_culled",
	"quail_degenerate",
)


def mesh_format(obj: bpy.types.Object) -> MeshFormat:
	if obj is None or obj.type != 'MESH':
		return MeshFormat.BLENDER

	try:
		return MeshFormat(obj.get("quaildef", "blender"))
	except ValueError:
		return MeshFormat.BLENDER


def _armature_for_mesh(obj: bpy.types.Object):
	for modifier in obj.modifiers:
		if modifier.type == 'ARMATURE' and modifier.object:
			return modifier.object

	if obj.parent and obj.parent.type == 'ARMATURE':
		return obj.parent

	return None


def _set_object_mode(obj: bpy.types.Object, context) -> None:
	view_layer = getattr(context, "view_layer", None)

	if view_layer is not None:
		view_layer.objects.active = obj

	if obj.mode != 'OBJECT':
		bpy.ops.object.mode_set(mode='OBJECT')


def _triangulate(mesh: bpy.types.Mesh) -> None:
	bm = bmesh.new()

	try:
		bm.from_mesh(mesh)
		bm.faces.ensure_lookup_table()
		bmesh.ops.triangulate(bm, faces=list(bm.faces))
		bm.to_mesh(mesh)
	finally:
		bm.free()

	mesh.update()


def _ensure_vertex_normals(mesh: bpy.types.Mesh) -> None:
	attribute = mesh.attributes.get("vertex_normals")

	if attribute is not None and (
		attribute.domain != 'POINT'
		or attribute.data_type != 'FLOAT_VECTOR'
	):
		mesh.attributes.remove(attribute)
		attribute = None

	if attribute is None:
		attribute = mesh.attributes.new(
			name="vertex_normals",
			type='FLOAT_VECTOR',
			domain='POINT',
		)

	mesh.calc_loop_triangles()

	for vertex in mesh.vertices:
		normal = vertex.normal.normalized()
		attribute.data[vertex.index].vector = (
			normal.x,
			normal.y,
			normal.z,
		)


def _ensure_point_vertex_colors(mesh: bpy.types.Mesh) -> bool:
	attribute = mesh.color_attributes.get("vertex_colors")

	if attribute is not None and attribute.domain == 'POINT':
		return True

	source = attribute

	if source is None:
		for candidate in mesh.color_attributes:
			if candidate.domain == 'CORNER':
				source = candidate
				break

	if source is None:
		return False

	# Copy loop colors before removing a CORNER attribute named
	# "vertex_colors"; accessing its data after removal is invalid.
	source_colors = [
		tuple(item.color)
		for item in source.data
	]

	if attribute is not None:
		mesh.color_attributes.remove(attribute)

	point_attribute = mesh.color_attributes.new(
		name="vertex_colors",
		type='FLOAT_COLOR',
		domain='POINT',
	)
	accumulated = [
		[0.0, 0.0, 0.0, 0.0]
		for _ in mesh.vertices
	]
	counts = [0 for _ in mesh.vertices]

	for polygon in mesh.polygons:
		for loop_index in polygon.loop_indices:
			vertex_index = mesh.loops[loop_index].vertex_index
			color = source_colors[loop_index]

			for component in range(4):
				accumulated[vertex_index][component] += color[component]

			counts[vertex_index] += 1

	for vertex_index, total in enumerate(accumulated):
		count = counts[vertex_index]

		if count == 0:
			continue

		point_attribute.data[vertex_index].color = tuple(
			component / count
			for component in total
		)

	if source != attribute:
		mesh.color_attributes.remove(source)

	return True


def _split_then_merge(obj: bpy.types.Object) -> None:
	"""Normalize point vertices using the existing common mesh helpers."""

	mesh = obj.data
	split_vertices_by_uv(obj)
	_ensure_point_vertex_colors(mesh)

	if not mesh.uv_layers.active:
		return

	if mesh.attributes.get("vertex_normals") is None:
		return

	bm = bmesh.new()

	try:
		bm.from_mesh(mesh)
		bm.verts.ensure_lookup_table()
		bm.edges.ensure_lookup_table()
		bm.faces.ensure_lookup_table()
		vcol_name = None

		if mesh.color_attributes.get("vertex_colors") is not None:
			vcol_name = "vertex_colors"

		merge_verts_by_attrs(
			bm,
			vcol_name=vcol_name,
			float_vec_name="vertex_normals",
		)
		bm.to_mesh(mesh)
	finally:
		bm.free()

	mesh.update()


def _ensure_int_face_attribute(
	mesh: bpy.types.Mesh,
	name: str,
	default: int,
) -> None:
	attribute = mesh.attributes.get(name)

	if attribute is not None and (
		attribute.domain != 'FACE'
		or attribute.data_type != 'INT'
	):
		mesh.attributes.remove(attribute)
		attribute = None

	if attribute is not None:
		return

	attribute = mesh.attributes.new(
		name=name,
		type='INT',
		domain='FACE',
	)

	for item in attribute.data:
		item.value = default


def _ensure_dmface_data(mesh: bpy.types.Mesh) -> None:
	attribute = mesh.color_attributes.get("DATA")

	if attribute is not None and attribute.domain != 'FACE':
		mesh.color_attributes.remove(attribute)
		attribute = None

	if attribute is not None:
		return

	attribute = mesh.color_attributes.new(
		name="DATA",
		type='BYTE_COLOR',
		domain='FACE',
	)

	for item in attribute.data:
		item.color = (0.0, 0.0, 0.0, 0.0)


def _ensure_eqg_face_attributes(mesh: bpy.types.Mesh) -> None:
	for name in EQG_FACE_ATTRIBUTES:
		_ensure_int_face_attribute(mesh, name, 0)


def _ensure_vertex_normal_modifier(obj: bpy.types.Object) -> None:
	modifier = obj.modifiers.get("VertexNormals")

	if modifier is None:
		modifier = obj.modifiers.new("VertexNormals", 'NODES')

	if modifier.type == 'NODES':
		modifier.node_group = get_vertex_normal_nodegroup()


def _mesh_bounds(mesh: bpy.types.Mesh):
	if not mesh.vertices:
		zero = Vector((0.0, 0.0, 0.0))
		return zero, zero, 0.0, 0.0

	minimum = Vector((
		min(vertex.co.x for vertex in mesh.vertices),
		min(vertex.co.y for vertex in mesh.vertices),
		min(vertex.co.z for vertex in mesh.vertices),
	))
	maximum = Vector((
		max(vertex.co.x for vertex in mesh.vertices),
		max(vertex.co.y for vertex in mesh.vertices),
		max(vertex.co.z for vertex in mesh.vertices),
	))
	center = (minimum + maximum) * 0.5
	radius = max(
		(vertex.co - center).length
		for vertex in mesh.vertices
	)
	extent = (maximum - minimum).length
	return minimum, maximum, radius, extent


def _fpscale(mesh: bpy.types.Mesh, extent: float) -> int:
	vertex_count = max(len(mesh.vertices), 1)
	density = vertex_count / max(extent, 0.0001)
	return int(round(max(
		5,
		min(13, 5 + ((density ** 0.75) * 0.25)),
	)))


def _apply_dmspritedef2(obj: bpy.types.Object) -> None:
	mesh = obj.data
	props = obj.quail_dmspritedef2
	minimum, maximum, radius, extent = _mesh_bounds(mesh)
	props.usecenteroffset = True
	props.materialpalette = None
	props.dmtrack = ""
	props.dmrgbtrack = ""
	props.polyhedron = None
	props.useparams2 = False
	props.params2_x = 0.0
	props.params2_y = 0.0
	props.params2_z = 0.0
	props.useboundingbox = False
	props.b_box_min_x = 0.0
	props.b_box_min_y = 0.0
	props.b_box_min_z = 0.0
	props.b_box_max_x = 0.0
	props.b_box_max_y = 0.0
	props.b_box_max_z = 0.0
	props.useboundingradius = True
	props.boundingradius = radius
	props.usevertexcoloralpha = (
		mesh.color_attributes.get("vertex_colors") is not None
	)
	props.spritedefpolyhedron = False
	fpscale = _fpscale(mesh, extent)
	props.fpscale_prev = fpscale
	props.fpscale = fpscale
	_ensure_int_face_attribute(mesh, "quail_passable", 0)
	_ensure_vertex_normal_modifier(obj)
	apply_bounding_radius_geo(
		parent_obj=obj,
		radius=radius,
		enabled=False,
	)
	apply_bounding_box_geo(
		obj,
		(
			(minimum.x, minimum.y, minimum.z),
			(maximum.x, maximum.y, maximum.z),
		),
		use_custom=False,
		visible=False,
	)


def _apply_dmspritedefinition(obj: bpy.types.Object) -> None:
	props = obj.quail_dmspritedefinition
	props.fragment1 = 0
	props.materialpalette = None
	props.fragment3 = 0
	props.hascenter = True
	props.hasparams1 = False
	props.params1_x = 0.0
	props.params1_y = 0.0
	props.params1_z = 0.0
	props.data8 = 0
	props.hasparams2 = False
	props.params2_x = 0.0
	props.params2_y = 0.0
	props.params2_z = 0.0
	_ensure_int_face_attribute(obj.data, "FLAG", 75)
	_ensure_dmface_data(obj.data)
	_ensure_vertex_normal_modifier(obj)


def _apply_eqgmodeldef(obj: bpy.types.Object) -> None:
	obj.quail_eqgmodeldef.version = '3'
	_ensure_eqg_face_attributes(obj.data)
	_ensure_vertex_normal_modifier(obj)


def _apply_eqgskinnedmodeldef(obj: bpy.types.Object) -> None:
	obj.quail_eqgskinnedmodeldef.version = '1'
	obj.quail_eqgskinnedmodeldef.mainpiece = True
	_ensure_eqg_face_attributes(obj.data)
	_ensure_vertex_normal_modifier(obj)


def _apply_eqgterdef(obj: bpy.types.Object) -> None:
	obj.quail_eqgterdef.version = '5'
	_ensure_eqg_face_attributes(obj.data)
	_ensure_vertex_normal_modifier(obj)


def _validate_target(obj: bpy.types.Object, target: MeshFormat) -> None:
	if obj is None:
		raise MeshConversionError("Object is None")

	if obj.type != 'MESH':
		raise MeshConversionError(f"{obj.name} is not a mesh")

	armature = _armature_for_mesh(obj)

	if target == MeshFormat.EQGSKINNEDMODELDEF and armature is None:
		raise MeshConversionError(
			"EQGSKINNEDMODELDEF requires an armature"
		)

	if target == MeshFormat.EQGTERDEF and armature is not None:
		raise MeshConversionError(
			"A mesh with an armature cannot become an EQGTERDEF"
		)


def convert_mesh(
	obj: bpy.types.Object,
	target_format: MeshFormat | str,
	context,
) -> str:
	try:
		target = MeshFormat(target_format)
	except ValueError:
		return f"Unsupported mesh target: {target_format}"

	if target == MeshFormat.BLENDER:
		return "BLENDER is not a conversion target"

	try:
		source_format = mesh_format(obj)

		if source_format == target:
			return ""

		_validate_target(obj, target)
		_set_object_mode(obj, context)
		previous_updating = state.QUAIL_UPDATING

		try:
			mesh = obj.data

			# Only generic Blender meshes require geometry normalization.
			# Decoded S3D and EQG meshes already have authoritative vertex,
			# UV, normal, color, material, and face-attribute organization.
			if source_format == MeshFormat.BLENDER:
				_triangulate(mesh)
				_ensure_vertex_normals(mesh)
				_split_then_merge(obj)

			obj["quaildef"] = target.value

			if target == MeshFormat.DMSPRITEDEF2:
				_apply_dmspritedef2(obj)

			elif target == MeshFormat.DMSPRITEDEFINITION:
				_apply_dmspritedefinition(obj)

			elif target == MeshFormat.EQGMODELDEF:
				_apply_eqgmodeldef(obj)

			elif target == MeshFormat.EQGSKINNEDMODELDEF:
				_apply_eqgskinnedmodeldef(obj)

			elif target == MeshFormat.EQGTERDEF:
				_apply_eqgterdef(obj)

			mesh.update()

		finally:
			state.QUAIL_UPDATING = previous_updating

		return ""

	except MeshConversionError as exception:
		return str(exception)

	except Exception as exception:
		return f"Mesh conversion failed: {exception}"


def convert_to_dmspritedef2(obj: bpy.types.Object, context) -> str:
	return convert_mesh(obj, MeshFormat.DMSPRITEDEF2, context)


def convert_to_dmspritedefinition(obj: bpy.types.Object, context) -> str:
	return convert_mesh(obj, MeshFormat.DMSPRITEDEFINITION, context)


def convert_to_eqgmodeldef(obj: bpy.types.Object, context) -> str:
	return convert_mesh(obj, MeshFormat.EQGMODELDEF, context)


def convert_to_eqgskinnedmodeldef(obj: bpy.types.Object, context) -> str:
	return convert_mesh(obj, MeshFormat.EQGSKINNEDMODELDEF, context)


def convert_to_eqgterdef(obj: bpy.types.Object, context) -> str:
	return convert_mesh(obj, MeshFormat.EQGTERDEF, context)

MESH_CONVERSION_TARGETS = (
	(
		MeshFormat.DMSPRITEDEF2,
		"DMSPRITEDEF2",
	),
	(
		MeshFormat.DMSPRITEDEFINITION,
		"DMSPRITEDEFINITION",
	),
	(
		MeshFormat.EQGMODELDEF,
		"EQGMODELDEF",
	),
	(
		MeshFormat.EQGSKINNEDMODELDEF,
		"EQGSKINNEDMODELDEF",
	),
	(
		MeshFormat.EQGTERDEF,
		"EQGTERDEF",
	),
)


def draw_mesh_conversion_in_transform(self, context):
	obj = context.object

	if not obj or obj.type != 'MESH':
		return

	current_format = mesh_format(obj)
	armature = _armature_for_mesh(obj)

	layout = self.layout
	box = layout.box()
	box.label(
		text="Convert Mesh",
		icon='MESH_DATA',
	)

	column = box.column(align=True)

	for target, label in MESH_CONVERSION_TARGETS:
		if target == current_format:
			continue

		row = column.row(align=True)

		if (
			target == MeshFormat.EQGSKINNEDMODELDEF
			and armature is None
		):
			row.enabled = False

		elif (
			target == MeshFormat.EQGTERDEF
			and armature is not None
		):
			row.enabled = False

		operator = row.operator(
			"object.convert_quail_mesh",
			text=f"Convert to {label}",
		)

		operator.target_format = target.value

class OBJECT_OT_convert_quail_mesh(bpy.types.Operator):
	bl_idname = "object.convert_quail_mesh"
	bl_label = "Convert Mesh"
	bl_options = {'REGISTER', 'UNDO'}

	target_format: bpy.props.EnumProperty(
		name="Target Format",
		items=(
			("dmspritedef2", "DMSPRITEDEF2", ""),
			(
				"dmspritedefinition",
				"DMSPRITEDEFINITION",
				"",
			),
			("eqgmodeldef", "EQGMODELDEF", ""),
			(
				"eqgskinnedmodeldef",
				"EQGSKINNEDMODELDEF",
				"",
			),
			("eqgterdef", "EQGTERDEF", ""),
		),
	)

	@classmethod
	def poll(cls, context):
		obj = context.object

		return (
			obj is not None
			and obj.type == 'MESH'
		)

	def execute(self, context):
		obj = context.object

		err = convert_mesh(
			obj,
			self.target_format,
			context,
		)

		if err:
			self.report({'ERROR'}, err)
			return {'CANCELLED'}

		target = MeshFormat(self.target_format)

		self.report(
			{'INFO'},
			f"Converted {obj.name} to {target.name}",
		)

		return {'FINISHED'}

def register():
	bpy.types.OBJECT_PT_transform.append(
		draw_mesh_conversion_in_transform
	)


def unregister():
	try:
		bpy.types.OBJECT_PT_transform.remove(
			draw_mesh_conversion_in_transform
		)
	except ValueError:
		pass
