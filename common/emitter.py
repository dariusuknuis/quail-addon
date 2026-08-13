# pyright: basic, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false

import bpy
import os
import math

EMITTER_NODE_GROUP_NAME = "EverQuest Emitter"

def add_emitter_input(node_group, name, socket_type, default=None):
	socket = node_group.interface.new_socket(name=name, in_out='INPUT', socket_type=socket_type)
	if default is not None:
		socket.default_value = default
	return socket

def set_modifier_input(modifier, node_group, name, value):
	for socket in node_group.interface.items_tree:
		if socket.item_type == 'SOCKET' and socket.in_out == 'INPUT' and socket.name == name:
			modifier[socket.identifier] = value
			return
	raise KeyError(f"Geometry Nodes input not found: {name}")

def set_emitter_modifier_inputs(obj, modifier, node_group, material):
	props = obj.quail_emitterdef
	animation_frames = max(1, props.animationframes)
	atlas_columns = max(1, math.ceil(math.sqrt(animation_frames)))
	atlas_rows = max(1, math.ceil(animation_frames / atlas_columns))
	particle_lifespan = max(props.particlelifespan, 0.0001)
	creation_count = max(0, props.particlesatcreation)
	particles_per_interval = max(0, props.particlesatinterval)
	interval_rate = max(0.0, props.intervalspersecond)
	radius_x = abs(props.shaperadius)
	radius_y = abs(props.shaperadiusminor) if props.shaperadiusminor != 0.0 else radius_x
	radius_z = abs(props.shapeheight) if props.shapeheight != 0.0 else radius_x
	if props.spawnshape == '0':
		radius_x = radius_y = radius_z = 0.0
	wind_y = -abs(props.windspeed)
	width = max(props.particlewidthmin, 0.01)
	height = max(props.particleheightmin, 0.01)
	values = {
		"Material": material,
		"Particle Lifespan": particle_lifespan,
		"Creation Count": creation_count,
		"Particles Per Interval": particles_per_interval,
		"Interval Rate": interval_rate,
		"Safe Particles Per Interval": max(1, particles_per_interval),
		"Safe Interval Rate": max(0.0001, interval_rate),
		"Spawn Delay": props.spawndelay,
		"Tint Start": (*props.tintstart, 1.0),
		"Tint End": (*props.tintend, 1.0),
		"Use Fade In": props.fadeintime > 0.0,
		"Fade In Time": max(props.fadeintime, 0.0001),
		"Use Fade Out": props.fadeouttime > 0.0,
		"Fade Out Time": max(props.fadeouttime, 0.0001),
		"Use Scale In": props.scaleintime > 0.0,
		"Scale In Time": max(props.scaleintime, 0.0001),
		"Use Scale Out": props.scaleouttime > 0.0,
		"Scale Out Time": max(props.scaleouttime, 0.0001),
		"Use Width Squash": props.widthsquashtime > 0.0,
		"Width Squash Time": max(props.widthsquashtime, 0.0001),
		"Use Height Squash": props.heightsquashtime > 0.0,
		"Height Squash Time": max(props.heightsquashtime, 0.0001),
		"Max Alpha": props.maxalpha,
		"Animation Rate": props.animationrate,
		"Animation Frames": animation_frames,
		"Atlas Columns": atlas_columns,
		"Atlas Rows": atlas_rows,
		"Spawn Shape": int(props.spawnshape),
		"Shape Radius": radius_x,
		"Shape Radius Minor": radius_y,
		"Shape Height": radius_z,
		"Spawn Min": (-radius_x, -radius_y, -radius_z),
		"Spawn Max": (radius_x, radius_y, radius_z),
		"Allow Center Pass Through": props.allowcenterpassthrough,
		"Velocity Min": (min(props.rightwardspeedmin, props.rightwardspeedmax), min(props.forwardspeedmin, props.forwardspeedmax) + wind_y, min(props.upwardspeedmin, props.upwardspeedmax)),
		"Velocity Max": (max(props.rightwardspeedmin, props.rightwardspeedmax), max(props.forwardspeedmin, props.forwardspeedmax) + wind_y, max(props.upwardspeedmin, props.upwardspeedmax)),
		"Acceleration": (props.rightwardacceleration, props.forwardacceleration, props.upwardacceleration - props.gravity),
		"Outward Speed Min": min(props.outwardspeedmin, props.outwardspeedmax),
		"Outward Speed Max": max(props.outwardspeedmin, props.outwardspeedmax),
		"Half Outward Acceleration": 0.5 * props.outwardacceleration,
		"Random Outward Direction": props.spawnshape == '0',
		"Orbital Speed Min": math.radians(min(props.orbitalspeedmin, props.orbitalspeedmax)),
		"Orbital Speed Max": math.radians(max(props.orbitalspeedmin, props.orbitalspeedmax)),
		"Half Orbital Acceleration": 0.5 * math.radians(props.orbitalacceleration),
		"Random Start Rotation Max": 2.0 * math.pi if props.randomrotation else 0.0,
		"Spin Rate Min": math.radians(min(props.particlespinrate, props.particlespinratemax)),
		"Spin Rate Max": math.radians(max(props.particlespinrate, props.particlespinratemax)),
		"Particle Width": width,
		"Particle Height": height,
		"Random Scale Max": (max(props.particlewidthmax / width, 1.0), max(props.particleheightmax / height, 1.0), 1.0),
	}
	for name, value in values.items():
		set_modifier_input(modifier, node_group, name, value)

def find_emitter_texture(texture_name, assets_path=None):
	if not texture_name:
		return None
	image = bpy.data.images.get(texture_name)
	if image:
		return image
	texture_basename = os.path.basename(texture_name).lower()
	for candidate in bpy.data.images:
		if os.path.basename(candidate.filepath).lower() == texture_basename or candidate.name.lower() == texture_basename:
			return candidate
	paths = []
	if assets_path:
		paths.append(os.path.join(assets_path, texture_name))
	paths.append(bpy.path.abspath(os.path.join("//assets", texture_name)))
	for texture_path in paths:
		if os.path.isfile(texture_path):
			try:
				return bpy.data.images.load(texture_path, check_existing=True)
			except Exception as e:
				print(f"Unable to load emitter texture {texture_path}: {e}")
	return None

def create_emitter_material(obj, assets_path=None):
	props = obj.quail_emitterdef
	name = f"{obj.name}_material"
	material = bpy.data.materials.get(name)
	if not material:
		material = bpy.data.materials.new(name)
	material.use_nodes = True
	material.diffuse_color = (*props.tintstart, props.maxalpha)

	material.surface_render_method = 'BLENDED'

	nodes = material.node_tree.nodes
	links = material.node_tree.links
	nodes.clear()

	output = nodes.new("ShaderNodeOutputMaterial")
	tint_attribute = nodes.new("ShaderNodeAttribute")
	tint_attribute.attribute_name = "eq_particle_tint"
	tint_attribute.attribute_type = 'INSTANCER'
	alpha_attribute = nodes.new("ShaderNodeAttribute")
	alpha_attribute.attribute_name = "eq_particle_alpha"
	alpha_attribute.attribute_type = 'INSTANCER'
	base_uv_attribute = nodes.new("ShaderNodeAttribute")
	base_uv_attribute.attribute_name = "eq_base_uv"
	base_uv_attribute.attribute_type = 'GEOMETRY'
	separate_uv = nodes.new("ShaderNodeSeparateXYZ")
	flip_uv_y = nodes.new("ShaderNodeMath")
	flip_uv_y.operation = 'SUBTRACT'
	flip_uv_y.inputs[0].default_value = 1.0
	combine_uv = nodes.new("ShaderNodeCombineXYZ")
	atlas_offset_attribute = nodes.new("ShaderNodeAttribute")
	atlas_offset_attribute.attribute_name = "eq_atlas_offset"
	atlas_offset_attribute.attribute_type = 'INSTANCER'
	material_scale_uv = nodes.new("ShaderNodeVectorMath")
	material_scale_uv.operation = 'MULTIPLY'
	material_offset_uv = nodes.new("ShaderNodeVectorMath")
	material_offset_uv.operation = 'ADD'
	animation_frames = max(1, props.animationframes)
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
	links.new(base_uv_attribute.outputs["Vector"], separate_uv.inputs["Vector"])
	links.new(separate_uv.outputs["X"], combine_uv.inputs["X"])
	links.new(separate_uv.outputs["Y"], flip_uv_y.inputs[1])
	links.new(flip_uv_y.outputs[0], combine_uv.inputs["Y"])
	links.new(separate_uv.outputs["Z"], combine_uv.inputs["Z"])
	links.new(combine_uv.outputs["Vector"], material_scale_uv.inputs[0])
	links.new(material_scale_uv.outputs["Vector"], material_offset_uv.inputs[0])
	links.new(atlas_offset_attribute.outputs["Vector"], material_offset_uv.inputs[1])
	image = find_emitter_texture(props.texture, assets_path)
	if image:
		texture = nodes.new("ShaderNodeTexImage")
		texture.image = image
		links.new(material_offset_uv.outputs["Vector"], texture.inputs["Vector"])
		links.new(texture.outputs["Color"], tinted_color.inputs[1])
		links.new(texture.outputs["Alpha"], final_alpha.inputs[0])

	if props.additiveblending:
		# EverQuest additive particles do not alpha-composite their dark texels
		# over the scene. Keep the surface transparent and add only the tinted,
		# particle-alpha-scaled texture color. Overlapping bright particles can
		# therefore accumulate without darkening or obscuring the background.
		emission_color = nodes.new("ShaderNodeVectorMath")
		emission_color.operation = 'SCALE'
		emission = nodes.new("ShaderNodeEmission")
		transparent = nodes.new("ShaderNodeBsdfTransparent")
		add_shader = nodes.new("ShaderNodeAddShader")
		links.new(tinted_color.outputs["Color"], emission_color.inputs["Vector"])
		links.new(final_alpha.outputs[0], emission_color.inputs["Scale"])
		links.new(emission_color.outputs["Vector"], emission.inputs["Color"])
		emission.inputs["Strength"].default_value = 1.0
		links.new(transparent.outputs["BSDF"], add_shader.inputs[0])
		links.new(emission.outputs["Emission"], add_shader.inputs[1])
		links.new(add_shader.outputs["Shader"], output.inputs["Surface"])
	else:
		shader = nodes.new("ShaderNodeBsdfPrincipled")
		shader.inputs["Roughness"].default_value = 1.0
		links.new(tinted_color.outputs["Color"], shader.inputs["Base Color"])
		links.new(final_alpha.outputs[0], shader.inputs["Alpha"])
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

def build_spawn_shape_field(nodes, links, group_input, particle_index):
	"""Build the ten EQ emitter spawn shapes and return (position, random_nodes)."""
	random_nodes = []

	def math_node(operation, a=None, b=None, value_a=None, value_b=None):
		node = nodes.new("ShaderNodeMath")
		node.operation = operation
		if a is not None:
			links.new(a, node.inputs[0])
		elif value_a is not None:
			node.inputs[0].default_value = value_a
		if b is not None:
			links.new(b, node.inputs[1])
		elif value_b is not None:
			node.inputs[1].default_value = value_b
		return node.outputs[0]

	def random_float(minimum=0.0, maximum=1.0):
		node = nodes.new("FunctionNodeRandomValue")
		node.data_type = 'FLOAT'
		node.inputs["Min"].default_value = minimum
		node.inputs["Max"].default_value = maximum
		random_nodes.append(node)
		return node.outputs["Value"]

	def combine(x=None, y=None, z=None, x_value=0.0, y_value=0.0, z_value=0.0):
		node = nodes.new("ShaderNodeCombineXYZ")
		node.inputs["X"].default_value = x_value
		node.inputs["Y"].default_value = y_value
		node.inputs["Z"].default_value = z_value
		if x is not None:
			links.new(x, node.inputs["X"])
		if y is not None:
			links.new(y, node.inputs["Y"])
		if z is not None:
			links.new(z, node.inputs["Z"])
		return node.outputs["Vector"]

	def ellipse(angle, radial_factor=None, z=None):
		cos_angle = math_node('COSINE', angle)
		sin_angle = math_node('SINE', angle)
		x = math_node('MULTIPLY', cos_angle, group_input.outputs["Shape Radius"])
		y = math_node('MULTIPLY', sin_angle, group_input.outputs["Shape Radius Minor"])
		if radial_factor is not None:
			x = math_node('MULTIPLY', x, radial_factor)
			y = math_node('MULTIPLY', y, radial_factor)
		return combine(x, y, z)

	def random_angle():
		return math_node('MULTIPLY', random_float(), value_b=2.0 * math.pi)

	# Point.
	shapes = [combine()]

	# Ring (uniform): a low-discrepancy angle derived from the particle ID.
	uniform_angle = math_node('MULTIPLY', particle_index.outputs["Index"], value_b=math.pi * (3.0 - math.sqrt(5.0)))
	shapes.append(ellipse(uniform_angle))

	# Cylinder (uniform): fixed radius with an evenly distributed angle and
	# random height. Cylinder (random): random angle and volume-weighted radius.
	cylinder_z = math_node('MULTIPLY', random_float(-1.0, 1.0), group_input.outputs["Shape Height"])
	shapes.append(ellipse(uniform_angle, z=cylinder_z))
	random_cylinder_radius = math_node('POWER', random_float(), value_b=0.5)
	random_cylinder_z = math_node('MULTIPLY', random_float(-1.0, 1.0), group_input.outputs["Shape Height"])
	shapes.append(ellipse(random_angle(), random_cylinder_radius, random_cylinder_z))

	# Random disk.
	disk_radius = math_node('POWER', random_float(), value_b=0.5)
	shapes.append(ellipse(random_angle(), disk_radius))

	# Random ellipsoid volume. cos(theta) is uniform in [-1, 1] and the cube
	# root radius makes particle density uniform through the volume.
	sphere_u = random_float(-1.0, 1.0)
	sphere_phi = random_angle()
	sphere_radius = math_node('POWER', random_float(), value_b=1.0 / 3.0)
	u_squared = math_node('MULTIPLY', sphere_u, sphere_u)
	one_minus_u_squared = math_node('SUBTRACT', value_a=1.0, b=u_squared)
	sphere_xy = math_node('SQRT', one_minus_u_squared)
	sphere_xy = math_node('MULTIPLY', sphere_xy, sphere_radius)
	sphere_x = math_node('MULTIPLY', math_node('COSINE', sphere_phi), sphere_xy)
	sphere_x = math_node('MULTIPLY', sphere_x, group_input.outputs["Shape Radius"])
	sphere_y = math_node('MULTIPLY', math_node('SINE', sphere_phi), sphere_xy)
	sphere_y = math_node('MULTIPLY', sphere_y, group_input.outputs["Shape Radius Minor"])
	sphere_z = math_node('MULTIPLY', sphere_u, sphere_radius)
	sphere_z = math_node('MULTIPLY', sphere_z, group_input.outputs["Shape Height"])
	shapes.append(combine(sphere_x, sphere_y, sphere_z))

	# Random cube/box.
	cube = nodes.new("FunctionNodeRandomValue")
	cube.data_type = 'FLOAT_VECTOR'
	random_nodes.append(cube)
	links.new(group_input.outputs["Spawn Min"], cube.inputs["Min"])
	links.new(group_input.outputs["Spawn Max"], cube.inputs["Max"])
	shapes.append(cube.outputs["Value"])

	# Random cone volume, centered vertically. Radius tapers to zero at +height.
	cone_t = random_float()
	cone_z_normalized = math_node('MULTIPLY', cone_t, value_b=2.0)
	cone_z_normalized = math_node('SUBTRACT', cone_z_normalized, value_b=1.0)
	cone_z = math_node('MULTIPLY', cone_z_normalized, group_input.outputs["Shape Height"])
	cone_radius = math_node('SUBTRACT', value_a=1.0, b=cone_t)
	cone_radius = math_node('MULTIPLY', cone_radius, math_node('POWER', random_float(), value_b=0.5))
	shapes.append(ellipse(random_angle(), cone_radius, cone_z))

	# Random torus volume. Shape Radius is the major radius and Shape Radius
	# Minor is the tube radius; Shape Height scales the tube vertically.
	torus_major_angle = random_angle()
	torus_minor_angle = random_angle()
	torus_tube_factor = math_node('POWER', random_float(), value_b=0.5)
	torus_tube_radius = math_node('MULTIPLY', group_input.outputs["Shape Radius Minor"], torus_tube_factor)
	torus_minor_cos = math_node('MULTIPLY', math_node('COSINE', torus_minor_angle), torus_tube_radius)
	torus_ring_radius = math_node('ADD', group_input.outputs["Shape Radius"], torus_minor_cos)
	torus_x = math_node('MULTIPLY', math_node('COSINE', torus_major_angle), torus_ring_radius)
	torus_y = math_node('MULTIPLY', math_node('SINE', torus_major_angle), torus_ring_radius)
	torus_z = math_node('MULTIPLY', math_node('SINE', torus_minor_angle), torus_tube_factor)
	torus_z = math_node('MULTIPLY', torus_z, group_input.outputs["Shape Height"])
	shapes.append(combine(torus_x, torus_y, torus_z))

	# Ring (random): fixed radius and random angle.
	shapes.append(ellipse(random_angle()))

	# Select the requested shape without duplicating the node group per emitter.
	selected = shapes[0]
	for shape_index in range(1, 10):
		compare = nodes.new("FunctionNodeCompare")
		compare.data_type = 'INT'
		compare.operation = 'EQUAL'
		compare.inputs["B"].default_value = shape_index
		links.new(group_input.outputs["Spawn Shape"], compare.inputs["A"])
		switch = nodes.new("GeometryNodeSwitch")
		switch.input_type = 'VECTOR'
		links.new(compare.outputs["Result"], switch.inputs["Switch"])
		links.new(selected, switch.inputs["False"])
		links.new(shapes[shape_index], switch.inputs["True"])
		selected = switch.outputs["Output"]

	return selected, random_nodes

def create_emitter_geometry_nodes(obj, material):
	name = EMITTER_NODE_GROUP_NAME
	node_group = bpy.data.node_groups.get(name)
	if node_group:
		modifier = obj.modifiers.get("EverQuest Particles")
		if not modifier or modifier.type != 'NODES':
			modifier = obj.modifiers.new(name="EverQuest Particles", type='NODES')
		modifier.node_group = node_group
		set_emitter_modifier_inputs(obj, modifier, node_group, material)
		set_emitter_frame_range(obj, modifier, node_group)
		return modifier

	node_group = bpy.data.node_groups.new(name, "GeometryNodeTree")
	node_group.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')
	start_socket = node_group.interface.new_socket(name="Start Frame", in_out='INPUT', socket_type='NodeSocketInt')
	end_socket = node_group.interface.new_socket(name="End Frame", in_out='INPUT', socket_type='NodeSocketInt')
	start_socket.default_value = bpy.context.scene.frame_start
	end_socket.default_value = bpy.context.scene.frame_end
	for input_name, socket_type, default in (
		("Material", 'NodeSocketMaterial', None),
		("Particle Lifespan", 'NodeSocketFloat', 1.0),
		("Creation Count", 'NodeSocketInt', 0),
		("Particles Per Interval", 'NodeSocketInt', 0),
		("Interval Rate", 'NodeSocketFloat', 0.0),
		("Safe Particles Per Interval", 'NodeSocketFloat', 1.0),
		("Safe Interval Rate", 'NodeSocketFloat', 0.0001),
		("Spawn Delay", 'NodeSocketFloat', 0.0),
		("Tint Start", 'NodeSocketColor', (1.0, 1.0, 1.0, 1.0)),
		("Tint End", 'NodeSocketColor', (1.0, 1.0, 1.0, 1.0)),
		("Use Fade In", 'NodeSocketBool', False),
		("Fade In Time", 'NodeSocketFloat', 0.0001),
		("Use Fade Out", 'NodeSocketBool', False),
		("Fade Out Time", 'NodeSocketFloat', 0.0001),
		("Use Scale In", 'NodeSocketBool', False),
		("Scale In Time", 'NodeSocketFloat', 0.0001),
		("Use Scale Out", 'NodeSocketBool', False),
		("Scale Out Time", 'NodeSocketFloat', 0.0001),
		("Use Width Squash", 'NodeSocketBool', False),
		("Width Squash Time", 'NodeSocketFloat', 0.0001),
		("Use Height Squash", 'NodeSocketBool', False),
		("Height Squash Time", 'NodeSocketFloat', 0.0001),
		("Max Alpha", 'NodeSocketFloat', 1.0),
		("Animation Rate", 'NodeSocketFloat', 1.0),
		("Animation Frames", 'NodeSocketFloat', 1.0),
		("Atlas Columns", 'NodeSocketFloat', 1.0),
		("Atlas Rows", 'NodeSocketFloat', 1.0),
		("Spawn Shape", 'NodeSocketInt', 0),
		("Shape Radius", 'NodeSocketFloat', 0.0),
		("Shape Radius Minor", 'NodeSocketFloat', 0.0),
		("Shape Height", 'NodeSocketFloat', 0.0),
		("Spawn Min", 'NodeSocketVector', (0.0, 0.0, 0.0)),
		("Spawn Max", 'NodeSocketVector', (0.0, 0.0, 0.0)),
		("Allow Center Pass Through", 'NodeSocketBool', False),
		("Velocity Min", 'NodeSocketVector', (0.0, 0.0, 0.0)),
		("Velocity Max", 'NodeSocketVector', (0.0, 0.0, 0.0)),
		("Acceleration", 'NodeSocketVector', (0.0, 0.0, 0.0)),
		("Outward Speed Min", 'NodeSocketFloat', 0.0),
		("Outward Speed Max", 'NodeSocketFloat', 0.0),
		("Half Outward Acceleration", 'NodeSocketFloat', 0.0),
		("Random Outward Direction", 'NodeSocketBool', False),
		("Orbital Speed Min", 'NodeSocketFloat', 0.0),
		("Orbital Speed Max", 'NodeSocketFloat', 0.0),
		("Half Orbital Acceleration", 'NodeSocketFloat', 0.0),
		("Random Start Rotation Max", 'NodeSocketFloat', 0.0),
		("Spin Rate Min", 'NodeSocketFloat', 0.0),
		("Spin Rate Max", 'NodeSocketFloat', 0.0),
		("Particle Width", 'NodeSocketFloat', 1.0),
		("Particle Height", 'NodeSocketFloat', 1.0),
		("Random Scale Max", 'NodeSocketVector', (1.0, 1.0, 1.0)),
	):
		add_emitter_input(node_group, input_name, socket_type, default)

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
	fade_in_switch = nodes.new("GeometryNodeSwitch")
	lifetime_remaining = nodes.new("ShaderNodeMath")
	fade_out_factor = nodes.new("ShaderNodeMath")
	fade_out_switch = nodes.new("GeometryNodeSwitch")
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
	random_velocity = nodes.new("FunctionNodeRandomValue")
	velocity_movement = nodes.new("ShaderNodeVectorMath")
	acceleration_vector = nodes.new("ShaderNodeCombineXYZ")
	acceleration_movement = nodes.new("ShaderNodeVectorMath")
	directional_movement = nodes.new("ShaderNodeVectorMath")
	random_outward_direction = nodes.new("FunctionNodeRandomValue")
	outward_direction = nodes.new("ShaderNodeVectorMath")
	outward_direction_switch = nodes.new("GeometryNodeSwitch")
	random_outward_speed = nodes.new("FunctionNodeRandomValue")
	outward_velocity_distance = nodes.new("ShaderNodeMath")
	outward_acceleration_distance = nodes.new("ShaderNodeMath")
	outward_distance = nodes.new("ShaderNodeMath")
	outward_movement = nodes.new("ShaderNodeVectorMath")
	radial_position = nodes.new("ShaderNodeVectorMath")
	spawn_radius = nodes.new("ShaderNodeVectorMath")
	signed_radial_distance = nodes.new("ShaderNodeMath")
	has_not_crossed_center = nodes.new("FunctionNodeCompare")
	center_pass_allowed = nodes.new("FunctionNodeBooleanMath")
	particle_center_visible = nodes.new("FunctionNodeBooleanMath")
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
	camera_rotation = nodes.new("FunctionNodeRotateRotation")
	random_scale = nodes.new("FunctionNodeRandomValue")
	scale_in_factor = nodes.new("ShaderNodeMath")
	scale_in_switch = nodes.new("GeometryNodeSwitch")
	scale_out_factor = nodes.new("ShaderNodeMath")
	scale_out_switch = nodes.new("GeometryNodeSwitch")
	uniform_scale = nodes.new("ShaderNodeMath")
	width_squash_factor = nodes.new("ShaderNodeMath")
	width_squash_switch = nodes.new("GeometryNodeSwitch")
	height_squash_factor = nodes.new("ShaderNodeMath")
	height_squash_switch = nodes.new("GeometryNodeSwitch")
	separate_random_scale = nodes.new("ShaderNodeSeparateXYZ")
	final_width_scale = nodes.new("ShaderNodeMath")
	final_width_squash = nodes.new("ShaderNodeMath")
	final_height_scale = nodes.new("ShaderNodeMath")
	final_height_squash = nodes.new("ShaderNodeMath")
	final_instance_scale = nodes.new("ShaderNodeCombineXYZ")
	sprite = nodes.new("GeometryNodeMeshGrid")
	store_uv = nodes.new("GeometryNodeStoreNamedAttribute")
	transform_sprite = nodes.new("GeometryNodeTransform")
	set_material = nodes.new("GeometryNodeSetMaterial")
	instance = nodes.new("GeometryNodeInstanceOnPoints")

	spawn_position, spawn_random_nodes = build_spawn_shape_field(
		nodes,
		links,
		group_input,
		particle_index,
	)

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
	fade_in_factor.operation = 'DIVIDE'
	fade_in_factor.use_clamp = True
	fade_in_switch.input_type = 'FLOAT'
	fade_in_switch.inputs["False"].default_value = 1.0
	fade_out_factor.operation = 'DIVIDE'
	fade_out_factor.use_clamp = True
	fade_out_switch.input_type = 'FLOAT'
	fade_out_switch.inputs["False"].default_value = 1.0
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
	outward_direction_switch.input_type = 'VECTOR'
	outward_velocity_distance.operation = 'MULTIPLY'
	outward_acceleration_distance.operation = 'MULTIPLY'
	outward_distance.operation = 'ADD'
	outward_movement.operation = 'SCALE'
	radial_position.operation = 'ADD'
	spawn_radius.operation = 'LENGTH'
	signed_radial_distance.operation = 'ADD'
	has_not_crossed_center.data_type = 'FLOAT'
	has_not_crossed_center.operation = 'GREATER_EQUAL'
	has_not_crossed_center.inputs["B"].default_value = 0.0
	center_pass_allowed.operation = 'OR'
	particle_center_visible.operation = 'AND'
	orbital_velocity_angle.operation = 'MULTIPLY'
	orbital_acceleration_angle.operation = 'MULTIPLY'
	orbital_angle.operation = 'ADD'
	orbital_rotation.rotation_type = 'AXIS_ANGLE'
	particle_movement.operation = 'ADD'
	spin_movement.operation = 'MULTIPLY'
	particle_rotation.operation = 'ADD'
	camera_info.transform_space = 'RELATIVE'
	camera_rotation.rotation_space = 'LOCAL'
	scale_in_factor.operation = 'DIVIDE'
	scale_in_factor.use_clamp = True
	scale_in_switch.input_type = 'FLOAT'
	scale_in_switch.inputs["False"].default_value = 1.0
	scale_out_factor.operation = 'DIVIDE'
	scale_out_factor.use_clamp = True
	scale_out_switch.input_type = 'FLOAT'
	scale_out_switch.inputs["False"].default_value = 1.0
	uniform_scale.operation = 'MINIMUM'
	width_squash_factor.operation = 'DIVIDE'
	width_squash_factor.use_clamp = True
	width_squash_switch.input_type = 'FLOAT'
	width_squash_switch.inputs["False"].default_value = 1.0
	height_squash_factor.operation = 'DIVIDE'
	height_squash_factor.use_clamp = True
	height_squash_switch.input_type = 'FLOAT'
	height_squash_switch.inputs["False"].default_value = 1.0
	final_width_scale.operation = 'MULTIPLY'
	final_width_squash.operation = 'MULTIPLY'
	final_height_scale.operation = 'MULTIPLY'
	final_height_squash.operation = 'MULTIPLY'
	final_instance_scale.inputs["Z"].default_value = 1.0

	fps = bpy.context.scene.render.fps / bpy.context.scene.render.fps_base
	frame_seconds.inputs[1].default_value = 1.0 / fps
	range_seconds.inputs[1].default_value = 1.0 / fps
	positive_interval_time.inputs[1].default_value = 0.0
	interval_event_number.inputs[1].default_value = 1.0
	particle_started.inputs["B"].default_value = 0.0
	half_age_squared.inputs[1].default_value = 0.5
	row_plus_one.inputs[1].default_value = 1.0
	row_offset.inputs[0].default_value = 1.0

	mesh_line.inputs["Count"].default_value = 1
	mesh_line.inputs["Start Location"].default_value = (0.0, 0.0, 0.0)
	mesh_line.inputs["Offset"].default_value = (0.0, 0.0, 0.0)

	random_velocity.data_type = 'FLOAT_VECTOR'

	random_outward_direction.data_type = 'FLOAT_VECTOR'
	random_outward_direction.inputs["Min"].default_value = (-1.0, -1.0, -1.0)
	random_outward_direction.inputs["Max"].default_value = (1.0, 1.0, 1.0)
	random_outward_speed.data_type = 'FLOAT'

	random_orbital_speed.data_type = 'FLOAT'
	orbital_rotation.inputs["Axis"].default_value = (0.0, 0.0, 1.0)

	random_start_rotation.data_type = 'FLOAT'
	random_start_rotation.inputs["Min"].default_value = 0.0
	random_spin_rate.data_type = 'FLOAT'

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

	# A Blender camera looks down its local -Z axis. Flip the grid so its
	# visible normal also points down local -Z, then use the camera rotation
	# directly. This preserves a stable camera up/right orientation.
	transform_sprite.inputs["Rotation"].default_value = (math.pi, 0.0, 0.0)

	random_scale.data_type = 'FLOAT_VECTOR'
	random_scale.inputs["Min"].default_value = (1.0, 1.0, 1.0)

	# Every point now represents one real emission. Its point index is therefore
	# a stable, unique particle ID. Different fixed seeds keep the independently
	# randomized properties from being correlated.
	random_nodes = (
		random_velocity,
		random_outward_direction,
		random_outward_speed,
		random_orbital_speed,
		random_start_rotation,
		random_spin_rate,
		random_scale,
		*spawn_random_nodes,
	)
	for seed_offset, random_node in enumerate(random_nodes, start=1):
		random_node.inputs["Seed"].default_value = seed_offset * 101

	links.new(scene_time.outputs["Frame"], after_start.inputs["A"])
	links.new(group_input.outputs["Start Frame"], after_start.inputs["B"])
	links.new(scene_time.outputs["Frame"], before_end.inputs["A"])
	links.new(group_input.outputs["End Frame"], before_end.inputs["B"])
	links.new(after_start.outputs["Result"], in_frame_range.inputs[0])
	links.new(before_end.outputs["Result"], in_frame_range.inputs[1])
	links.new(scene_time.outputs["Frame"], frame_offset.inputs[0])
	links.new(group_input.outputs["Start Frame"], frame_offset.inputs[1])
	links.new(frame_offset.outputs[0], frame_seconds.inputs[0])
	links.new(group_input.outputs["Spawn Delay"], interval_time_available.inputs[1])
	links.new(group_input.outputs["Interval Rate"], interval_event_count.inputs[1])
	links.new(group_input.outputs["Particles Per Interval"], interval_particle_count.inputs[1])
	links.new(group_input.outputs["Creation Count"], total_particle_count.inputs[1])
	links.new(group_input.outputs["Creation Count"], is_creation_particle.inputs["B"])
	links.new(group_input.outputs["Creation Count"], interval_particle_index.inputs[1])
	links.new(group_input.outputs["Safe Particles Per Interval"], interval_event_divide.inputs[1])
	links.new(group_input.outputs["Safe Interval Rate"], interval_birth_offset.inputs[1])
	links.new(group_input.outputs["Spawn Delay"], interval_birth_time.inputs[1])
	links.new(group_input.outputs["Spawn Delay"], birth_time.inputs["True"])
	links.new(group_input.outputs["Particle Lifespan"], particle_alive.inputs["B"])
	links.new(group_input.outputs["Particle Lifespan"], normalized_age.inputs[1])
	links.new(group_input.outputs["Tint Start"], tint_mix.inputs[1])
	links.new(group_input.outputs["Tint End"], tint_mix.inputs[2])
	links.new(group_input.outputs["Fade In Time"], fade_in_factor.inputs[1])
	links.new(group_input.outputs["Use Fade In"], fade_in_switch.inputs["Switch"])
	links.new(group_input.outputs["Fade Out Time"], fade_out_factor.inputs[1])
	links.new(group_input.outputs["Use Fade Out"], fade_out_switch.inputs["Switch"])
	links.new(group_input.outputs["Use Scale In"], scale_in_switch.inputs["Switch"])
	links.new(group_input.outputs["Scale In Time"], scale_in_factor.inputs[1])
	links.new(group_input.outputs["Use Scale Out"], scale_out_switch.inputs["Switch"])
	links.new(group_input.outputs["Scale Out Time"], scale_out_factor.inputs[1])
	links.new(group_input.outputs["Use Width Squash"], width_squash_switch.inputs["Switch"])
	links.new(group_input.outputs["Width Squash Time"], width_squash_factor.inputs[1])
	links.new(group_input.outputs["Use Height Squash"], height_squash_switch.inputs["Switch"])
	links.new(group_input.outputs["Height Squash Time"], height_squash_factor.inputs[1])
	links.new(group_input.outputs["Particle Lifespan"], lifetime_remaining.inputs[0])
	links.new(group_input.outputs["Max Alpha"], particle_alpha.inputs[1])
	links.new(group_input.outputs["Animation Rate"], animation_position.inputs[1])
	links.new(group_input.outputs["Animation Frames"], wrapped_frame.inputs[1])
	links.new(group_input.outputs["Atlas Columns"], atlas_column.inputs[1])
	links.new(group_input.outputs["Atlas Columns"], atlas_row_divide.inputs[1])
	links.new(group_input.outputs["Atlas Columns"], column_offset.inputs[1])
	links.new(group_input.outputs["Atlas Rows"], row_fraction.inputs[1])
	links.new(group_input.outputs["Velocity Min"], random_velocity.inputs["Min"])
	links.new(group_input.outputs["Velocity Max"], random_velocity.inputs["Max"])
	links.new(group_input.outputs["Outward Speed Min"], random_outward_speed.inputs["Min"])
	links.new(group_input.outputs["Outward Speed Max"], random_outward_speed.inputs["Max"])
	links.new(group_input.outputs["Half Outward Acceleration"], outward_acceleration_distance.inputs[1])
	links.new(group_input.outputs["Random Outward Direction"], outward_direction_switch.inputs["Switch"])
	links.new(group_input.outputs["Orbital Speed Min"], random_orbital_speed.inputs["Min"])
	links.new(group_input.outputs["Orbital Speed Max"], random_orbital_speed.inputs["Max"])
	links.new(group_input.outputs["Half Orbital Acceleration"], orbital_acceleration_angle.inputs[1])
	links.new(group_input.outputs["Random Start Rotation Max"], random_start_rotation.inputs["Max"])
	links.new(group_input.outputs["Spin Rate Min"], random_spin_rate.inputs["Min"])
	links.new(group_input.outputs["Spin Rate Max"], random_spin_rate.inputs["Max"])
	links.new(group_input.outputs["Particle Width"], sprite.inputs["Size X"])
	links.new(group_input.outputs["Particle Height"], sprite.inputs["Size Y"])
	links.new(group_input.outputs["Random Scale Max"], random_scale.inputs["Max"])
	links.new(group_input.outputs["Material"], set_material.inputs["Material"])

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
	links.new(particle_age.outputs[0], fade_in_factor.inputs[0])
	links.new(fade_in_factor.outputs[0], fade_in_switch.inputs["True"])
	links.new(particle_age.outputs[0], lifetime_remaining.inputs[1])
	links.new(lifetime_remaining.outputs[0], fade_out_factor.inputs[0])
	links.new(fade_out_factor.outputs[0], fade_out_switch.inputs["True"])
	links.new(fade_in_switch.outputs["Output"], fade_factor.inputs[0])
	links.new(fade_out_switch.outputs["Output"], fade_factor.inputs[1])
	links.new(fade_factor.outputs[0], particle_alpha.inputs[0])

	# SCALEINTIME grows uniformly from zero to full size. SCALEOUTTIME
	# shrinks uniformly from full size to zero over the remaining lifetime.
	links.new(particle_age.outputs[0], scale_in_factor.inputs[0])
	links.new(scale_in_factor.outputs[0], scale_in_switch.inputs["True"])
	links.new(lifetime_remaining.outputs[0], scale_out_factor.inputs[0])
	links.new(scale_out_factor.outputs[0], scale_out_switch.inputs["True"])
	links.new(scale_in_switch.outputs["Output"], uniform_scale.inputs[0])
	links.new(scale_out_switch.outputs["Output"], uniform_scale.inputs[1])

	# Squash timing is measured backward from death. A squash duration longer
	# than the particle lifespan therefore begins partially reduced at birth.
	links.new(lifetime_remaining.outputs[0], width_squash_factor.inputs[0])
	links.new(width_squash_factor.outputs[0], width_squash_switch.inputs["True"])
	links.new(lifetime_remaining.outputs[0], height_squash_factor.inputs[0])
	links.new(height_squash_factor.outputs[0], height_squash_switch.inputs["True"])

	# The billboard grid lies in local XY: X is width, Y is height, and Z is
	# its normal. Apply the uniform envelope and independent squash envelopes
	# without realizing the particle instances.
	links.new(random_scale.outputs["Value"], separate_random_scale.inputs["Vector"])
	links.new(separate_random_scale.outputs["X"], final_width_scale.inputs[0])
	links.new(uniform_scale.outputs[0], final_width_scale.inputs[1])
	links.new(final_width_scale.outputs[0], final_width_squash.inputs[0])
	links.new(width_squash_switch.outputs["Output"], final_width_squash.inputs[1])
	links.new(separate_random_scale.outputs["Y"], final_height_scale.inputs[0])
	links.new(uniform_scale.outputs[0], final_height_scale.inputs[1])
	links.new(final_height_scale.outputs[0], final_height_squash.inputs[0])
	links.new(height_squash_switch.outputs["Output"], final_height_squash.inputs[1])
	links.new(final_width_squash.outputs[0], final_instance_scale.inputs["X"])
	links.new(final_height_squash.outputs[0], final_instance_scale.inputs["Y"])
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
	links.new(group_input.outputs["Acceleration"], acceleration_movement.inputs["Vector"])
	links.new(half_age_squared.outputs[0], acceleration_movement.inputs["Scale"])
	links.new(velocity_movement.outputs["Vector"], directional_movement.inputs[0])
	links.new(acceleration_movement.outputs["Vector"], directional_movement.inputs[1])
	links.new(spawn_position, outward_direction_switch.inputs["False"])
	links.new(random_outward_direction.outputs["Value"], outward_direction_switch.inputs["True"])
	links.new(outward_direction_switch.outputs["Output"], outward_direction.inputs[0])
	links.new(random_outward_speed.outputs["Value"], outward_velocity_distance.inputs[0])
	links.new(particle_age.outputs[0], outward_velocity_distance.inputs[1])
	links.new(age_squared.outputs[0], outward_acceleration_distance.inputs[0])
	links.new(outward_velocity_distance.outputs[0], outward_distance.inputs[0])
	links.new(outward_acceleration_distance.outputs[0], outward_distance.inputs[1])
	links.new(outward_direction.outputs["Vector"], outward_movement.inputs["Vector"])
	links.new(outward_distance.outputs[0], outward_movement.inputs["Scale"])
	links.new(spawn_position, radial_position.inputs[0])
	links.new(outward_movement.outputs["Vector"], radial_position.inputs[1])

	# A negative outward acceleration can reverse a particle and pull it back
	# through the emitter origin. EQ removes it at that crossing unless
	# ALLOWCENTERPASSTHROUGH is enabled.
	links.new(spawn_position, spawn_radius.inputs[0])
	links.new(spawn_radius.outputs["Value"], signed_radial_distance.inputs[0])
	links.new(outward_distance.outputs[0], signed_radial_distance.inputs[1])
	links.new(signed_radial_distance.outputs[0], has_not_crossed_center.inputs["A"])
	links.new(group_input.outputs["Allow Center Pass Through"], center_pass_allowed.inputs[0])
	links.new(has_not_crossed_center.outputs["Result"], center_pass_allowed.inputs[1])
	links.new(particle_visible.outputs["Boolean"], particle_center_visible.inputs[0])
	links.new(center_pass_allowed.outputs["Boolean"], particle_center_visible.inputs[1])
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
	links.new(particle_rotation.outputs[0], rotation_vector.inputs["Z"])
	links.new(active_camera.outputs["Active Camera"], camera_info.inputs["Object"])
	links.new(camera_info.outputs["Rotation"], camera_rotation.inputs["Rotation"])
	links.new(rotation_vector.outputs["Vector"], camera_rotation.inputs["Rotate By"])
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
	links.new(particle_center_visible.outputs["Boolean"], instance.inputs["Selection"])
	links.new(camera_rotation.outputs["Rotation"], instance.inputs["Rotation"])
	links.new(final_instance_scale.outputs["Vector"], instance.inputs["Scale"])
	links.new(instance.outputs["Instances"], output.inputs["Geometry"])

	modifier = obj.modifiers.get("EverQuest Particles")
	if not modifier or modifier.type != 'NODES':
		modifier = obj.modifiers.new(name="EverQuest Particles", type='NODES')
	modifier.node_group = node_group
	set_emitter_modifier_inputs(obj, modifier, node_group, material)
	set_emitter_frame_range(obj, modifier, node_group)
	return modifier

def get_emitter_modifier(obj):
	modifier = obj.modifiers.get("EverQuest Particles") if obj else None
	if modifier and modifier.type == 'NODES':
		return modifier
	return None

def apply_emitter_settings(obj):
	if not obj or obj.get("quaildef") != "emitterdef":
		return
	material = obj.data.materials[0] if obj.data and obj.data.materials else None
	if material is None:
		material = create_emitter_material(obj)
		if obj.data:
			obj.data.materials.append(material)
	modifier = get_emitter_modifier(obj)
	if modifier is None or modifier.node_group is None:
		create_emitter_geometry_nodes(obj, material)
		return
	set_emitter_modifier_inputs(obj, modifier, modifier.node_group, material)

def apply_emitter_material(obj, assets_path=None):
	if not obj or obj.get("quaildef") != "emitterdef":
		return
	material = create_emitter_material(obj, assets_path)
	if obj.data:
		if obj.data.materials:
			obj.data.materials[0] = material
		else:
			obj.data.materials.append(material)
	modifier = get_emitter_modifier(obj)
	if modifier and modifier.node_group:
		set_modifier_input(modifier, modifier.node_group, "Material", material)

def apply_emitter_transform(obj):
	if not obj or obj.get("quaildef") != "emitterdef":
		return
	shapeoffset = obj.quail_emitterdef.shapeoffset
	obj.location = (shapeoffset[2], shapeoffset[1], shapeoffset[0])

def apply_emitter(obj, assets_path=None):
	if not obj or obj.get("quaildef") != "emitterdef":
		return
	apply_emitter_transform(obj)
	apply_emitter_material(obj, assets_path)
	apply_emitter_settings(obj)
