# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
import os
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty, EnumProperty

class QuailEqgTerDefProperties(bpy.types.PropertyGroup):
    version: EnumProperty(
        name="Version",
        description="Version of the ActorDef",
        items=[
            ('1', "1", "First version"),
            ('2', "2", "Second version"),
            ('3', "3", "Third version"),
        ],
        default='1'
    )

class OBJECT_OT_add_quail_eqgterdef(bpy.types.Operator):
    """Create a new EqgTerDef"""
    bl_idname = "object.add_quail_eqgterdef"
    bl_label = "EqgTerDef"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # Create an Empty
        obj = bpy.data.objects.new("EqgTerDef", bpy.data.meshes.new("EqgTerDefMesh"))
        bpy.ops.object.mode_set(mode='OBJECT')

        # Add custom property to identify this as an actor
        obj['quaildef'] = 'eqgterdef'

        # Link to collection
        context.collection.objects.link(obj)

        # Set active object
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        return {'FINISHED'}

# Panel to display actor properties
class PROPERTIES_PT_quail_eqgterdef(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"  # This puts it in the Object Properties panel
    bl_label = "EQGTERDEF"
    # bl_options = {'DEFAULT_CLOSED'}
    bl_order = -100

    @classmethod
    def poll(cls, context):
        return context.object and context.object.get('quaildef') == 'eqgterdef'

    def draw(self, context):
        pass

def draw_eqgterdef_in_transform(self, context):
    obj = context.object
    if obj and obj.get('quaildef') == 'eqgterdef':
        layout = self.layout
        box = layout.box()
        box.label(text="EQGTERDEF")
        row = box.row()
        row.prop(obj.quail_eqgterdef, "version")

# Register classes
def register():
    # ignored, auto_load bpy.utils.register_class(QuailActorDefProperties)
    # ignored, auto_load bpy.utils.register_class(OBJECT_OT_add_custom_empty)
    # ignored, auto_load bpy.utils.register_class(VIEW3D_MT_quail_add)
    # ignored, auto_load bpy.utils.register_class(PROPERTIES_PT_quail_actor)
    bpy.types.OBJECT_PT_transform.prepend(draw_eqgterdef_in_transform)
    bpy.types.Object.quail_eqgterdef = PointerProperty(type=QuailEqgTerDefProperties)


def unregister():
    del bpy.types.Object.quail_eqgterdef
    bpy.types.OBJECT_PT_transform.remove(draw_eqgterdef_in_transform)
    # ignored, auto_load bpy.utils.unregister_class(PROPERTIES_PT_quail_actor)
    # ignored, auto_load bpy.utils.unregister_class(VIEW3D_MT_quail_add)
    # ignored, auto_load bpy.utils.unregister_class(OBJECT_OT_add_custom_empty)
    # ignored, auto_load bpy.utils.unregister_class(QuailActorDefProperties)