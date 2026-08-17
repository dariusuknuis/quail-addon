# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
import mathutils
from bpy.props import BoolProperty, EnumProperty, IntProperty, PointerProperty, StringProperty
from ...common import state


def renderer_object(properties):
	obj = properties.id_data
	if not obj or obj.get("quaildef") != "eqgparticlerender":
		return None
	return obj


def find_emitterdef(emitter_tag: int):
	tag = str(emitter_tag)
	for obj in bpy.data.objects:
		if obj.get("quaildef") != "emitterdef":
			continue
		if hasattr(obj, "quail_emitterdef") and obj.quail_emitterdef.tag == tag:
			return obj
	return None


def copy_emitter_modifier(source, target):
	existing = target.modifiers.get("EverQuest Particles")
	if existing:
		target.modifiers.remove(existing)

	source_modifier = source.modifiers.get("EverQuest Particles")
	if not source_modifier or source_modifier.type != 'NODES':
		return None

	modifier = target.modifiers.new(
		name="EverQuest Particles",
		type='NODES',
	)
	modifier.node_group = source_modifier.node_group
	for key in source_modifier.keys():
		try:
			modifier[key] = source_modifier[key]
		except (TypeError, ValueError):
			pass
	return modifier


def apply_render_emitter(obj):
	emitter = find_emitterdef(obj.quail_eqgparticlerender.render)
	if not emitter:
		existing = obj.modifiers.get("EverQuest Particles")
		if existing:
			obj.modifiers.remove(existing)
		obj.hide_viewport = True
		obj.hide_render = True
		print(
			f"Particle renderer {obj.name}: EMITTERDEF "
			f"{obj.quail_eqgparticlerender.render} not found"
		)
		return

	obj.data = emitter.data
	copy_emitter_modifier(emitter, obj)

	from ...handlers import refresh_particle_renderer
	refresh_particle_renderer(obj)


def renderer_model_tag(obj):
	for collection in obj.users_collection:
		suffix = "_PARTICLERENDERDEF"
		if collection.name.endswith(suffix):
			return collection.name[:-len(suffix)]
	return ""


def renderer_definition_version(obj):
	for collection in obj.users_collection:
		if collection.get("quaildef") != "eqgparticlerenderdef":
			continue
		return int(collection.quail_eqgparticlerenderdef.version)
	return 5


def find_particlepoint(obj, point_name: str):
	tag = renderer_model_tag(obj)
	if not tag:
		return None
	collection = bpy.data.collections.get(f"{tag}_PARTICLEPOINTDEF")
	if not collection:
		return None
	return collection.objects.get(point_name)


def apply_particlepoint_constraint(obj):
	props = obj.quail_eqgparticlerender
	particlepoint = find_particlepoint(obj, props.particlepoint.strip())
	if not particlepoint:
		print(
			f"Particle renderer {obj.name}: particle point "
			f"{props.particlepoint} not found"
		)
		return

	for constraint in list(obj.constraints):
		if constraint.type in {'CHILD_OF', 'COPY_LOCATION'}:
			obj.constraints.remove(constraint)

	obj.location = (0.0, 0.0, 0.0)
	if props.ground:
		constraint = obj.constraints.new(type='COPY_LOCATION')
		constraint.name = particlepoint.name
		constraint.target = particlepoint
		constraint.use_x = True
		constraint.use_y = True
		constraint.use_z = False
		constraint.use_offset = True
		constraint.owner_space = 'WORLD'
		constraint.target_space = 'WORLD'
		return

	constraint = obj.constraints.new(type='CHILD_OF')
	constraint.name = particlepoint.name
	constraint.target = particlepoint
	constraint.owner_space = 'WORLD'
	constraint.target_space = 'WORLD'
	constraint.inverse_matrix = mathutils.Matrix.Identity(4)


def update_render_emitter(self, context):
	if state.QUAIL_UPDATING:
		return
	obj = renderer_object(self)
	if obj:
		apply_render_emitter(obj)


def update_render_placement(self, context):
	if state.QUAIL_UPDATING:
		return
	obj = renderer_object(self)
	if obj:
		apply_particlepoint_constraint(obj)


def update_render_schedule(self, context):
	if state.QUAIL_UPDATING:
		return
	obj = renderer_object(self)
	if not obj:
		return
	from ...handlers import refresh_particle_renderer
	refresh_particle_renderer(obj, context.scene if context else None)


class QuailEqgParticleRenderDefProperties(bpy.types.PropertyGroup):
	version: EnumProperty(
		name="Version",
		items=[
			('1', "1", ""),
			('2', "2", "Adds Ground"),
			('3', "3", "Adds Play with Mat"),
			('4', "4", "Adds Sporadic"),
			('5', "5", "Adds Cold Emitter ID"),
		],
		default="5",
	)


class QuailEqgParticleRenderProperties(bpy.types.PropertyGroup):
	render: IntProperty(
		name="Emitter",
		description="Tag of the referenced EMITTERDEF",
		min=0,
		update=update_render_emitter,
	)
	particlepoint: StringProperty(
		name="Particle Point",
		description="EQGPARTICLEPOINTDEF point from which this emitter plays",
		update=update_render_placement,
	)
	particletype: EnumProperty(
		name="Particle Type",
		items=[
			('0', "Persistent", "Plays continuously"),
			('1', "Animation Based", "Triggered by an animation"),
		],
		description="Controls how the particles are triggered",
		default='1',
		update=update_render_schedule,
	)
	animnumber: IntProperty(
		name="Animation Number",
		description="EverQuest animation index used when Particle Type is 1",
		min=0,
		update=update_render_schedule,
	)
	animvariation: IntProperty(
		name="Animation Variation",
		min=0,
		update=update_render_schedule,
	)
	randomanim: BoolProperty(
		name="Random Animation",
		update=update_render_schedule,
	)
	starttime: IntProperty(
		name="Start Time",
		description="Delay from the animation start in milliseconds",
		min=0,
		update=update_render_schedule,
	)
	lifespan: IntProperty(
		name="Lifespan",
		description="Length of time that the renderer plays, in seconds",
		min=0,
		update=update_render_schedule,
	)
	ground: BoolProperty(
		name="Ground",
		description="Follow the particle point in X and Y while remaining at world Z zero",
		update=update_render_placement,
	)
	playwithmat: IntProperty(name="Play With Mat", default=-1, update=update_render_schedule)
	sporadic: BoolProperty(
		name="Sporadic",
		description="Play only occasionally when the associated animation is triggered",
		update=update_render_schedule,
	)
	coldemitterid: IntProperty(
		name="Cold Emitter",
		description="Alternative EMITTERDEF tag used in a cold zone",
		min=0,
	)


def draw_eqgparticlerenderdef_in_visibility(self, context):
	collection = context.collection
	if not collection or collection.get("quaildef") != "eqgparticlerenderdef":
		return

	layout = self.layout
	layout.separator()
	box = layout.box()
	box.label(text="EQGPARTICLERENDERDEF")
	box.prop(collection.quail_eqgparticlerenderdef, "version")


def draw_eqgparticlerender_in_transform(self, context):
	obj = context.object
	if not obj or obj.get("quaildef") != "eqgparticlerender":
		return

	props = obj.quail_eqgparticlerender
	box = self.layout.box()
	box.label(text="RENDER")

	box.prop(props, "render")
	box.prop(props, "particlepoint")
	box.prop(props, "particletype")

	animation_box = box.box()
	animation_box.label(text="Animation")
	animation_box.prop(props, "animnumber")
	animation_box.prop(props, "animvariation")
	animation_box.prop(props, "randomanim")
	animation_box.prop(props, "starttime")
	animation_box.prop(props, "lifespan")

	version = renderer_definition_version(obj)
	if version >= 2:
		options_box = box.box()
		options_box.label(text="Options")
		options_box.prop(props, "ground")
		if version >= 3:
			options_box.prop(props, "playwithmat")
		if version >= 4:
			options_box.prop(props, "sporadic")
		if version >= 5:
			options_box.prop(props, "coldemitterid")


def register():
	bpy.types.Collection.quail_eqgparticlerenderdef = PointerProperty(
		type=QuailEqgParticleRenderDefProperties
	)
	bpy.types.Object.quail_eqgparticlerender = PointerProperty(
		type=QuailEqgParticleRenderProperties
	)
	bpy.types.COLLECTION_PT_collection_flags.prepend(
		draw_eqgparticlerenderdef_in_visibility
	)
	bpy.types.OBJECT_PT_transform.prepend(
		draw_eqgparticlerender_in_transform
	)


def unregister():
	bpy.types.COLLECTION_PT_collection_flags.remove(
		draw_eqgparticlerenderdef_in_visibility
	)
	bpy.types.OBJECT_PT_transform.remove(
		draw_eqgparticlerender_in_transform
	)
	del bpy.types.Object.quail_eqgparticlerender
	del bpy.types.Collection.quail_eqgparticlerenderdef
