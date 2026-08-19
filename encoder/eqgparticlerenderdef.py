# pyright: basic, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false, reportOptionalSubscript=false

import bpy

from ..wce.eqgparticlerenderdef import eqgparticlerenderdef


def _definition_tag(collection: bpy.types.Collection) -> str:
	suffix = "_particlerenderdef"
	name = collection.name
	return name[:-len(suffix)] if name.casefold().endswith(suffix) else name


def encode_eqgparticlerenderdef(parser, collection: bpy.types.Collection) -> str:
	if collection.get("quaildef") != "eqgparticlerenderdef":
		return ""

	if not hasattr(collection, "quail_eqgparticlerenderdef"):
		return f"EQGPARTICLERENDERDEF collection {collection.name} has no definition properties"

	result = eqgparticlerenderdef()
	result.tag = _definition_tag(collection)
	result.version = int(collection.quail_eqgparticlerenderdef.version)
	result.renders = []
	particlepoint_collection = bpy.data.collections.get(f"{result.tag}_PARTICLEPOINTDEF")

	for obj in collection.objects:
		if obj.get("quaildef") != "eqgparticlerender":
			continue

		if not hasattr(obj, "quail_eqgparticlerender"):
			return f"Particle renderer {obj.name} has no renderer properties"

		props = obj.quail_eqgparticlerender
		particlepoint = props.particlepoint.strip()

		if not particlepoint:
			return f"Particle renderer {obj.name} has no particle point"

		if particlepoint_collection is None:
			return f"Particle-point collection {result.tag}_PARTICLEPOINTDEF not found"

		if particlepoint_collection.objects.get(particlepoint) is None:
			return f"Particle renderer {obj.name}: particle point {particlepoint} not found"

		render = eqgparticlerenderdef.render()
		render.render = int(props.render)
		render.particlepoint = particlepoint
		render.particletype = int(props.particletype)
		render.animnumber = int(props.animnumber)
		render.animvariation = int(props.animvariation)
		render.randomanim = 1 if props.randomanim else 0
		render.starttime = int(props.starttime)
		render.lifespan = int(props.lifespan)
		render.ground = 1 if props.ground else 0
		render.playwithmat = int(props.playwithmat)
		render.sporadic = 1 if props.sporadic else 0
		render.coldemitterid = int(props.coldemitterid)
		result.renders.append(render)

	if not hasattr(parser, "eqgparticlerenderdefs"):
		return "Parser has no eqgparticlerenderdefs collection"

	parser.eqgparticlerenderdefs[result.tag] = result
	return ""
