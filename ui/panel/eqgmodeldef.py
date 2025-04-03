# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
import bmesh
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty, EnumProperty
from .eqgface import ensure_face_layers, get_face_property, set_face_property, FACE_PROPS, QuailEqgFaceProperties

class QuailEqgModelDefProperties(bpy.types.PropertyGroup):
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

class OBJECT_OT_add_quail_eqgmodeldef(bpy.types.Operator):
    """Create a new EqgModelDef"""
    bl_idname = "object.add_quail_eqgmodeldef"
    bl_label = "EqgModelDef"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # Create an Empty
        obj = bpy.data.objects.new("EqgModelDef", bpy.data.meshes.new("EqgModelDefMesh"))
        bpy.ops.object.mode_set(mode='OBJECT')

        # Add custom property to identify this as an actor
        obj['quaildef'] = 'eqgmodeldef'

        # Link to collection
        context.collection.objects.link(obj)

        # Set active object
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        return {'FINISHED'}

# Panel to display actor properties
class PROPERTIES_PT_quail_eqgmodeldef(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"  # This puts it in the Object Properties panel
    bl_label = "EQGMODELDEF"
    # bl_options = {'DEFAULT_CLOSED'}
    bl_order = -100

    @classmethod
    def poll(cls, context):
        return context.object and context.object.get('quaildef') == 'eqgmodeldef'

    def draw(self, context):
        pass

def draw_eqgmodeldef_in_transform(self, context):
    obj = context.object
    if not obj:
        return
    if obj.get('quaildef') != 'eqgmodeldef':
        return

    layout = self.layout
    box = layout.box()
    box.label(text="EQGMODELDEF")
    row = box.row()
    row.prop(obj.quail_eqgmodeldef, "version")

    if context.mode != 'EDIT_MESH':
        return

    mesh = obj.data
    try:
        # This might fail if mesh is corrupted
        ensure_face_layers(mesh)

        bm = bmesh.from_edit_mesh(mesh)
        selected_faces = [f for f in bm.faces if f.select]

        if len(selected_faces) != 1:
            return

        face = selected_faces[0]
        face_index = face.index

        # Create a temporary property group once during registration
        scene = context.scene

        # Draw UI for face attributes
        box = layout.box()
        box.label(text=f"Face Properties ({face_index})")

        # Use custom UI elements for boolean properties
        for prop_name in FACE_PROPS:
            prop_value = get_face_property(mesh, face_index, prop_name)
            row = box.row()

            # Create a checkbox-like button
            icon = 'CHECKBOX_HLT' if prop_value else 'CHECKBOX_DEHLT'
            op = row.operator("mesh.quail_toggle_face_property", text=prop_name, icon=icon)
            op.face_index = face_index
            op.prop_name = prop_name
            op.new_value = not prop_value  # Toggle value when clicked

    except Exception as e:
        layout = self.layout
        row = box.row()
        row.label(text=f"Error processing face data: {e}")

class MESH_OT_quail_toggle_face_property(bpy.types.Operator):
    """Toggle face property value"""
    bl_idname = "mesh.quail_toggle_face_property"
    bl_label = "Toggle Face Property"
    bl_options = {'REGISTER', 'UNDO'}

    face_index: IntProperty(default=-1)
    prop_name: StringProperty(default="")
    new_value: BoolProperty(default=False)

    def execute(self, context):
        try:
            obj = context.object
            if not obj or not obj.data or self.face_index < 0 or not self.prop_name:
                return {'CANCELLED'}

            # Set property in mesh attribute
            mesh = obj.data
            set_face_property(mesh, self.face_index, self.prop_name, self.new_value)

            # Force a redraw to update the UI
            context.area.tag_redraw()

            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error toggling face property: {e}")
            return {'CANCELLED'}

# Register classes
def register():
    # ignored, auto_load bpy.utils.register_class(QuailActorDefProperties)
    # ignored, auto_load bpy.utils.register_class(OBJECT_OT_add_custom_empty)
    # ignored, auto_load bpy.utils.register_class(VIEW3D_MT_quail_add)
    # ignored, auto_load bpy.utils.register_class(PROPERTIES_PT_quail_actor)
    #bpy.utils.register_class(MESH_OT_quail_toggle_face_property)
    if not hasattr(bpy.types.OBJECT_PT_transform, "_quail_registered"):
        bpy.types.OBJECT_PT_transform.prepend(draw_eqgmodeldef_in_transform)
        # Set a flag to track registration
        setattr(bpy.types.OBJECT_PT_transform, "_quail_registered", True)

    if not hasattr(bpy.types.Object, 'quail_eqgmodeldef'):
        bpy.types.Object.quail_eqgmodeldef = PointerProperty(type=QuailEqgModelDefProperties)


def unregister():
    if hasattr(bpy.types.Object, 'quail_eqgmodeldef'):
        del bpy.types.Object.quail_eqgmodeldef

    if hasattr(bpy.types.OBJECT_PT_transform, "_quail_registered"):
        delattr(bpy.types.OBJECT_PT_transform, "_quail_registered")
        bpy.types.OBJECT_PT_transform._draw_funcs_prepend.remove(draw_eqgmodeldef_in_transform)
    #bpy.utils.unregister_class(MESH_OT_quail_toggle_face_property)
    # ignored, auto_load bpy.utils.unregister_class(PROPERTIES_PT_quail_actor)
    # ignored, auto_load bpy.utils.unregister_class(VIEW3D_MT_quail_add)
    # ignored, auto_load bpy.utils.unregister_class(OBJECT_OT_add_custom_empty)
    # ignored, auto_load bpy.utils.unregister_class(QuailActorDefProperties)