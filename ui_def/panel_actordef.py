# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
import os
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty

# Define Actor properties
class QuailActorDefProperties(bpy.types.PropertyGroup):
    currentaction: StringProperty(
        name="Action",
        description="Current Action",
        default=""
    )

    boundsref: IntProperty(
        name="BoundsRef",
        description="Bounds reference",
        default=1
    )

    callback: StringProperty(
        name="Callback",
        description="Callback function for the actor",
        default=""
    )

    activegeometry: StringProperty(
        name="Geometry",
        description="Active Geometry",
        default=""
    )

    collider: BoolProperty(
        name="Collider",
        description="Use Model Collider",
        default=False
    )

    userdata: StringProperty(
        name="User Data",
        description="User Data",
        default=""
    )

class OBJECT_OT_add_custom_empty(bpy.types.Operator):
    """Create a new ActorDef"""
    bl_idname = "object.add_custom_actor"
    bl_label = "ActorDef"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create an Empty
        obj = bpy.data.objects.new("Actor", None)

        # Set transformation
        obj.location = context.scene.cursor.location

        obj.empty_display_type = 'SINGLE_ARROW'

        # Add custom property to identify this as an actor
        obj['quaildef'] = 'actordef'


        # Link to collection
        context.collection.objects.link(obj)

        # Set active object
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        return {'FINISHED'}

# Panel to display actor properties
class PROPERTIES_PT_quail_actordef(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"  # This puts it in the Object Properties panel
    bl_label = "ACTORDEF"
    # bl_options = {'DEFAULT_CLOSED'}
    bl_order = -100

    @classmethod
    def poll(cls, context):
        # Only show this panel when an actor is selected
        return context.object and context.object.get('quaildef') == 'actordef'

    def draw(self, context):
        pass


# Create a new Quail menu class
class VIEW3D_MT_quail_add(bpy.types.Menu):
    bl_idname = "VIEW3D_MT_quail_add"
    bl_label = "Quail"

    def draw(self, context):
        layout = self.layout
        layout.operator(OBJECT_OT_add_custom_empty.bl_idname, icon='IMAGE_DATA')
        # Add other Quail related operators here

# Function to add the Quail menu to the Add menu
def add_quail_menu(self, context):
    self.layout.menu(VIEW3D_MT_quail_add.bl_idname, icon='GHOST_ENABLED')


def draw_actordef_in_transform(self, context):
    obj = context.object
    if obj and obj.get('quaildef') == 'actordef':
        layout = self.layout
        box = layout.box()
        box.label(text="ACTORDEF")
        row = box.row()
        row.prop(obj.quail_actordef, "currentaction")

        row = box.row()
        row.prop(obj.quail_actordef, "boundsref")

        row = box.row()
        row.prop(obj.quail_actordef, "callback")

        row = box.row()
        row.prop(obj.quail_actordef, "activegeometry")

        row = box.row()
        row.prop(obj.quail_actordef, "collider")

        row = box.row()
        row.prop(obj.quail_actordef, "userdata")

# Register classes
def register():
    # ignored, auto_load bpy.utils.register_class(QuailActorDefProperties)
    # ignored, auto_load bpy.utils.register_class(OBJECT_OT_add_custom_empty)
    # ignored, auto_load bpy.utils.register_class(VIEW3D_MT_quail_add)
    # ignored, auto_load bpy.utils.register_class(PROPERTIES_PT_quail_actor)
    bpy.types.Object.quail_actordef = PointerProperty(type=QuailActorDefProperties)
    bpy.types.VIEW3D_MT_add.append(add_quail_menu)
    bpy.types.OBJECT_PT_transform.prepend(draw_actordef_in_transform)

def unregister():
    bpy.types.VIEW3D_MT_add.remove(add_quail_menu)
    del bpy.types.Object.quail_actordef
    bpy.types.OBJECT_PT_transform.remove(draw_actordef_in_transform)
    # ignored, auto_load bpy.utils.unregister_class(PROPERTIES_PT_quail_actor)
    # ignored, auto_load bpy.utils.unregister_class(VIEW3D_MT_quail_add)
    # ignored, auto_load bpy.utils.unregister_class(OBJECT_OT_add_custom_empty)
    # ignored, auto_load bpy.utils.unregister_class(QuailActorDefProperties)