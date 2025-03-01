import bpy
import os
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty

image_path = "pawn.svg"

def load_custom_image():
    """Load custom image into Blender."""
    if image_path and os.path.exists(image_path):
        image = bpy.data.images.load(image_path, check_existing=True)
        return image.name
    print(f"Image not found: {image_path}")
    return None

# Callback function for string property
def update_actor_name(self, context):
    # This function will be called whenever the actor_name property is changed
    print(f"Actor name changed to: {self.actor_name}")
    # Update the object name to match
    if context.object:
        context.object.name = self.actor_name

# Define Actor properties
class QuailActorProperties(bpy.types.PropertyGroup):
    actor_name: StringProperty(
        name="Actor Name",
        description="Name of the actor",
        default="Actor",
        update=update_actor_name
    )

    actor_type: StringProperty(
        name="Actor Type",
        description="Type of the actor (NPC, Player, etc.)",
        default="NPC"
    )

    callback_script: StringProperty(
        name="Callback Script",
        description="Script to call when this actor is activated",
        default=""
    )

class OBJECT_OT_add_custom_empty(bpy.types.Operator):
    """Add a custom Empty type called 'Actor' with a custom image"""
    bl_idname = "object.add_custom_actor"
    bl_label = "Actor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create an Empty
        obj = bpy.data.objects.new("Actor", None)

        # Set transformation
        obj.location = context.scene.cursor.location

        # Use the Empty display type as IMAGE
        obj.empty_display_type = 'IMAGE'

        # Load custom image and assign it
        image_name = load_custom_image()
        if image_name:
            obj.data = bpy.data.images.get(image_name)

        # Add custom property to identify this as an actor
        obj['is_quail_actor'] = True

        # Initialize the actor properties
        if obj.get('actor_props') is None:
            obj['actor_props'] = {}

        # Link to collection
        context.collection.objects.link(obj)

        # Set active object
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        return {'FINISHED'}

# Panel to display actor properties
class PROPERTIES_PT_quail_actor(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"  # This puts it in the Object Properties panel
    bl_label = "Quail Actor Properties"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        # Only show this panel when an actor is selected
        return context.object and context.object.get('is_quail_actor')

    def draw(self, context):
        layout = self.layout
        obj = context.object

        # Access actor properties
        box = layout.box()
        row = box.row()
        row.prop(context.scene.quail_actor_props, "actor_name")

        row = box.row()
        row.prop(context.scene.quail_actor_props, "actor_type")

        row = box.row()
        row.prop(context.scene.quail_actor_props, "callback_script")

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
    self.layout.menu(VIEW3D_MT_quail_add.bl_idname, icon='PLUGIN')

# Register classes
def register():
    # ignored, auto_load bpy.utils.register_class(QuailActorProperties)
    # ignored, auto_load bpy.utils.register_class(OBJECT_OT_add_custom_empty)
    # ignored, auto_load bpy.utils.register_class(VIEW3D_MT_quail_add)
    # ignored, auto_load bpy.utils.register_class(PROPERTIES_PT_quail_actor)
    bpy.types.Scene.quail_actor_props = PointerProperty(type=QuailActorProperties)
    bpy.types.VIEW3D_MT_add.append(add_quail_menu)

def unregister():
    bpy.types.VIEW3D_MT_add.remove(add_quail_menu)
    del bpy.types.Scene.quail_actor_props
    # ignored, auto_load bpy.utils.unregister_class(PROPERTIES_PT_quail_actor)
    # ignored, auto_load bpy.utils.unregister_class(VIEW3D_MT_quail_add)
    # ignored, auto_load bpy.utils.unregister_class(OBJECT_OT_add_custom_empty)
    # ignored, auto_load bpy.utils.unregister_class(QuailActorProperties)