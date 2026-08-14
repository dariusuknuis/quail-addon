# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import BoolProperty, EnumProperty, IntProperty, PointerProperty, StringProperty


class QuailEqgParticleRenderDefProperties(bpy.types.PropertyGroup):
	version: IntProperty(name="Version", min=0)


class QuailEqgParticleRenderProperties(bpy.types.PropertyGroup):
	render: IntProperty(
		name="Emitter",
		description="Tag of the referenced EMITTERDEF",
		min=0,
	)
	particlepoint: StringProperty(
		name="Particle Point",
		description="EQGPARTICLEPOINTDEF point from which this emitter plays",
	)
	particletype: EnumProperty(
		name="Particle Type",
		items=[
			('0', "Persistent", "Plays continuously"),
			('1', "Animation Based", "Triggered by an animation"),
		],
		description="Controls how the particles are triggered",
		default='1',
	)
	animnumber: IntProperty(
		name="Animation Number",
		description="EverQuest animation index used when Particle Type is 1",
		min=0,
	)
	animvariation: IntProperty(name="Animation Variation", min=0)
	randomanim: BoolProperty(name="Random Animation")
	starttime: IntProperty(
		name="Start Time",
		description="Delay from the animation start in milliseconds",
		min=0,
	)
	lifespan: IntProperty(
		name="Lifespan",
		description="Length of time that the renderer plays, in seconds",
		min=0,
	)
	ground: BoolProperty(
		name="Ground",
		description="Follow the particle point in X and Y while remaining at world Z zero",
	)
	playwithmat: IntProperty(name="Play With Mat", default=-1)
	sporadic: BoolProperty(
		name="Sporadic",
		description="Play only occasionally when the associated animation is triggered",
	)
	coldemitterid: IntProperty(
		name="Cold Emitter",
		description="Alternative EMITTERDEF tag used in a cold zone",
		min=0,
	)


class QUAIL_PT_eqgparticlerenderdef_collection(bpy.types.Panel):
	bl_label = "EQGPARTICLERENDERDEF"
	bl_idname = "QUAIL_PT_eqgparticlerenderdef_collection"
	bl_space_type = 'PROPERTIES'
	bl_region_type = 'WINDOW'
	bl_context = "collection"

	@classmethod
	def poll(cls, context):
		collection = context.collection
		return bool(
			collection
			and collection.get("quaildef") == "eqgparticlerenderdef"
		)

	def draw(self, context):
		collection = context.collection
		if not collection:
			return

		box = self.layout.box()
		box.label(text="EQGPARTICLERENDERDEF")
		box.prop(collection.quail_eqgparticlerenderdef, "version")


def draw_eqgparticlerender_in_transform(self, context):
	obj = context.object
	if not obj or obj.get("quaildef") != "eqgparticlerender":
		return

	props = obj.quail_eqgparticlerender
	box = self.layout.box()
	box.label(text=f"RENDER")

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

	options_box = box.box()
	options_box.label(text="Options")
	options_box.prop(props, "ground")
	options_box.prop(props, "playwithmat")
	options_box.prop(props, "sporadic")
	options_box.prop(props, "coldemitterid")


def register():
	bpy.types.Collection.quail_eqgparticlerenderdef = PointerProperty(
		type=QuailEqgParticleRenderDefProperties
	)
	bpy.types.Object.quail_eqgparticlerender = PointerProperty(
		type=QuailEqgParticleRenderProperties
	)
	bpy.types.OBJECT_PT_transform.prepend(
		draw_eqgparticlerender_in_transform
	)


def unregister():
	bpy.types.OBJECT_PT_transform.remove(
		draw_eqgparticlerender_in_transform
	)
	del bpy.types.Object.quail_eqgparticlerender
	del bpy.types.Collection.quail_eqgparticlerenderdef
