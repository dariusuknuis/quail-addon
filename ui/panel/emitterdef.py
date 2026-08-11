# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, FloatVectorProperty, IntProperty, PointerProperty, StringProperty


class QuailEmitterDefProperties(bpy.types.PropertyGroup):
	tag: StringProperty(name="Tag")
	texture: StringProperty(name="Texture")

	relativetobone: BoolProperty(name="Relative to Bone")
	noocclusion: BoolProperty(name="No Occlusion")
	additiveblending: BoolProperty(name="Additive Blending")
	scalewithactor: BoolProperty(name="Scale Particles with Actor")
	sticktoactor: BoolProperty(name="Stick to Actor")

	spriteorientation: EnumProperty(name="Sprite Orientation", items=[
		('0', "Camera Facing", "Sprite always faces the camera"),
		('1', "Upward", "Sprite is oriented upward in the world"),
		('2', "Flat", "Sprite is oriented flat in the world"),
	], default='0')

	defaultlifespan: FloatProperty(name="Default Lifespan", description="Emitter lifespan in seconds; negative overrides the spell duration")
	particlelifespan: FloatProperty(name="Particle Lifespan", min=0.0, unit='TIME')
	particlesatcreation: IntProperty(name="Particles at Creation", min=0)
	particlesatinterval: IntProperty(name="Particles at Interval", min=0)
	intervalspersecond: FloatProperty(name="Intervals per Second", min=0.0)
	spawndelay: FloatProperty(name="Spawn Delay", min=0.0, unit='TIME')
	fadeintime: FloatProperty(name="Fade In Time", min=0.0, unit='TIME')
	fadeouttime: FloatProperty(name="Fade Out Time", min=0.0, unit='TIME')
	scaleintime: FloatProperty(name="Scale In Time", min=0.0, unit='TIME')
	scaleouttime: FloatProperty(name="Scale Out Time", min=0.0, unit='TIME')
	reductiondistance: FloatProperty(name="Reduction Distance", min=0.0, subtype='DISTANCE')
	maxalpha: FloatProperty(name="Maximum Alpha", min=0.0, max=1.0, default=1.0)

	spawnshape: EnumProperty(name="Spawn Shape", items=[
		('0', "Point", "Point"),
		('1', "Ring (Uniform)", "Uniform ring"),
		('2', "Cylinder (Uniform)", "Uniform cylinder"),
		('3', "Cylinder (Random)", "Random cylinder"),
		('4', "Disk (Random)", "Random disk"),
		('5', "Sphere (Random)", "Random sphere"),
		('6', "Cube (Random)", "Random cube"),
		('7', "Cone (Random)", "Random cone"),
		('8', "Torus (Random)", "Random torus"),
		('9', "Ring (Random)", "Random ring"),
	], default='0')

	shaperadius: FloatProperty(name="Shape Radius", min=0.0, subtype='DISTANCE')
	shaperadiusminor: FloatProperty(name="Shape Minor Radius", min=0.0, subtype='DISTANCE')
	shapeheight: FloatProperty(name="Shape Height", min=0.0, subtype='DISTANCE')
	shapeoffset: FloatVectorProperty(name="Shape Offset", description="Upward, forward and rightward offset", size=3, subtype='XYZ')
	shapetilt: FloatVectorProperty(name="Shape Tilt", description="Forward and rightward tilt", size=2)

	particlewidthmin: FloatProperty(name="Particle Width Min", min=0.0)
	particlewidthmax: FloatProperty(name="Particle Width Max", min=0.0)
	particleheightmin: FloatProperty(name="Particle Height Min", min=0.0)
	particleheightmax: FloatProperty(name="Particle Height Max", min=0.0)
	particlezbias: FloatProperty(name="Particle Z Bias")

	tintstart: FloatVectorProperty(name="Tint Start", subtype='COLOR', size=3, min=0.0, max=1.0, default=(1.0, 1.0, 1.0))
	tintend: FloatVectorProperty(name="Tint End", subtype='COLOR', size=3, min=0.0, max=1.0, default=(1.0, 1.0, 1.0))

	upwardspeedmin: FloatProperty(name="Upward Speed Min")
	upwardspeedmax: FloatProperty(name="Upward Speed Max")
	upwardacceleration: FloatProperty(name="Upward Acceleration")
	forwardspeedmin: FloatProperty(name="Forward Speed Min")
	forwardspeedmax: FloatProperty(name="Forward Speed Max")
	forwardacceleration: FloatProperty(name="Forward Acceleration")
	rightwardspeedmin: FloatProperty(name="Rightward Speed Min")
	rightwardspeedmax: FloatProperty(name="Rightward Speed Max")
	rightwardacceleration: FloatProperty(name="Rightward Acceleration")
	outwardspeedmin: FloatProperty(name="Outward Speed Min")
	outwardspeedmax: FloatProperty(name="Outward Speed Max")
	outwardacceleration: FloatProperty(name="Outward Acceleration")
	orbitalspeedmin: FloatProperty(name="Orbital Speed Min")
	orbitalspeedmax: FloatProperty(name="Orbital Speed Max")
	orbitalacceleration: FloatProperty(name="Orbital Acceleration")
	gravity: FloatProperty(name="Gravity")
	windspeed: FloatProperty(name="Wind Speed", description="Applied in the negative Y direction by the current preview")

	animationframes: IntProperty(name="Animation Frames", description="Expected values are 1, 4 or 16", min=1, default=1)
	animationrate: FloatProperty(name="Animation Rate", description="Texture animation frames per second", min=0.0)
	particlespinrate: FloatProperty(name="Particle Spin Rate Min")
	particlespinratemax: FloatProperty(name="Particle Spin Rate Max")
	randomrotation: BoolProperty(name="Random Starting Rotation")

	particleorientation: EnumProperty(name="Particle Orientation", items=[
		('0', "Normal", "Normal orientation"),
		('1', "+X", "Positive X axis"),
		('2', "+Y", "Positive Y axis"),
		('3', "+Z", "Positive Z axis"),
		('4', "-X", "Negative X axis"),
		('5', "-Y", "Negative Y axis"),
		('6', "-Z", "Negative Z axis"),
	], default='0')

	proportionalsizescaling: BoolProperty(name="Proportional Size Scaling")
	heightsquashtime: FloatProperty(name="Height Squash Time", min=0.0, unit='TIME')
	widthsquashtime: FloatProperty(name="Width Squash Time", min=0.0, unit='TIME')
	allowcenterpassthrough: BoolProperty(name="Allow Center Pass Through")
	scaleemitterwithactor: BoolProperty(name="Scale Emitter with Actor")

	oldparticletype: IntProperty(name="Old Particle Type")
	oldflags: IntProperty(name="Old Flags", min=0)
	oldsize: IntProperty(name="Old Size", min=0)
	oldgravity: FloatVectorProperty(name="Old Gravity", size=3, subtype='XYZ')
	bbmin: FloatVectorProperty(name="Bounding Box Min", size=3, subtype='XYZ')
	bbmax: FloatVectorProperty(name="Bounding Box Max", size=3, subtype='XYZ')
	spawnscale: FloatProperty(name="Old Spawn Scale")
	alpha: FloatProperty(name="Old Alpha")


def draw_properties(box, props, names):
	for name in names:
		box.prop(props, name)


def draw_emitterdef_in_transform(self, context):
	obj = context.object
	if not obj or obj.get("quaildef") != "emitterdef":
		return

	props = obj.quail_emitterdef
	layout = self.layout

	box = layout.box()
	box.label(text="EMITTERDEF")
	draw_properties(box, props, ("tag", "texture"))

	box = layout.box()
	box.label(text="Attachment and Rendering")
	draw_properties(box, props, (
		"relativetobone", "noocclusion", "additiveblending", "scalewithactor",
		"spriteorientation", "sticktoactor", "reductiondistance", "particlezbias",
	))

	box = layout.box()
	box.label(text="Emission and Lifetime")
	draw_properties(box, props, (
		"defaultlifespan", "particlelifespan", "particlesatcreation",
		"particlesatinterval", "intervalspersecond", "spawndelay",
		"fadeintime", "fadeouttime", "scaleintime", "scaleouttime", "maxalpha",
	))

	box = layout.box()
	box.label(text="Spawn Shape")
	draw_properties(box, props, (
		"spawnshape", "shaperadius", "shaperadiusminor", "shapeheight",
		"shapeoffset", "shapetilt", "scaleemitterwithactor",
	))

	box = layout.box()
	box.label(text="Directional Motion")
	draw_properties(box, props, (
		"upwardspeedmin", "upwardspeedmax", "upwardacceleration",
		"forwardspeedmin", "forwardspeedmax", "forwardacceleration",
		"rightwardspeedmin", "rightwardspeedmax", "rightwardacceleration",
		"gravity", "windspeed",
	))

	box = layout.box()
	box.label(text="Radial and Orbital Motion")
	draw_properties(box, props, (
		"outwardspeedmin", "outwardspeedmax", "outwardacceleration",
		"orbitalspeedmin", "orbitalspeedmax", "orbitalacceleration",
	))

	box = layout.box()
	box.label(text="Appearance and Animation")
	draw_properties(box, props, (
		"tintstart", "tintend", "animationframes", "animationrate",
		"particlespinrate", "particlespinratemax", "randomrotation",
	))

	box = layout.box()
	box.label(text="Size and Orientation")
	draw_properties(box, props, (
		"particlewidthmin", "particlewidthmax", "particleheightmin",
		"particleheightmax", "particleorientation", "proportionalsizescaling",
		"heightsquashtime", "widthsquashtime", "allowcenterpassthrough",
	))

	box = layout.box()
	box.label(text="Legacy Values")
	draw_properties(box, props, (
		"oldparticletype", "oldflags", "oldsize", "oldgravity",
		"bbmin", "bbmax", "spawnscale", "alpha",
	))


def register():
	bpy.types.Object.quail_emitterdef = PointerProperty(type=QuailEmitterDefProperties)
	bpy.types.OBJECT_PT_transform.prepend(draw_emitterdef_in_transform)


def unregister():
	bpy.types.OBJECT_PT_transform.remove(draw_emitterdef_in_transform)
	del bpy.types.Object.quail_emitterdef
