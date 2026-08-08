# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import BoolProperty, IntProperty, PointerProperty


class QuailEqgAniDefProperties(bpy.types.PropertyGroup):
    version: IntProperty(name="Version", default=1)
    strict: BoolProperty(name="Strict", default=False)


class DOPESHEET_PT_quail_eqganidef(bpy.types.Panel):
    bl_label = "EQGANIDEF"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Quail'

    @classmethod
    def poll(cls, context):
        obj = context.object

        if not obj or obj.type != 'ARMATURE':
            return False

        if obj.get("quaildef") != "eqgmodarmature":
            return False

        if not obj.animation_data or not obj.animation_data.action:
            return False

        return obj.animation_data.action.get("quaildef") == "eqganidef"

    def draw(self, context):
        action = context.object.animation_data.action
        props = action.quail_eqganidef

        layout = self.layout
        layout.prop(props, "version")
        layout.prop(props, "strict")


def register():
    if not hasattr(bpy.types.Action, "quail_eqganidef"):
        bpy.types.Action.quail_eqganidef = PointerProperty(type=QuailEqgAniDefProperties)


def unregister():
    if hasattr(bpy.types.Action, "quail_eqganidef"):
        del bpy.types.Action.quail_eqganidef