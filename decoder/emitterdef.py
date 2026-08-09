# pyright: basic, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false

import bpy
import os
import math
from .context import Context
from ..wce.emitterdef import emitterdef

def create_emitter_material(ctx: Context, emitter: emitterdef):
	name = f"{emitter.name}_material"
	material = bpy.data.materials.get(name)
	if material:
		return material

	material = bpy.data.materials.new(name)
	material.use_nodes = True
	material.diffuse_color = (emitter.tintstart[0] / 255.0, emitter.tintstart[1] / 255.0, emitter.tintstart[2] / 255.0, emitter.maxalpha)

	material.surface_render_method = 'BLENDED'

	nodes = material.node_tree.nodes
	links = material.node_tree.links
	nodes.clear()

	output = nodes.new("ShaderNodeOutputMaterial")
	shader = nodes.new("ShaderNodeBsdfPrincipled")
	shader.inputs["Base Color"].default_value = material.diffuse_color
	shader.inputs["Emission Color"].default_value = material.diffuse_color
	shader.inputs["Emission Strength"].default_value = 1.0 if emitter.additiveblending else 0.0
	shader.inputs["Alpha"].default_value = emitter.maxalpha
	shader.inputs["Roughness"].default_value = 1.0

	texture_path = None
	if ctx.parser.assets_path:
		texture_path = os.path.join(ctx.parser.assets_path, emitter.texture)

	if texture_path:
		try:
			image = bpy.data.images.load(texture_path, check_existing=True)
			texture = nodes.new("ShaderNodeTexImage")
			uv = nodes.new("ShaderNodeAttribute")
			uv.attribute_name = "UVMap"
			texture.image = image
			links.new(uv.outputs["Vector"], texture.inputs["Vector"])
			links.new(texture.outputs["Color"], shader.inputs["Base Color"])
			links.new(texture.outputs["Color"], shader.inputs["Emission Color"])
			links.new(texture.outputs["Alpha"], shader.inputs["Alpha"])
		except Exception as e:
			print(f"Unable to load emitter texture {texture_path}: {e}")

	links.new(shader.outputs["BSDF"], output.inputs["Surface"])
	return material

def set_emitter_frame_range(obj, modifier, node_group):
	obj["start_frame"] = bpy.context.scene.frame_start
	obj["end_frame"] = bpy.context.scene.frame_end
	for socket in node_group.interface.items_tree:
		if socket.item_type != 'SOCKET' or socket.in_out != 'INPUT':
			continue
		if socket.name == "Start Frame":
			modifier[socket.identifier] = bpy.context.scene.frame_start
			driver = modifier.driver_add(f'["{socket.identifier}"]').driver
			variable = driver.variables.new()
			variable.name = "start_frame"
			variable.targets[0].id_type = 'SCENE'
			variable.targets[0].id = bpy.context.scene
			variable.targets[0].data_path = "frame_start"
			driver.expression = "start_frame"
		if socket.name == "End Frame":
			modifier[socket.identifier] = bpy.context.scene.frame_end
			driver = modifier.driver_add(f'["{socket.identifier}"]').driver
			variable = driver.variables.new()
			variable.name = "end_frame"
			variable.targets[0].id_type = 'SCENE'
			variable.targets[0].id = bpy.context.scene
			variable.targets[0].data_path = "frame_end"
			driver.expression = "end_frame"

def create_emitter_geometry_nodes(obj, emitter: emitterdef, material):
	name = f"{emitter.name}_geometry"
	node_group = bpy.data.node_groups.get(name)
	if node_group:
		modifier = obj.modifiers.new(name="EverQuest Particles", type='NODES')
		modifier.node_group = node_group
		set_emitter_frame_range(obj, modifier, node_group)
		return

	node_group = bpy.data.node_groups.new(name, "GeometryNodeTree")
	node_group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
	start_socket = node_group.interface.new_socket(name="Start Frame", in_out='INPUT', socket_type='NodeSocketInt')
	end_socket = node_group.interface.new_socket(name="End Frame", in_out='INPUT', socket_type='NodeSocketInt')
	start_socket.default_value = bpy.context.scene.frame_start
	end_socket.default_value = bpy.context.scene.frame_end

	nodes = node_group.nodes
	links = node_group.links

	group_input = nodes.new("NodeGroupInput")
	output = nodes.new("NodeGroupOutput")
	scene_time = nodes.new("GeometryNodeInputSceneTime")
	after_start = nodes.new("FunctionNodeCompare")
	before_end = nodes.new("FunctionNodeCompare")
	in_frame_range = nodes.new("FunctionNodeBooleanMath")
	frame_offset = nodes.new("ShaderNodeMath")
	frame_seconds = nodes.new("ShaderNodeMath")
	particle_age = nodes.new("ShaderNodeMath")
	age_squared = nodes.new("ShaderNodeMath")
	half_age_squared = nodes.new("ShaderNodeMath")
	animation_position = nodes.new("ShaderNodeMath")
	animation_frame = nodes.new("ShaderNodeMath")
	wrapped_frame = nodes.new("ShaderNodeMath")
	atlas_column = nodes.new("ShaderNodeMath")
	atlas_row_divide = nodes.new("ShaderNodeMath")
	atlas_row = nodes.new("ShaderNodeMath")
	column_offset = nodes.new("ShaderNodeMath")
	row_plus_one = nodes.new("ShaderNodeMath")
	row_fraction = nodes.new("ShaderNodeMath")
	row_offset = nodes.new("ShaderNodeMath")
	uv_scale_vector = nodes.new("ShaderNodeCombineXYZ")
	uv_offset_vector = nodes.new("ShaderNodeCombineXYZ")
	scale_uv = nodes.new("ShaderNodeVectorMath")
	offset_uv = nodes.new("ShaderNodeVectorMath")
	mesh_line = nodes.new("GeometryNodeMeshLine")
	set_position = nodes.new("GeometryNodeSetPosition")
	random_position = nodes.new("FunctionNodeRandomValue")
	random_velocity = nodes.new("FunctionNodeRandomValue")
	velocity_movement = nodes.new("ShaderNodeVectorMath")
	acceleration_vector = nodes.new("ShaderNodeCombineXYZ")
	acceleration_movement = nodes.new("ShaderNodeVectorMath")
	position_and_velocity = nodes.new("ShaderNodeVectorMath")
	particle_movement = nodes.new("ShaderNodeVectorMath")
	random_start_rotation = nodes.new("FunctionNodeRandomValue")
	random_spin_rate = nodes.new("FunctionNodeRandomValue")
	spin_movement = nodes.new("ShaderNodeMath")
	particle_rotation = nodes.new("ShaderNodeMath")
	rotation_vector = nodes.new("ShaderNodeCombineXYZ")
	active_camera = nodes.new("GeometryNodeInputActiveCamera")
	camera_info = nodes.new("GeometryNodeObjectInfo")
	position = nodes.new("GeometryNodeInputPosition")
	camera_direction = nodes.new("ShaderNodeVectorMath")
	billboard_rotation = nodes.new("FunctionNodeAlignEulerToVector")
	random_scale = nodes.new("FunctionNodeRandomValue")
	sprite = nodes.new("GeometryNodeMeshGrid")
	store_uv = nodes.new("GeometryNodeStoreNamedAttribute")
	transform_sprite = nodes.new("GeometryNodeTransform")
	set_material = nodes.new("GeometryNodeSetMaterial")
	instance = nodes.new("GeometryNodeInstanceOnPoints")

	after_start.data_type = 'FLOAT'
	after_start.operation = 'GREATER_EQUAL'
	before_end.data_type = 'FLOAT'
	before_end.operation = 'LESS_EQUAL'
	in_frame_range.operation = 'AND'
	frame_offset.operation = 'SUBTRACT'
	frame_seconds.operation = 'MULTIPLY'
	particle_age.operation = 'MODULO'
	age_squared.operation = 'MULTIPLY'
	half_age_squared.operation = 'MULTIPLY'
	animation_position.operation = 'MULTIPLY'
	animation_frame.operation = 'FLOOR'
	wrapped_frame.operation = 'MODULO'
	atlas_column.operation = 'MODULO'
	atlas_row_divide.operation = 'DIVIDE'
	atlas_row.operation = 'FLOOR'
	column_offset.operation = 'DIVIDE'
	row_plus_one.operation = 'ADD'
	row_fraction.operation = 'DIVIDE'
	row_offset.operation = 'SUBTRACT'
	scale_uv.operation = 'MULTIPLY'
	offset_uv.operation = 'ADD'
	velocity_movement.operation = 'SCALE'
	acceleration_movement.operation = 'SCALE'
	position_and_velocity.operation = 'ADD'
	particle_movement.operation = 'ADD'
	spin_movement.operation = 'MULTIPLY'
	particle_rotation.operation = 'ADD'
	camera_info.transform_space = 'RELATIVE'
	camera_direction.operation = 'SUBTRACT'
	billboard_rotation.axis = 'Y'
	billboard_rotation.pivot_axis = 'AUTO'

	animation_frames = max(1, emitter.animationframes)
	atlas_columns = max(1, math.ceil(math.sqrt(animation_frames)))
	atlas_rows = max(1, math.ceil(animation_frames / atlas_columns))
	fps = bpy.context.scene.render.fps / bpy.context.scene.render.fps_base
	frame_seconds.inputs[1].default_value = 1.0 / fps
	particle_age.inputs[1].default_value = max(emitter.particlelifespan, 0.0001)
	half_age_squared.inputs[1].default_value = 0.5
	animation_position.inputs[1].default_value = emitter.animationrate
	wrapped_frame.inputs[1].default_value = animation_frames
	atlas_column.inputs[1].default_value = atlas_columns
	atlas_row_divide.inputs[1].default_value = atlas_columns
	column_offset.inputs[1].default_value = atlas_columns
	row_plus_one.inputs[1].default_value = 1.0
	row_fraction.inputs[1].default_value = atlas_rows
	row_offset.inputs[0].default_value = 1.0
	uv_scale_vector.inputs["X"].default_value = 1.0 / atlas_columns
	uv_scale_vector.inputs["Y"].default_value = 1.0 / atlas_rows
	uv_scale_vector.inputs["Z"].default_value = 1.0

	count = max(1, emitter.particlesatcreation + emitter.particlesatinterval)
	mesh_line.inputs["Count"].default_value = count
	mesh_line.inputs["Start Location"].default_value = (0.0, 0.0, 0.0)
	mesh_line.inputs["Offset"].default_value = (0.0, 0.0, 0.0)

	radius_x = max(abs(emitter.shaperadius), 0.01)
	radius_y = max(abs(emitter.shaperadiusminor), radius_x)
	radius_z = max(abs(emitter.shapeheight), radius_x)

	random_position.data_type = 'FLOAT_VECTOR'
	random_position.inputs["Min"].default_value = (-radius_x, -radius_y, -radius_z)
	random_position.inputs["Max"].default_value = (radius_x, radius_y, radius_z)

	speed_min = tuple(min(emitter.speedmin[i], emitter.speedmax[i]) for i in range(3))
	speed_max = tuple(max(emitter.speedmin[i], emitter.speedmax[i]) for i in range(3))
	random_velocity.data_type = 'FLOAT_VECTOR'
	random_velocity.inputs["Min"].default_value = speed_min
	random_velocity.inputs["Max"].default_value = speed_max

	combined_acceleration = tuple(emitter.acceleration[i] + emitter.gravity[i] * emitter.scalargravity for i in range(3))
	acceleration_vector.inputs["X"].default_value = combined_acceleration[0]
	acceleration_vector.inputs["Y"].default_value = combined_acceleration[1]
	acceleration_vector.inputs["Z"].default_value = combined_acceleration[2]

	spin_min = min(emitter.particlespinrate, emitter.particlespinratemax)
	spin_max = max(emitter.particlespinrate, emitter.particlespinratemax)
	random_start_rotation.data_type = 'FLOAT'
	random_start_rotation.inputs["Min"].default_value = 0.0
	random_start_rotation.inputs["Max"].default_value = 2.0 * math.pi if emitter.randomrotation else 0.0
	random_spin_rate.data_type = 'FLOAT'
	random_spin_rate.inputs["Min"].default_value = math.radians(spin_min)
	random_spin_rate.inputs["Max"].default_value = math.radians(spin_max)

	width = max(emitter.particlewidthmin, 0.01)
	height = max(emitter.particleheightmin, 0.01)
	sprite.inputs["Size X"].default_value = width
	sprite.inputs["Size Y"].default_value = height
	sprite.inputs["Vertices X"].default_value = 2
	sprite.inputs["Vertices Y"].default_value = 2
	store_uv.data_type = 'FLOAT_VECTOR'
	store_uv.domain = 'CORNER'
	store_uv.inputs["Name"].default_value = "UVMap"

	transform_sprite.inputs["Rotation"].default_value = (-1.57079632679, 0.0, 0.0)

	random_scale.data_type = 'FLOAT_VECTOR'
	random_scale.inputs["Min"].default_value = (1.0, 1.0, 1.0)
	random_scale.inputs["Max"].default_value = (max(emitter.particlewidthmax / width, 1.0), max(emitter.particlewidthmax / width, 1.0), max(emitter.particleheightmax / height, 1.0))

	set_material.inputs["Material"].default_value = material

	links.new(scene_time.outputs["Frame"], after_start.inputs["A"])
	links.new(group_input.outputs["Start Frame"], after_start.inputs["B"])
	links.new(scene_time.outputs["Frame"], before_end.inputs["A"])
	links.new(group_input.outputs["End Frame"], before_end.inputs["B"])
	links.new(after_start.outputs["Result"], in_frame_range.inputs[0])
	links.new(before_end.outputs["Result"], in_frame_range.inputs[1])
	links.new(scene_time.outputs["Frame"], frame_offset.inputs[0])
	links.new(group_input.outputs["Start Frame"], frame_offset.inputs[1])
	links.new(frame_offset.outputs[0], frame_seconds.inputs[0])
	links.new(frame_seconds.outputs[0], particle_age.inputs[0])
	links.new(particle_age.outputs[0], age_squared.inputs[0])
	links.new(particle_age.outputs[0], age_squared.inputs[1])
	links.new(age_squared.outputs[0], half_age_squared.inputs[0])
	links.new(particle_age.outputs[0], animation_position.inputs[0])
	links.new(animation_position.outputs[0], animation_frame.inputs[0])
	links.new(animation_frame.outputs[0], wrapped_frame.inputs[0])
	links.new(wrapped_frame.outputs[0], atlas_column.inputs[0])
	links.new(wrapped_frame.outputs[0], atlas_row_divide.inputs[0])
	links.new(atlas_row_divide.outputs[0], atlas_row.inputs[0])
	links.new(atlas_column.outputs[0], column_offset.inputs[0])
	links.new(atlas_row.outputs[0], row_plus_one.inputs[0])
	links.new(row_plus_one.outputs[0], row_fraction.inputs[0])
	links.new(row_fraction.outputs[0], row_offset.inputs[1])
	links.new(column_offset.outputs[0], uv_offset_vector.inputs["X"])
	links.new(row_offset.outputs[0], uv_offset_vector.inputs["Y"])
	links.new(sprite.outputs["UV Map"], scale_uv.inputs[0])
	links.new(uv_scale_vector.outputs["Vector"], scale_uv.inputs[1])
	links.new(scale_uv.outputs["Vector"], offset_uv.inputs[0])
	links.new(uv_offset_vector.outputs["Vector"], offset_uv.inputs[1])
	links.new(random_velocity.outputs["Value"], velocity_movement.inputs["Vector"])
	links.new(particle_age.outputs[0], velocity_movement.inputs["Scale"])
	links.new(acceleration_vector.outputs["Vector"], acceleration_movement.inputs["Vector"])
	links.new(half_age_squared.outputs[0], acceleration_movement.inputs["Scale"])
	links.new(random_position.outputs["Value"], position_and_velocity.inputs[0])
	links.new(velocity_movement.outputs["Vector"], position_and_velocity.inputs[1])
	links.new(position_and_velocity.outputs["Vector"], particle_movement.inputs[0])
	links.new(acceleration_movement.outputs["Vector"], particle_movement.inputs[1])
	links.new(random_spin_rate.outputs["Value"], spin_movement.inputs[0])
	links.new(particle_age.outputs[0], spin_movement.inputs[1])
	links.new(random_start_rotation.outputs["Value"], particle_rotation.inputs[0])
	links.new(spin_movement.outputs[0], particle_rotation.inputs[1])
	links.new(particle_rotation.outputs[0], rotation_vector.inputs["Y"])
	links.new(active_camera.outputs["Active Camera"], camera_info.inputs["Object"])
	links.new(camera_info.outputs["Location"], camera_direction.inputs[0])
	links.new(position.outputs["Position"], camera_direction.inputs[1])
	links.new(rotation_vector.outputs["Vector"], billboard_rotation.inputs["Rotation"])
	links.new(camera_direction.outputs["Vector"], billboard_rotation.inputs["Vector"])
	links.new(mesh_line.outputs["Mesh"], set_position.inputs["Geometry"])
	links.new(particle_movement.outputs["Vector"], set_position.inputs["Offset"])
	links.new(sprite.outputs["Mesh"], store_uv.inputs["Geometry"])
	links.new(offset_uv.outputs["Vector"], store_uv.inputs["Value"])
	links.new(store_uv.outputs["Geometry"], transform_sprite.inputs["Geometry"])
	links.new(transform_sprite.outputs["Geometry"], set_material.inputs["Geometry"])
	links.new(set_material.outputs["Geometry"], instance.inputs["Instance"])
	links.new(set_position.outputs["Geometry"], instance.inputs["Points"])
	links.new(in_frame_range.outputs["Boolean"], instance.inputs["Selection"])
	links.new(billboard_rotation.outputs["Rotation"], instance.inputs["Rotation"])
	links.new(random_scale.outputs["Value"], instance.inputs["Scale"])
	links.new(instance.outputs["Instances"], output.inputs["Geometry"])

	modifier = obj.modifiers.new(name="EverQuest Particles", type='NODES')
	modifier.node_group = node_group
	set_emitter_frame_range(obj, modifier, node_group)

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
	obj["tag"] = emitter.tag
	obj["texture"] = emitter.texture
	obj["relativetobone"] = emitter.relativetobone
	obj["noocclusion"] = emitter.noocclusion
	obj["additiveblending"] = emitter.additiveblending
	obj["scalewithactor"] = emitter.scalewithactor
	obj["spriteorientation"] = emitter.spriteorientation
	obj["sticktoactor"] = emitter.sticktoactor
	obj["defaultlifespan"] = emitter.defaultlifespan
	obj["particlelifespan"] = emitter.particlelifespan
	obj["particlesatcreation"] = emitter.particlesatcreation
	obj["particlesatinterval"] = emitter.particlesatinterval
	obj["intervalspersecond"] = emitter.intervalspersecond
	obj["spawndelay"] = emitter.spawndelay
	obj["fadeintime"] = emitter.fadeintime
	obj["fadeouttime"] = emitter.fadeouttime
	obj["scaleintime"] = emitter.scaleintime
	obj["scaleouttime"] = emitter.scaleouttime
	obj["reductiondistance"] = emitter.reductiondistance
	obj["maxalpha"] = emitter.maxalpha
	obj["spawnshape"] = emitter.spawnshape
	obj["shaperadius"] = emitter.shaperadius
	obj["shaperadiusminor"] = emitter.shaperadiusminor
	obj["shapeheight"] = emitter.shapeheight
	obj["shapeoffset"] = emitter.shapeoffset
	obj["shapetilt"] = emitter.shapetilt
	obj["particlewidthmin"] = emitter.particlewidthmin
	obj["particlewidthmax"] = emitter.particlewidthmax
	obj["particleheightmin"] = emitter.particleheightmin
	obj["particleheightmax"] = emitter.particleheightmax
	obj["particlezbias"] = emitter.particlezbias
	obj["tintstart"] = emitter.tintstart
	obj["tintend"] = emitter.tintend
	obj["speedmin"] = emitter.speedmin
	obj["speedmax"] = emitter.speedmax
	obj["acceleration"] = emitter.acceleration
	obj["outwardspeedmin"] = emitter.outwardspeedmin
	obj["outwardspeedmax"] = emitter.outwardspeedmax
	obj["outwardspeedacceleration"] = emitter.outwardspeedacceleration
	obj["orbitalspeedmin"] = emitter.orbitalspeedmin
	obj["orbitalspeedmax"] = emitter.orbitalspeedmax
	obj["orbitalspeedacceleration"] = emitter.orbitalspeedacceleration
	obj["scalargravity"] = emitter.scalargravity
	obj["windspeed"] = emitter.windspeed
	obj["animationframes"] = emitter.animationframes
	obj["animationrate"] = emitter.animationrate
	obj["particlespinrate"] = emitter.particlespinrate
	obj["oldparticletype"] = emitter.oldparticletype
	obj["oldflags"] = emitter.oldflags
	obj["oldsize"] = emitter.oldsize
	obj["gravity"] = emitter.gravity
	obj["bbmin"] = emitter.bbmin
	obj["bbmax"] = emitter.bbmax
	obj["spawnscale"] = emitter.spawnscale
	obj["alpha"] = emitter.alpha
	obj["randomrotation"] = emitter.randomrotation
	obj["particleorientation"] = emitter.particleorientation
	obj["particlespinratemax"] = emitter.particlespinratemax
	obj["proportionalsizescaling"] = emitter.proportionalsizescaling
	obj["heightsquashtime"] = emitter.heightsquashtime
	obj["widthsquashtime"] = emitter.widthsquashtime
	obj["allowcenterpassthrough"] = emitter.allowcenterpassthrough
	obj["scaleemitterwithactor"] = emitter.scaleemitterwithactor

	obj.location = emitter.shapeoffset
	collection.objects.link(obj)

	material = create_emitter_material(ctx, emitter)
	obj.data.materials.append(material)
	create_emitter_geometry_nodes(obj, emitter, material)

	obj.hide_set(True)
	obj.hide_render = True
	return ""
