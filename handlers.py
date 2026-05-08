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

        # ----------------------------------------
        # STEP 1: Ensure DAG count matches bones
        # ----------------------------------------
        while len(props.dags) < len(bones):
            props.dags.add()

        while len(props.dags) > len(bones):
            props.dags.remove(len(props.dags) - 1)

        # ----------------------------------------
        # STEP 2: Update tags from bones (preserve data)
        # ----------------------------------------
        for i, bone in enumerate(bones):
            dag = props.dags[i]

            if dag.tag != bone.name:
                dag.tag = bone.name

        # ----------------------------------------
        # STEP 3: Clear subdags
        # ----------------------------------------
        for dag in props.dags:
            while len(dag.subdags) > 0:
                dag.subdags.remove(0)

        # ----------------------------------------
        # STEP 4: Build index lookup
        # ----------------------------------------
        name_to_index = {bone.name: i for i, bone in enumerate(bones)}

        # ----------------------------------------
        # STEP 5: Rebuild relationships
        # ----------------------------------------
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

        arm = obj.data

        for update in depsgraph.updates:

            if update.id.original not in {obj, arm}:
                continue

            sync_panel_from_armature(obj)
            break

    @staticmethod
    def particle_seed_handler(scene):

        if scene.frame_current != 1:
            return

        for obj in bpy.data.objects:

            if obj.get("quaildef") != "particleclouddef":
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
