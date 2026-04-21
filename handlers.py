import bpy
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
        # STEP 1: map existing DAGs by tag
        # ----------------------------------------
        existing = {d.tag: d for d in props.dags}

        # ----------------------------------------
        # STEP 2: rebuild DAG list WITHOUT losing data
        # ----------------------------------------
        new_dags = []

        for bone in bones:
            if bone.name in existing:
                d = existing[bone.name]  # reuse existing
            else:
                d = props.dags.add()
                d.tag = bone.name
                d.spritetag = ""
                d.track = ""

            new_dags.append(d)

        # ----------------------------------------
        # STEP 3: remove DAGs that no longer exist
        # ----------------------------------------
        bone_names = {b.name for b in bones}

        i = 0
        while i < len(props.dags):
            if props.dags[i].tag not in bone_names:
                props.dags.remove(i)
            else:
                i += 1

        # ----------------------------------------
        # STEP 4: rebuild lookup
        # ----------------------------------------
        tag_to_index = {d.tag: i for i, d in enumerate(props.dags)}

        # ----------------------------------------
        # STEP 5: clear subdags
        # ----------------------------------------
        for dag in props.dags:
            while len(dag.subdags) > 0:
                dag.subdags.remove(0)

        # ----------------------------------------
        # STEP 6: rebuild relationships
        # ----------------------------------------
        for bone in bones:
            if not bone.parent:
                continue

            parent = bone.parent.name
            child = bone.name

            if parent not in tag_to_index or child not in tag_to_index:
                continue

            p_idx = tag_to_index[parent]
            c_idx = tag_to_index[child]

            item = props.dags[p_idx].subdags.add()
            item.dag_index = c_idx

        print("[HS SYNC] Panel updated (preserving data)")

    finally:
        state.QUAIL_UPDATING = False

class QuailHandlers:
    _last_mode = None
    @staticmethod
    @bpy.app.handlers.persistent
    def load_handler(_):
        pass
    def depsgraph_handler(scene, depsgraph):

        obj = bpy.context.object
        if not obj:
            return

        if obj.type != 'ARMATURE':
            return

        if obj.get("quaildef") != "hierarchicalspritedef":
            return

        current_mode = obj.mode

        # 🔥 ONLY when exiting edit mode
        if QuailHandlers._last_mode == 'EDIT' and current_mode == 'OBJECT':
            sync_panel_from_armature(obj)

        QuailHandlers._last_mode = current_mode


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

    @staticmethod
    def unregister():
        bpy.app.handlers.save_pre.remove(QuailHandlers.save_pre_handler)
        bpy.app.handlers.load_post.remove(QuailHandlers.load_handler)
        if QuailHandlers.depsgraph_handler in bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.remove(QuailHandlers.depsgraph_handler)
