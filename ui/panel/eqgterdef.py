# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy, bmesh
from bpy.props import PointerProperty, EnumProperty
from .eqgface import ensure_face_layers, get_face_property, FACE_PROPS

class QuailEqgTerDefProperties(bpy.types.PropertyGroup):
    version: EnumProperty(
        name="Version",
        description="Version of the Terrain Model",
        items=[
            ('1', "1", "First version"),
            ('2', "2", "Second version"),
            ('3', "3", "Third version"),
            ('4', "4", "Fourth version"),
            ('5', "5", "Fifth version"),
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
    bl_context = "object"
    bl_label = "EQGTERDEF"
    bl_order = -100

    @classmethod
    def poll(cls, context):
        return context.object and context.object.get('quaildef') == 'eqgterdef'

    def draw(self, context):
        pass

def draw_eqgterdef_in_transform(self, context):
    obj = context.object

    if not obj:
        return

    if obj.get('quaildef') != 'eqgterdef':
        return

    if obj.type != 'MESH':
        return

    layout = self.layout

    box = layout.box()
    box.label(text="EQGTERDEF")

    row = box.row()
    row.prop(
        obj.quail_eqgterdef,
        "version"
    )

    if context.mode != 'EDIT_MESH':
        return

    mesh = obj.data

    try:
        ensure_face_layers(mesh)

        bm = bmesh.from_edit_mesh(mesh)
        bm.faces.ensure_lookup_table()
        bm.faces.index_update()

        selected_faces = [
            face
            for face in bm.faces
            if face.select
        ]

        if len(selected_faces) != 1:
            return

        face = selected_faces[0]
        face_index = face.index

        box = layout.box()
        box.label(
            text=f"Face Properties ({face_index})"
        )

        for prop_name in FACE_PROPS:
            prop_value = get_face_property(
                mesh,
                face_index,
                prop_name
            )

            row = box.row()

            icon = (
                'CHECKBOX_HLT'
                if prop_value
                else 'CHECKBOX_DEHLT'
            )

            op = row.operator(
                "mesh.quail_toggle_face_property",
                text=prop_name,
                icon=icon
            )

            op.face_index = face_index
            op.prop_name = prop_name
            op.new_value = not prop_value

    except Exception as e:
        box = layout.box()
        box.label(
            text=f"Error processing face data: {e}"
        )

# Register classes
def register():
    bpy.types.OBJECT_PT_transform.prepend(draw_eqgterdef_in_transform)
    bpy.types.Object.quail_eqgterdef = PointerProperty(type=QuailEqgTerDefProperties)

def unregister():
    del bpy.types.Object.quail_eqgterdef
    bpy.types.OBJECT_PT_transform.remove(draw_eqgterdef_in_transform)