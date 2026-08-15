# pyright: basic, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false

import bpy
from .context import Context
from ..wce.emitterdef import emitterdef
from ..common import state
from ..common.emitter import apply_emitter

def decode_emitterdef(ctx: Context, emitter: emitterdef) -> str:
	collection = ctx.collection.children.get("EMITTER_DEFS")
	if not collection:
		collection = bpy.data.collections.new("EMITTER_DEFS")
		ctx.collection.children.link(collection)

	mesh = bpy.data.meshes.new(f"{emitter.name}_mesh")
	mesh.from_pydata([(0.0, 0.0, 0.0)], [], [])
	mesh.update()

	obj = bpy.data.objects.new(emitter.name, mesh)
	obj["quaildef"] = "emitterdef"
	collection.objects.link(obj)

	props = obj.quail_emitterdef
	was_updating = state.QUAIL_UPDATING
	state.QUAIL_UPDATING = True
	try:
		props.tag = emitter.tag
		props.texture = emitter.texture
		props.relativetobone = bool(emitter.relativetobone)
		props.noocclusion = bool(emitter.noocclusion)
		props.additiveblending = bool(emitter.additiveblending)
		props.scalewithactor = bool(emitter.scalewithactor)
		props.spriteorientation = str(emitter.spriteorientation)
		props.sticktoactor = bool(emitter.sticktoactor)
		props.defaultlifespan = emitter.defaultlifespan
		props.particlelifespan = emitter.particlelifespan
		props.particlesatcreation = emitter.particlesatcreation
		props.particlesatinterval = emitter.particlesatinterval
		props.intervalspersecond = emitter.intervalspersecond
		props.spawndelay = emitter.spawndelay
		props.fadeintime = emitter.fadeintime
		props.fadeouttime = emitter.fadeouttime
		props.scaleintime = emitter.scaleintime
		props.scaleouttime = emitter.scaleouttime
		props.reductiondistance = emitter.reductiondistance
		props.maxalpha = emitter.maxalpha
		props.spawnshape = str(emitter.spawnshape)
		props.shaperadius = emitter.shaperadius
		props.shaperadiusminor = emitter.shaperadiusminor
		props.shapeheight = emitter.shapeheight
		props.shapeoffset = emitter.shapeoffset
		props.shapetilt = emitter.shapetilt
		props.particlewidthmin = emitter.particlewidthmin
		props.particlewidthmax = emitter.particlewidthmax
		props.particleheightmin = emitter.particleheightmin
		props.particleheightmax = emitter.particleheightmax
		props.particlezbias = emitter.particlezbias
		props.tintstart = tuple(value / 255.0 for value in emitter.tintstart)
		props.tintend = tuple(value / 255.0 for value in emitter.tintend)
		props.upwardspeedmin = emitter.upwardspeedmin
		props.upwardspeedmax = emitter.upwardspeedmax
		props.upwardacceleration = emitter.upwardacceleration
		props.forwardspeedmin = emitter.forwardspeedmin
		props.forwardspeedmax = emitter.forwardspeedmax
		props.forwardacceleration = emitter.forwardacceleration
		props.rightwardspeedmin = emitter.rightwardspeedmin
		props.rightwardspeedmax = emitter.rightwardspeedmax
		props.rightwardacceleration = emitter.rightwardacceleration
		props.outwardspeedmin = emitter.outwardspeedmin
		props.outwardspeedmax = emitter.outwardspeedmax
		props.outwardacceleration = emitter.outwardacceleration
		props.orbitalspeedmin = emitter.orbitalspeedmin
		props.orbitalspeedmax = emitter.orbitalspeedmax
		props.orbitalacceleration = emitter.orbitalacceleration
		props.gravity = emitter.gravity
		props.windspeed = emitter.windspeed
		props.animationframes = emitter.animationframes
		props.animationrate = emitter.animationrate
		props.particlespinrate = emitter.particlespinrate
		props.oldparticletype = emitter.oldparticletype
		props.oldflags = emitter.oldflags
		props.oldsize = emitter.oldsize
		props.oldgravity = emitter.oldgravity
		props.bbmin = emitter.bbmin
		props.bbmax = emitter.bbmax
		props.spawnscale = emitter.spawnscale
		props.alpha = emitter.alpha
		props.randomrotation = bool(emitter.randomrotation)
		props.particleorientation = str(emitter.particleorientation)
		props.particlespinratemax = emitter.particlespinratemax
		props.proportionalsizescaling = bool(emitter.proportionalsizescaling)
		props.heightsquashtime = emitter.heightsquashtime
		props.widthsquashtime = emitter.widthsquashtime
		props.allowcenterpassthrough = bool(emitter.allowcenterpassthrough)
		props.scaleemitterwithactor = bool(emitter.scaleemitterwithactor)
	finally:
		state.QUAIL_UPDATING = was_updating

	apply_emitter(obj, getattr(ctx.parser, "assets_path", None))

	obj.hide_set(True)
	obj.hide_render = True
	obj.hide_viewport = True
	return ""
