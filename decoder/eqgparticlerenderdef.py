# pyright: basic, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false

import bpy
import mathutils

from .context import Context
from ..common import state
from ..wce.eqgparticlerenderdef import eqgparticlerenderdef


def ensure_particlerender_collection(parent_collection, tag: str):
	collection_name = f"{tag}_PARTICLERENDERDEF"
	collection = parent_collection.children.get(collection_name)
	if collection:
		return collection

	collection = bpy.data.collections.get(collection_name)
	if not collection:
		collection = bpy.data.collections.new(collection_name)

	parent_collection.children.link(collection)
	return collection


def find_emitterdef(emitter_tag: int):
	tag = str(emitter_tag)
	for obj in bpy.data.objects:
		if obj.get("quaildef") != "emitterdef":
			continue
		if not hasattr(obj, "quail_emitterdef"):
			continue
		if obj.quail_emitterdef.tag == tag:
			return obj
	return None


def find_particlepoint(parent_collection, tag: str, point_name: str):
	collection = parent_collection.children.get(f"{tag}_PARTICLEPOINTDEF")
	if not collection:
		return None
	return collection.objects.get(point_name)


def copy_emitter_instance(source, name: str):
	# Construct a fresh object instead of copying the hidden EMITTERDEF object.
	# This keeps the renderer independent of the template collection's viewport
	# visibility while still sharing the lightweight mesh/material datablock and
	# the common EverQuest Emitter node group.
	obj = bpy.data.objects.new(name, source.data)

	source_modifier = source.modifiers.get("EverQuest Particles")
	if source_modifier and source_modifier.type == 'NODES':
		modifier = obj.modifiers.new(
			name="EverQuest Particles",
			type='NODES',
		)
		modifier.node_group = source_modifier.node_group
		modifier.show_viewport = source_modifier.show_viewport
		modifier.show_render = source_modifier.show_render

		# Geometry Nodes modifier inputs are stored as ID properties. Copy those
		# values so this renderer starts with the selected EMITTERDEF settings.
		for key in source_modifier.keys():
			try:
				modifier[key] = source_modifier[key]
			except (TypeError, ValueError):
				pass

	obj.hide_viewport = False
	obj.hide_render = False
	return obj


def create_emitter_placeholder(name: str):
	# Use the same one-point mesh representation as an EMITTERDEF so the
	# placeholder can later receive the emitter material and Geometry Nodes
	# modifier without replacing the renderer object or losing panel values.
	mesh = bpy.data.meshes.new(f"{name}_mesh")
	mesh.from_pydata([(0.0, 0.0, 0.0)], [], [])
	mesh.update()
	return bpy.data.objects.new(name, mesh)


def constrain_to_particlepoint(obj, particlepoint, ground: bool):
	if ground:
		constraint = obj.constraints.new(type='COPY_LOCATION')
		constraint.name = particlepoint.name
		constraint.target = particlepoint
		constraint.use_x = True
		constraint.use_y = True
		constraint.use_z = False
		constraint.use_offset = True
		constraint.owner_space = 'WORLD'
		constraint.target_space = 'WORLD'
		obj.location.z = 0.0
		return

	constraint = obj.constraints.new(type='CHILD_OF')
	constraint.name = particlepoint.name
	constraint.target = particlepoint
	constraint.owner_space = 'WORLD'
	constraint.target_space = 'WORLD'
	constraint.inverse_matrix = mathutils.Matrix.Identity(4)


def populate_render_properties(obj, render):
	props = obj.quail_eqgparticlerender
	was_updating = state.QUAIL_UPDATING
	state.QUAIL_UPDATING = True
	try:
		props.render = render.render
		props.particlepoint = render.particlepoint
		props.particletype = str(render.particletype)
		props.animnumber = render.animnumber
		props.animvariation = render.animvariation
		props.randomanim = bool(render.randomanim)
		props.starttime = render.starttime
		props.lifespan = render.lifespan
		props.ground = bool(render.ground)
		props.playwithmat = render.playwithmat
		props.sporadic = bool(render.sporadic)
		props.coldemitterid = render.coldemitterid
	finally:
		state.QUAIL_UPDATING = was_updating


def decode_eqgparticlerenderdef(
	ctx: Context,
	particlerenderdef: eqgparticlerenderdef,
) -> str:
	# Imported here to avoid coupling decoder module initialization to handler
	# registration during add-on startup.
	from ..handlers import initialize_particle_renderer

	# ------------------------------------------------
	# Find the corresponding armature and its owning collection
	# ------------------------------------------------
	armature_name = f"{particlerenderdef.tag}_armature"
	armature_obj = bpy.data.objects.get(armature_name)

	if armature_obj is None:
		return f"Armature {armature_name} not found"

	if armature_obj.type != 'ARMATURE':
		return f"Object {armature_name} is not an armature"

	if not armature_obj.users_collection:
		return f"Armature {armature_name} does not belong to a collection"

	parent_collection = armature_obj.users_collection[0]

	# Particle points are required for placement. Missing emitter definitions
	# are allowed and produce renderer placeholders instead.
	resolved = []
	for index, render in enumerate(particlerenderdef.renders):
		emitter = find_emitterdef(render.render)
		if emitter is None:
			print(
				f"Render {index}: EMITTERDEF {render.render} not found; "
				"creating placeholder"
			)

		particlepoint = find_particlepoint(
			parent_collection,
			particlerenderdef.tag,
			render.particlepoint,
		)
		if particlepoint is None:
			return (
				f"Render {index}: particle point "
				f"{render.particlepoint} not found"
			)

		resolved.append((render, emitter, particlepoint))

	# ------------------------------------------------
	# Create collection and populate its panel properties
	# ------------------------------------------------
	collection = ensure_particlerender_collection(
		parent_collection,
		particlerenderdef.tag,
	)
	collection["quaildef"] = "eqgparticlerenderdef"

	collection_props = collection.quail_eqgparticlerenderdef
	was_updating = state.QUAIL_UPDATING
	state.QUAIL_UPDATING = True
	try:
		collection_props.version = str(particlerenderdef.version)
	finally:
		state.QUAIL_UPDATING = was_updating

	# ------------------------------------------------
	# Create one independently schedulable emitter instance per RENDER
	# ------------------------------------------------
	for index, (render, emitter, particlepoint) in enumerate(resolved):
		name = f"RENDER_{index:03d}"
		if emitter is None:
			obj = create_emitter_placeholder(name)
		else:
			obj = copy_emitter_instance(emitter, name)
		obj["quaildef"] = "eqgparticlerender"
		collection.objects.link(obj)
		obj.hide_set(False)
		populate_render_properties(obj, render)
		constrain_to_particlepoint(obj, particlepoint, bool(render.ground))
		initialize_particle_renderer(obj)

	return ""
