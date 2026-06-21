import bpy
import sys


class VIEW3D_PT_quail_hs_sync(bpy.types.Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Quail"
    bl_label = "Sync HierarchicalSprite"

    @classmethod
    def poll(cls, context):

        obj = context.object

        if not obj:
            return False

        if obj.type != 'ARMATURE':
            return False

        return obj.get("quaildef") == "hierarchicalspritedef"

    def draw(self, context):

        layout = self.layout

        layout.operator(
            "quail.sync_hierarchicalsprite",
            icon='FILE_REFRESH',
        )

class QUAIL_OT_sync_hierarchicalsprite(bpy.types.Operator):
    bl_idname = "quail.sync_hierarchicalsprite"
    bl_label = "Sync HierarchicalSprite"

    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        obj = context.object

        if not obj:
            return False

        if obj.type != 'ARMATURE':
            return False

        return obj.get("quaildef") == "hierarchicalspritedef"

    def execute(self, context):

        handlers_mod = sys.modules["quail-addon.handlers"]

        handlers_mod.sync_panel_from_armature(
            context.object
        )

        self.report(
            {'INFO'},
            "HierarchicalSprite synchronized"
        )

        return {'FINISHED'}