import bpy, random
from .common import state

# =========================================================
# SAFE SYNC (Armature → Panel)
# =========================================================

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
                expected_track = expected_track.replace(
                    "DAG.",
                    "TRACK."
                )

            elif expected_track.endswith("DAG"):
                expected_track = (
                    expected_track[:-3] +
                    "TRACK"
                )

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

        name_to_index = {
            bone.name: i
            for i, bone in enumerate(bones)
        }

        for i, bone in enumerate(bones):
            if not bone.parent:
                continue

            parent_name = bone.parent.name
            if parent_name not in name_to_index:
                continue

            parent_index = name_to_index[parent_name]
            item = props.dags[parent_index].subdags.add()
            item.dag_index = i

    finally:

        state.QUAIL_UPDATING = False

class QuailHandlers:
    _last_mode = None
    @staticmethod
    @bpy.app.handlers.persistent
    def load_handler(_):
        pass
    @staticmethod
    def depsgraph_handler(scene, depsgraph):

        obj = bpy.context.object
        if not obj:
            return

        if obj.type != 'ARMATURE':
            return

        if obj.get("quaildef") != "hierarchicalspritedef":
            return

        current_mode = obj.mode

        if (
            QuailHandlers._last_mode == 'EDIT'
            and current_mode != 'EDIT'
        ):
            sync_panel_from_armature(obj)

        QuailHandlers._last_mode = current_mode

    @staticmethod
    def particle_seed_handler(scene):

        if scene.frame_current != 1:
            return

        for obj in bpy.data.objects:

            if obj.get("quaildef") not in {
                "particleclouddef",
                "particlecloudinst",
            }:
                continue

            for modifier in obj.modifiers:

                if modifier.type != 'PARTICLE_SYSTEM':
                    continue

                psys = modifier.particle_system

                if not psys:
                    continue

                psys.seed = random.randint(0, 1000000)

        bpy.context.view_layer.update()


    @staticmethod
    @bpy.app.handlers.persistent
    def save_pre_handler(_):
        pass

    @staticmethod
    def register():
        bpy.app.handlers.load_post.append(QuailHandlers.load_handler)
        bpy.app.handlers.save_pre.append(QuailHandlers.save_pre_handler)
        if QuailHandlers.depsgraph_handler not in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(QuailHandlers.depsgraph_handler)

        if QuailHandlers.particle_seed_handler not in bpy.app.handlers.frame_change_pre:
            bpy.app.handlers.frame_change_pre.append(
                QuailHandlers.particle_seed_handler
            )

    @staticmethod
    def unregister():
        bpy.app.handlers.save_pre.remove(QuailHandlers.save_pre_handler)
        bpy.app.handlers.load_post.remove(QuailHandlers.load_handler)
        if QuailHandlers.depsgraph_handler in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.remove(QuailHandlers.depsgraph_handler)

        if QuailHandlers.particle_seed_handler in bpy.app.handlers.frame_change_pre:
            bpy.app.handlers.frame_change_pre.remove(
                QuailHandlers.particle_seed_handler
            )
