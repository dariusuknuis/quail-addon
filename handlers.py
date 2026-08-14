import random

import bpy
from .common import state
from .common.animation import action_matches_eqg_animation


def get_particle_renderer_modifier(obj):
	modifier = obj.modifiers.get("EverQuest Particles")
	if modifier and modifier.type == 'NODES' and modifier.node_group:
		return modifier
	return None


def geometry_input_identifier(node_group, name: str):
	cache_key = (node_group.as_pointer(), name)
	cached = EqgParticleRenderRuntime.input_identifiers.get(cache_key)
	if cached:
		return cached
	for socket in node_group.interface.items_tree:
		if socket.item_type == 'SOCKET' and socket.in_out == 'INPUT' and socket.name == name:
			EqgParticleRenderRuntime.input_identifiers[cache_key] = socket.identifier
			return socket.identifier
	return None


def modifier_input_has_driver(obj, modifier, identifier: str):
	animation_data = obj.animation_data
	if not animation_data:
		return False
	expected = f'modifiers["{modifier.name}"]["{identifier}"]'
	return any(fcurve.data_path == expected for fcurve in animation_data.drivers)


def set_particle_renderer_range(obj, start_frame: float, end_frame: float):
	modifier = get_particle_renderer_modifier(obj)
	if not modifier:
		return False

	changed = False
	for name, value in (("Start Frame", start_frame), ("End Frame", end_frame)):
		identifier = geometry_input_identifier(modifier.node_group, name)
		if not identifier:
			return False

		target_value = int(round(value))
		data_path = f'["{identifier}"]'
		has_driver = modifier_input_has_driver(obj, modifier, identifier)
		current_value = modifier.get(identifier)
		if not has_driver and current_value == target_value:
			continue

		if has_driver:
			try:
				modifier.driver_remove(data_path)
			except (TypeError, RuntimeError):
				pass
		modifier[identifier] = target_value
		changed = True

	if changed:
		obj.update_tag()
	return True


def set_particle_renderer_enabled(obj, enabled: bool):
	hidden = not enabled
	if obj.hide_viewport != hidden:
		obj.hide_viewport = hidden
	if obj.hide_render != hidden:
		obj.hide_render = hidden


def disable_particle_renderer(obj):
	result = set_particle_renderer_range(obj, 1.0, 0.0)
	set_particle_renderer_enabled(obj, False)
	return result


def particle_renderer_armature(obj):
	for constraint in obj.constraints:
		if constraint.type not in {'CHILD_OF', 'COPY_LOCATION'}:
			continue
		point = constraint.target
		if point and point.parent and point.parent.type == 'ARMATURE':
			return point.parent
	return None


def particle_renderer_model_tag(obj):
	armature = particle_renderer_armature(obj)
	if not armature:
		return ""
	name = armature.name
	if name.lower().endswith("_armature"):
		return name[:-9]
	return name


def initialize_particle_renderer(obj, scene=None):
	if not obj or obj.get("quaildef") != "eqgparticlerender":
		return
	if not get_particle_renderer_modifier(obj):
		return

	scene = scene or bpy.context.scene
	props = obj.quail_eqgparticlerender
	if props.particletype == '0':
		fps = scene.render.fps / scene.render.fps_base
		start = scene.frame_start + (props.starttime / 1000.0) * fps
		set_particle_renderer_range(obj, start, scene.frame_end)
		set_particle_renderer_enabled(obj, True)
	else:
		disable_particle_renderer(obj)


class EqgParticleRenderRuntime:
	last_frame = None
	last_actions = {}
	active_ranges = {}
	input_identifiers = {}

	@classmethod
	def reset(cls):
		cls.last_frame = None
		cls.last_actions.clear()
		cls.active_ranges.clear()
		cls.input_identifiers.clear()

	@classmethod
	def update(cls, scene):
		current_frame = float(scene.frame_current)
		fps = scene.render.fps / scene.render.fps_base
		went_backwards = cls.last_frame is not None and current_frame < cls.last_frame
		current_actions = {}
		changed_armatures = set()

		for armature in bpy.data.objects:
			if armature.type != 'ARMATURE' or not armature.animation_data:
				continue
			action = armature.animation_data.action
			if not action:
				continue
			armature_key = armature.as_pointer()
			action_identity = action.as_pointer()
			current_actions[armature_key] = action_identity
			if cls.last_actions.get(armature_key) != action_identity:
				changed_armatures.add(armature_key)

		if went_backwards:
			cls.active_ranges.clear()

		for obj in bpy.data.objects:
			if obj.get("quaildef") != "eqgparticlerender":
				continue
			if not get_particle_renderer_modifier(obj):
				continue

			props = obj.quail_eqgparticlerender
			if props.particletype == '0':
				start = scene.frame_start + (props.starttime / 1000.0) * fps
				set_particle_renderer_range(obj, start, scene.frame_end)
				set_particle_renderer_enabled(obj, True)
				continue

			key = obj.as_pointer()
			active = cls.active_ranges.get(key)
			if active and current_frame <= active[1]:
				set_particle_renderer_range(obj, active[0], active[1])
				set_particle_renderer_enabled(obj, True)
				continue
			if active:
				cls.active_ranges.pop(key, None)

			armature = particle_renderer_armature(obj)
			action = armature.animation_data.action if armature and armature.animation_data else None
			model_tag = particle_renderer_model_tag(obj)
			if not action_matches_eqg_animation(action, props.animnumber, model_tag):
				disable_particle_renderer(obj)
				continue

			action_key = armature.as_pointer()
			action_changed = action_key in changed_armatures
			trigger_frame = float(action.frame_range[0]) + (props.starttime / 1000.0) * fps
			end_frame = trigger_frame + float(props.lifespan) * fps
			previous_frame = cls.last_frame if cls.last_frame is not None else current_frame - 1.0
			crossed_trigger = previous_frame < trigger_frame <= current_frame
			inside_triggered_range = trigger_frame <= current_frame <= end_frame

			if action_changed and inside_triggered_range:
				crossed_trigger = True
			elif went_backwards and inside_triggered_range:
				crossed_trigger = True

			if crossed_trigger:
				if props.sporadic and random.random() >= 0.1:
					disable_particle_renderer(obj)
				else:
					cls.active_ranges[key] = (trigger_frame, end_frame)
					set_particle_renderer_range(obj, trigger_frame, end_frame)
					set_particle_renderer_enabled(obj, True)
			else:
				disable_particle_renderer(obj)

		cls.last_actions = current_actions
		cls.last_frame = current_frame


def sync_panel_from_armature(obj):
	if state.QUAIL_UPDATING:
		return

	state.QUAIL_UPDATING = True
	try:
		if not obj or obj.type != 'ARMATURE':
			return
		if obj.get("quaildef") != "hierarchicalspritedef":
			return

		props = obj.quail_hierarchicalspritedef
		bones = obj.data.bones
		old_dags = {}
		for dag in props.dags:
			old_dags[dag.tag] = {
				"track": dag.track,
				"spritetag": dag.spritetag,
			}

		while len(props.dags) > 0:
			props.dags.remove(0)

		for bone in bones:
			dag = props.dags.add()
			dag.tag = bone.name
			expected_track = bone.name
			if "DAG." in expected_track:
				expected_track = expected_track.replace("DAG.", "TRACK.")
			elif expected_track.endswith("DAG"):
				expected_track = expected_track[:-3] + "TRACK"

			old = old_dags.get(bone.name)
			if old:
				dag.track = old["track"] or expected_track
				if old["spritetag"]:
					dag.spritetag = old["spritetag"]
			else:
				dag.track = expected_track

		for dag in props.dags:
			while len(dag.subdags) > 0:
				dag.subdags.remove(0)

		name_to_index = {bone.name: i for i, bone in enumerate(bones)}
		for i, bone in enumerate(bones):
			if not bone.parent:
				continue
			parent_index = name_to_index.get(bone.parent.name)
			if parent_index is None:
				continue
			item = props.dags[parent_index].subdags.add()
			item.dag_index = i
	finally:
		state.QUAIL_UPDATING = False


class QuailHandlers:
	_last_mode = None

	@staticmethod
	@bpy.app.handlers.persistent
	def load_handler(_):
		EqgParticleRenderRuntime.reset()
		for obj in bpy.data.objects:
			if obj.get("quaildef") == "eqgparticlerender":
				initialize_particle_renderer(obj)

	@staticmethod
	def depsgraph_handler(scene, depsgraph):
		obj = bpy.context.object
		if not obj or obj.type != 'ARMATURE':
			return
		if obj.get("quaildef") != "hierarchicalspritedef":
			return

		current_mode = obj.mode
		if QuailHandlers._last_mode == 'EDIT' and current_mode != 'EDIT':
			sync_panel_from_armature(obj)
		QuailHandlers._last_mode = current_mode

	@staticmethod
	def particle_seed_handler(scene):
		if scene.frame_current != 1:
			return

		for obj in bpy.data.objects:
			if obj.get("quaildef") not in {"particleclouddef", "particlecloudinst"}:
				continue
			for modifier in obj.modifiers:
				if modifier.type != 'PARTICLE_SYSTEM':
					continue
				psys = modifier.particle_system
				if psys:
					psys.seed = random.randint(0, 1000000)

		bpy.context.view_layer.update()

	@staticmethod
	def eqg_particle_render_handler(scene):
		EqgParticleRenderRuntime.update(scene)

	@staticmethod
	@bpy.app.handlers.persistent
	def save_pre_handler(_):
		pass

	@staticmethod
	def register():
		if QuailHandlers.load_handler not in bpy.app.handlers.load_post:
			bpy.app.handlers.load_post.append(QuailHandlers.load_handler)
		if QuailHandlers.save_pre_handler not in bpy.app.handlers.save_pre:
			bpy.app.handlers.save_pre.append(QuailHandlers.save_pre_handler)
		if QuailHandlers.depsgraph_handler not in bpy.app.handlers.depsgraph_update_post:
			bpy.app.handlers.depsgraph_update_post.append(QuailHandlers.depsgraph_handler)
		if QuailHandlers.particle_seed_handler not in bpy.app.handlers.frame_change_pre:
			bpy.app.handlers.frame_change_pre.append(QuailHandlers.particle_seed_handler)
		if QuailHandlers.eqg_particle_render_handler not in bpy.app.handlers.frame_change_pre:
			bpy.app.handlers.frame_change_pre.append(QuailHandlers.eqg_particle_render_handler)

	@staticmethod
	def unregister():
		if QuailHandlers.save_pre_handler in bpy.app.handlers.save_pre:
			bpy.app.handlers.save_pre.remove(QuailHandlers.save_pre_handler)
		if QuailHandlers.load_handler in bpy.app.handlers.load_post:
			bpy.app.handlers.load_post.remove(QuailHandlers.load_handler)
		if QuailHandlers.depsgraph_handler in bpy.app.handlers.depsgraph_update_post:
			bpy.app.handlers.depsgraph_update_post.remove(QuailHandlers.depsgraph_handler)
		if QuailHandlers.particle_seed_handler in bpy.app.handlers.frame_change_pre:
			bpy.app.handlers.frame_change_pre.remove(QuailHandlers.particle_seed_handler)
		if QuailHandlers.eqg_particle_render_handler in bpy.app.handlers.frame_change_pre:
			bpy.app.handlers.frame_change_pre.remove(QuailHandlers.eqg_particle_render_handler)

		EqgParticleRenderRuntime.reset()
