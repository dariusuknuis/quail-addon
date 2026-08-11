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
	shader.inputs["Emission Strength"].default_value = 1.0 if emitter.additiveblending else 0.0
	shader.inputs["Roughness"].default_value = 1.0
	tint_attribute = nodes.new("ShaderNodeAttribute")
	tint_attribute.attribute_name = "eq_particle_tint"
	tint_attribute.attribute_type = 'INSTANCER'
	alpha_attribute = nodes.new("ShaderNodeAttribute")
	alpha_attribute.attribute_name = "eq_particle_alpha"
	alpha_attribute.attribute_type = 'INSTANCER'
	base_uv_attribute = nodes.new("ShaderNodeAttribute")
	base_uv_attribute.attribute_name = "eq_base_uv"
	base_uv_attribute.attribute_type = 'GEOMETRY'
	atlas_offset_attribute = nodes.new("ShaderNodeAttribute")
	atlas_offset_attribute.attribute_name = "eq_atlas_offset"
	atlas_offset_attribute.attribute_type = 'INSTANCER'
	material_scale_uv = nodes.new("ShaderNodeVectorMath")
	material_scale_uv.operation = 'MULTIPLY'
	material_offset_uv = nodes.new("ShaderNodeVectorMath")
	material_offset_uv.operation = 'ADD'
	animation_frames = max(1, emitter.animationframes)
	atlas_columns = max(1, math.ceil(math.sqrt(animation_frames)))
	atlas_rows = max(1, math.ceil(animation_frames / atlas_columns))
	material_scale_uv.inputs[1].default_value = (
		1.0 / atlas_columns,
		1.0 / atlas_rows,
		1.0,
	)
	tinted_color = nodes.new("ShaderNodeMixRGB")
	tinted_color.blend_type = 'MULTIPLY'
	tinted_color.inputs[0].default_value = 1.0
	tinted_color.inputs[1].default_value = (1.0, 1.0, 1.0, 1.0)
	final_alpha = nodes.new("ShaderNodeMath")
	final_alpha.operation = 'MULTIPLY'
	final_alpha.inputs[0].default_value = 1.0
	links.new(tint_attribute.outputs["Color"], tinted_color.inputs[2])
	links.new(alpha_attribute.outputs["Fac"], final_alpha.inputs[1])
	links.new(base_uv_attribute.outputs["Vector"], material_scale_uv.inputs[0])
	links.new(material_scale_uv.outputs["Vector"], material_offset_uv.inputs[0])
	links.new(atlas_offset_attribute.outputs["Vector"], material_offset_uv.inputs[1])
	links.new(tinted_color.outputs["Color"], shader.inputs["Base Color"])
	links.new(tinted_color.outputs["Color"], shader.inputs["Emission Color"])
	links.new(final_alpha.outputs[0], shader.inputs["Alpha"])

	texture_path = None
	if ctx.parser.assets_path:
		texture_path = os.path.join(ctx.parser.assets_path, emitter.texture)

	if texture_path:
		try:
			image = bpy.data.images.load(texture_path, check_existing=True)
			texture = nodes.new("ShaderNodeTexImage")
			texture.image = image
			links.new(material_offset_uv.outputs["Vector"], texture.inputs["Vector"])
			links.new(texture.outputs["Color"], tinted_color.inputs[1])
			links.new(texture.outputs["Alpha"], final_alpha.inputs[0])
		except Exception as e:
			print(f"Unable to load emitter texture {texture_path}: {e}")

	links.new(shader.outputs["BSDF"], output.inputs["Surface"])
	return material

def set_emitter_frame_range(obj, modifier, node_group):
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
	range_frames = nodes.new("ShaderNodeMath")
	range_seconds = nodes.new("ShaderNodeMath")
	interval_time_available = nodes.new("ShaderNodeMath")
	positive_interval_time = nodes.new("ShaderNodeMath")
	interval_event_count = nodes.new("ShaderNodeMath")
	interval_event_floor = nodes.new("ShaderNodeMath")
	interval_particle_count = nodes.new("ShaderNodeMath")
	total_particle_count = nodes.new("ShaderNodeMath")
	is_creation_particle = nodes.new("FunctionNodeCompare")
	interval_particle_index = nodes.new("ShaderNodeMath")
	interval_event_divide = nodes.new("ShaderNodeMath")
	interval_event_floor_index = nodes.new("ShaderNodeMath")
	interval_event_number = nodes.new("ShaderNodeMath")
	interval_birth_offset = nodes.new("ShaderNodeMath")
	interval_birth_time = nodes.new("ShaderNodeMath")
	birth_time = nodes.new("GeometryNodeSwitch")
	particle_age = nodes.new("ShaderNodeMath")
	particle_started = nodes.new("FunctionNodeCompare")
	particle_alive = nodes.new("FunctionNodeCompare")
	particle_in_lifetime = nodes.new("FunctionNodeBooleanMath")
	particle_visible = nodes.new("FunctionNodeBooleanMath")
	normalized_age = nodes.new("ShaderNodeMath")
	tint_mix = nodes.new("ShaderNodeMixRGB")
	fade_in_factor = nodes.new("ShaderNodeMath")
	lifetime_remaining = nodes.new("ShaderNodeMath")
	fade_out_factor = nodes.new("ShaderNodeMath")
	fade_factor = nodes.new("ShaderNodeMath")
	particle_alpha = nodes.new("ShaderNodeMath")
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
	uv_offset_vector = nodes.new("ShaderNodeCombineXYZ")
	mesh_line = nodes.new("GeometryNodeMeshLine")
	particle_index = nodes.new("GeometryNodeInputIndex")
	set_position = nodes.new("GeometryNodeSetPosition")
	store_tint = nodes.new("GeometryNodeStoreNamedAttribute")
	store_alpha = nodes.new("GeometryNodeStoreNamedAttribute")
	store_atlas_offset = nodes.new("GeometryNodeStoreNamedAttribute")
	random_position = nodes.new("FunctionNodeRandomValue")
	random_velocity = nodes.new("FunctionNodeRandomValue")
	velocity_movement = nodes.new("ShaderNodeVectorMath")
	acceleration_vector = nodes.new("ShaderNodeCombineXYZ")
	acceleration_movement = nodes.new("ShaderNodeVectorMath")
	directional_movement = nodes.new("ShaderNodeVectorMath")
	random_outward_direction = nodes.new("FunctionNodeRandomValue")
	outward_direction = nodes.new("ShaderNodeVectorMath")
	random_outward_speed = nodes.new("FunctionNodeRandomValue")
	outward_velocity_distance = nodes.new("ShaderNodeMath")
	outward_acceleration_distance = nodes.new("ShaderNodeMath")
	outward_distance = nodes.new("ShaderNodeMath")
	outward_movement = nodes.new("ShaderNodeVectorMath")
	radial_position = nodes.new("ShaderNodeVectorMath")
	random_orbital_speed = nodes.new("FunctionNodeRandomValue")
	orbital_velocity_angle = nodes.new("ShaderNodeMath")
	orbital_acceleration_angle = nodes.new("ShaderNodeMath")
	orbital_angle = nodes.new("ShaderNodeMath")
	orbital_rotation = nodes.new("ShaderNodeVectorRotate")
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
	range_frames.operation = 'SUBTRACT'
	range_seconds.operation = 'MULTIPLY'
	interval_time_available.operation = 'SUBTRACT'
	positive_interval_time.operation = 'MAXIMUM'
	interval_event_count.operation = 'MULTIPLY'
	interval_event_floor.operation = 'FLOOR'
	interval_particle_count.operation = 'MULTIPLY'
	total_particle_count.operation = 'ADD'
	is_creation_particle.data_type = 'INT'
	is_creation_particle.operation = 'LESS_THAN'
	interval_particle_index.operation = 'SUBTRACT'
	interval_event_divide.operation = 'DIVIDE'
	interval_event_floor_index.operation = 'FLOOR'
	interval_event_number.operation = 'ADD'
	interval_birth_offset.operation = 'DIVIDE'
	interval_birth_time.operation = 'ADD'
	birth_time.input_type = 'FLOAT'
	particle_age.operation = 'SUBTRACT'
	particle_started.data_type = 'FLOAT'
	particle_started.operation = 'GREATER_EQUAL'
	particle_alive.data_type = 'FLOAT'
	particle_alive.operation = 'LESS_THAN'
	particle_in_lifetime.operation = 'AND'
	particle_visible.operation = 'AND'
	normalized_age.operation = 'DIVIDE'
	normalized_age.use_clamp = True
	tint_mix.blend_type = 'MIX'
	lifetime_remaining.operation = 'SUBTRACT'
	fade_factor.operation = 'MINIMUM'
	particle_alpha.operation = 'MULTIPLY'
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
	velocity_movement.operation = 'SCALE'
	acceleration_movement.operation = 'SCALE'
	directional_movement.operation = 'ADD'
	outward_direction.operation = 'NORMALIZE'
	outward_velocity_distance.operation = 'MULTIPLY'
	outward_acceleration_distance.operation = 'MULTIPLY'
	outward_distance.operation = 'ADD'
	outward_movement.operation = 'SCALE'
	radial_position.operation = 'ADD'
	orbital_velocity_angle.operation = 'MULTIPLY'
	orbital_acceleration_angle.operation = 'MULTIPLY'
	orbital_angle.operation = 'ADD'
	orbital_rotation.rotation_type = 'AXIS_ANGLE'
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
	particle_lifespan = max(emitter.particlelifespan, 0.0001)
	creation_count = max(0, emitter.particlesatcreation)
	particles_per_interval = max(0, emitter.particlesatinterval)
	interval_rate = max(0.0, emitter.intervalspersecond)
	safe_particles_per_interval = max(1, particles_per_interval)
	safe_interval_rate = max(0.0001, interval_rate)
	frame_seconds.inputs[1].default_value = 1.0 / fps
	range_seconds.inputs[1].default_value = 1.0 / fps
	interval_time_available.inputs[1].default_value = emitter.spawndelay
	positive_interval_time.inputs[1].default_value = 0.0
	interval_event_count.inputs[1].default_value = interval_rate
	interval_particle_count.inputs[1].default_value = particles_per_interval
	total_particle_count.inputs[1].default_value = creation_count
	is_creation_particle.inputs["B"].default_value = creation_count
	interval_particle_index.inputs[1].default_value = creation_count
	interval_event_divide.inputs[1].default_value = safe_particles_per_interval
	interval_event_number.inputs[1].default_value = 1.0
	interval_birth_offset.inputs[1].default_value = safe_interval_rate
	interval_birth_time.inputs[1].default_value = emitter.spawndelay
	birth_time.inputs["True"].default_value = emitter.spawndelay
	particle_started.inputs["B"].default_value = 0.0
	particle_alive.inputs["B"].default_value = particle_lifespan
	normalized_age.inputs[1].default_value = particle_lifespan
	tint_mix.inputs[1].default_value = (
		emitter.tintstart[0] / 255.0,
		emitter.tintstart[1] / 255.0,
		emitter.tintstart[2] / 255.0,
		1.0,
	)
	tint_mix.inputs[2].default_value = (
		emitter.tintend[0] / 255.0,
		emitter.tintend[1] / 255.0,
		emitter.tintend[2] / 255.0,
		1.0,
	)
	if emitter.fadeintime > 0.0:
		fade_in_factor.operation = 'DIVIDE'
		fade_in_factor.use_clamp = True
		fade_in_factor.inputs[1].default_value = emitter.fadeintime
	else:
		fade_in_factor.operation = 'ADD'
		fade_in_factor.inputs[0].default_value = 1.0
	if emitter.fadeouttime > 0.0:
		fade_out_factor.operation = 'DIVIDE'
		fade_out_factor.use_clamp = True
		fade_out_factor.inputs[1].default_value = emitter.fadeouttime
	else:
		fade_out_factor.operation = 'ADD'
		fade_out_factor.inputs[0].default_value = 1.0
	lifetime_remaining.inputs[0].default_value = particle_lifespan
	particle_alpha.inputs[1].default_value = emitter.maxalpha
	half_age_squared.inputs[1].default_value = 0.5
	animation_position.inputs[1].default_value = emitter.animationrate
	wrapped_frame.inputs[1].default_value = animation_frames
	atlas_column.inputs[1].default_value = atlas_columns
	atlas_row_divide.inputs[1].default_value = atlas_columns
	column_offset.inputs[1].default_value = atlas_columns
	row_plus_one.inputs[1].default_value = 1.0
	row_fraction.inputs[1].default_value = atlas_rows
	row_offset.inputs[0].default_value = 1.0

	mesh_line.inputs["Count"].default_value = max(1, creation_count)
	mesh_line.inputs["Start Location"].default_value = (0.0, 0.0, 0.0)
	mesh_line.inputs["Offset"].default_value = (0.0, 0.0, 0.0)

	radius_x = abs(emitter.shaperadius)
	radius_y = abs(emitter.shaperadiusminor) if emitter.shaperadiusminor != 0.0 else radius_x
	radius_z = abs(emitter.shapeheight) if emitter.shapeheight != 0.0 else radius_x
	if emitter.spawnshape == 0:
		radius_x = 0.0
		radius_y = 0.0
		radius_z = 0.0

	random_position.data_type = 'FLOAT_VECTOR'
	random_position.inputs["Min"].default_value = (-radius_x, -radius_y, -radius_z)
	random_position.inputs["Max"].default_value = (radius_x, radius_y, radius_z)

	wind_y = -abs(emitter.windspeed)
	speed_min = (
		min(emitter.rightwardspeedmin, emitter.rightwardspeedmax),
		min(emitter.forwardspeedmin, emitter.forwardspeedmax) + wind_y,
		min(emitter.upwardspeedmin, emitter.upwardspeedmax),
	)
	speed_max = (
		max(emitter.rightwardspeedmin, emitter.rightwardspeedmax),
		max(emitter.forwardspeedmin, emitter.forwardspeedmax) + wind_y,
		max(emitter.upwardspeedmin, emitter.upwardspeedmax),
	)
	random_velocity.data_type = 'FLOAT_VECTOR'
	random_velocity.inputs["Min"].default_value = speed_min
	random_velocity.inputs["Max"].default_value = speed_max

	acceleration_vector.inputs["X"].default_value = emitter.rightwardacceleration
	acceleration_vector.inputs["Y"].default_value = emitter.forwardacceleration
	acceleration_vector.inputs["Z"].default_value = emitter.upwardacceleration - emitter.gravity

	random_outward_direction.data_type = 'FLOAT_VECTOR'
	random_outward_direction.inputs["Min"].default_value = (-1.0, -1.0, -1.0)
	random_outward_direction.inputs["Max"].default_value = (1.0, 1.0, 1.0)
	random_outward_speed.data_type = 'FLOAT'
	random_outward_speed.inputs["Min"].default_value = min(emitter.outwardspeedmin, emitter.outwardspeedmax)
	random_outward_speed.inputs["Max"].default_value = max(emitter.outwardspeedmin, emitter.outwardspeedmax)
	outward_acceleration_distance.inputs[1].default_value = 0.5 * emitter.outwardacceleration

	random_orbital_speed.data_type = 'FLOAT'
	random_orbital_speed.inputs["Min"].default_value = math.radians(min(emitter.orbitalspeedmin, emitter.orbitalspeedmax))
	random_orbital_speed.inputs["Max"].default_value = math.radians(max(emitter.orbitalspeedmin, emitter.orbitalspeedmax))
	orbital_acceleration_angle.inputs[1].default_value = 0.5 * math.radians(emitter.orbitalacceleration)
	orbital_rotation.inputs["Axis"].default_value = (0.0, 0.0, 1.0)

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
	store_uv.inputs["Name"].default_value = "eq_base_uv"
	store_tint.data_type = 'FLOAT_COLOR'
	store_tint.domain = 'POINT'
	store_tint.inputs["Name"].default_value = "eq_particle_tint"
	store_alpha.data_type = 'FLOAT'
	store_alpha.domain = 'POINT'
	store_alpha.inputs["Name"].default_value = "eq_particle_alpha"
	store_atlas_offset.data_type = 'FLOAT_VECTOR'
	store_atlas_offset.domain = 'POINT'
	store_atlas_offset.inputs["Name"].default_value = "eq_atlas_offset"

	transform_sprite.inputs["Rotation"].default_value = (-1.57079632679, 0.0, 0.0)

	random_scale.data_type = 'FLOAT_VECTOR'
	random_scale.inputs["Min"].default_value = (1.0, 1.0, 1.0)
	random_scale.inputs["Max"].default_value = (max(emitter.particlewidthmax / width, 1.0), max(emitter.particlewidthmax / width, 1.0), max(emitter.particleheightmax / height, 1.0))

	# Every point now represents one real emission. Its point index is therefore
	# a stable, unique particle ID. Different fixed seeds keep the independently
	# randomized properties from being correlated.
	random_nodes = (
		random_position,
		random_velocity,
		random_outward_direction,
		random_outward_speed,
		random_orbital_speed,
		random_start_rotation,
		random_spin_rate,
		random_scale,
	)
	for seed_offset, random_node in enumerate(random_nodes, start=1):
		random_node.inputs["Seed"].default_value = seed_offset * 101

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

	# Build one point for every creation particle and every interval emission
	# that can occur within the selected Start Frame / End Frame range.
	links.new(group_input.outputs["End Frame"], range_frames.inputs[0])
	links.new(group_input.outputs["Start Frame"], range_frames.inputs[1])
	links.new(range_frames.outputs[0], range_seconds.inputs[0])
	links.new(range_seconds.outputs[0], interval_time_available.inputs[0])
	links.new(interval_time_available.outputs[0], positive_interval_time.inputs[0])
	links.new(positive_interval_time.outputs[0], interval_event_count.inputs[0])
	links.new(interval_event_count.outputs[0], interval_event_floor.inputs[0])
	links.new(interval_event_floor.outputs[0], interval_particle_count.inputs[0])
	links.new(interval_particle_count.outputs[0], total_particle_count.inputs[0])
	links.new(total_particle_count.outputs[0], mesh_line.inputs["Count"])

	# Creation particles are born at SPAWNDELAY. Remaining points are grouped
	# into PARTICLESATINTERVAL-sized batches, one batch every 1/rate seconds.
	links.new(particle_index.outputs["Index"], is_creation_particle.inputs["A"])
	links.new(particle_index.outputs["Index"], interval_particle_index.inputs[0])
	links.new(interval_particle_index.outputs[0], interval_event_divide.inputs[0])
	links.new(interval_event_divide.outputs[0], interval_event_floor_index.inputs[0])
	links.new(interval_event_floor_index.outputs[0], interval_event_number.inputs[0])
	links.new(interval_event_number.outputs[0], interval_birth_offset.inputs[0])
	links.new(interval_birth_offset.outputs[0], interval_birth_time.inputs[0])
	links.new(is_creation_particle.outputs["Result"], birth_time.inputs["Switch"])
	links.new(interval_birth_time.outputs[0], birth_time.inputs["False"])
	links.new(frame_seconds.outputs[0], particle_age.inputs[0])
	links.new(birth_time.outputs["Output"], particle_age.inputs[1])

	for random_node in random_nodes:
		links.new(particle_index.outputs["Index"], random_node.inputs["ID"])

	links.new(particle_age.outputs[0], particle_started.inputs["A"])
	links.new(particle_age.outputs[0], particle_alive.inputs["A"])
	links.new(particle_started.outputs["Result"], particle_in_lifetime.inputs[0])
	links.new(particle_alive.outputs["Result"], particle_in_lifetime.inputs[1])
	links.new(in_frame_range.outputs["Boolean"], particle_visible.inputs[0])
	links.new(particle_in_lifetime.outputs["Boolean"], particle_visible.inputs[1])
	links.new(particle_age.outputs[0], normalized_age.inputs[0])
	links.new(normalized_age.outputs[0], tint_mix.inputs[0])
	if emitter.fadeintime > 0.0:
		links.new(particle_age.outputs[0], fade_in_factor.inputs[0])
	links.new(particle_age.outputs[0], lifetime_remaining.inputs[1])
	if emitter.fadeouttime > 0.0:
		links.new(lifetime_remaining.outputs[0], fade_out_factor.inputs[0])
	links.new(fade_in_factor.outputs[0], fade_factor.inputs[0])
	links.new(fade_out_factor.outputs[0], fade_factor.inputs[1])
	links.new(fade_factor.outputs[0], particle_alpha.inputs[0])
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
	links.new(random_velocity.outputs["Value"], velocity_movement.inputs["Vector"])
	links.new(particle_age.outputs[0], velocity_movement.inputs["Scale"])
	links.new(acceleration_vector.outputs["Vector"], acceleration_movement.inputs["Vector"])
	links.new(half_age_squared.outputs[0], acceleration_movement.inputs["Scale"])
	links.new(velocity_movement.outputs["Vector"], directional_movement.inputs[0])
	links.new(acceleration_movement.outputs["Vector"], directional_movement.inputs[1])
	if emitter.spawnshape == 0:
		links.new(random_outward_direction.outputs["Value"], outward_direction.inputs[0])
	else:
		links.new(random_position.outputs["Value"], outward_direction.inputs[0])
	links.new(random_outward_speed.outputs["Value"], outward_velocity_distance.inputs[0])
	links.new(particle_age.outputs[0], outward_velocity_distance.inputs[1])
	links.new(age_squared.outputs[0], outward_acceleration_distance.inputs[0])
	links.new(outward_velocity_distance.outputs[0], outward_distance.inputs[0])
	links.new(outward_acceleration_distance.outputs[0], outward_distance.inputs[1])
	links.new(outward_direction.outputs["Vector"], outward_movement.inputs["Vector"])
	links.new(outward_distance.outputs[0], outward_movement.inputs["Scale"])
	links.new(random_position.outputs["Value"], radial_position.inputs[0])
	links.new(outward_movement.outputs["Vector"], radial_position.inputs[1])
	links.new(random_orbital_speed.outputs["Value"], orbital_velocity_angle.inputs[0])
	links.new(particle_age.outputs[0], orbital_velocity_angle.inputs[1])
	links.new(age_squared.outputs[0], orbital_acceleration_angle.inputs[0])
	links.new(orbital_velocity_angle.outputs[0], orbital_angle.inputs[0])
	links.new(orbital_acceleration_angle.outputs[0], orbital_angle.inputs[1])
	links.new(radial_position.outputs["Vector"], orbital_rotation.inputs["Vector"])
	links.new(orbital_angle.outputs[0], orbital_rotation.inputs["Angle"])
	links.new(orbital_rotation.outputs["Vector"], particle_movement.inputs[0])
	links.new(directional_movement.outputs["Vector"], particle_movement.inputs[1])
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
	links.new(set_position.outputs["Geometry"], store_tint.inputs["Geometry"])
	links.new(tint_mix.outputs["Color"], store_tint.inputs["Value"])
	links.new(store_tint.outputs["Geometry"], store_alpha.inputs["Geometry"])
	links.new(particle_alpha.outputs[0], store_alpha.inputs["Value"])
	links.new(store_alpha.outputs["Geometry"], store_atlas_offset.inputs["Geometry"])
	links.new(uv_offset_vector.outputs["Vector"], store_atlas_offset.inputs["Value"])
	links.new(sprite.outputs["Mesh"], store_uv.inputs["Geometry"])
	links.new(sprite.outputs["UV Map"], store_uv.inputs["Value"])
	links.new(store_uv.outputs["Geometry"], transform_sprite.inputs["Geometry"])
	links.new(transform_sprite.outputs["Geometry"], set_material.inputs["Geometry"])
	links.new(set_material.outputs["Geometry"], instance.inputs["Instance"])
	links.new(store_atlas_offset.outputs["Geometry"], instance.inputs["Points"])
	links.new(particle_visible.outputs["Boolean"], instance.inputs["Selection"])
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
	props = obj.quail_emitterdef
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

	obj.location = (emitter.shapeoffset[2], emitter.shapeoffset[1], emitter.shapeoffset[0])
	collection.objects.link(obj)

	material = create_emitter_material(ctx, emitter)
	obj.data.materials.append(material)
	create_emitter_geometry_nodes(obj, emitter, material)

	obj.hide_set(True)
	obj.hide_render = True
	return ""
