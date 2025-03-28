# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
import os
import bmesh

from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty, EnumProperty

# Define property names for face attributes
FACE_PROPS = ["passable", "collisionrequired", "transparent", "culled", "degenerate"]

# Create custom data layers for face properties using the new attributes system
def ensure_face_layers(mesh):
    """Ensure all required face property layers exist on the mesh"""
    try:
        for prop_name in FACE_PROPS:
            layer_name = f"quail_{prop_name}"
            if layer_name not in mesh.attributes:
                attr = mesh.attributes.new(name=layer_name, type='BOOLEAN', domain='FACE')
                # Initialize all faces to False
                for i in range(len(mesh.polygons)):
                    attr.data[i].value = False
    except Exception as e:
        print(f"Error in ensure_face_layers: {e}")

# Helper functions to get/set face properties
def get_face_property(mesh, face_index, prop_name):
    """Get boolean face property from attribute layer"""
    try:
        layer_name = f"quail_{prop_name}"
        if layer_name in mesh.attributes:
            # Check if face index is in range
            if 0 <= face_index < len(mesh.attributes[layer_name].data):
                return mesh.attributes[layer_name].data[face_index].value
        return False
    except Exception as e:
        print(f"Error in get_face_property (prop={prop_name}, face={face_index}): {e}")
        return False

def set_face_property(mesh, face_index, prop_name, value):
    """Set boolean face property in attribute layer"""
    try:
        layer_name = f"quail_{prop_name}"

        # Create attribute if it doesn't exist
        if layer_name not in mesh.attributes:
            attr = mesh.attributes.new(name=layer_name, type='BOOLEAN', domain='FACE')
            # Initialize all faces to False first
            for i in range(len(mesh.polygons)):
                attr.data[i].value = False
        else:
            attr = mesh.attributes[layer_name]

        # Check if the face index is valid
        if 0 <= face_index < len(attr.data):
            attr.data[face_index].value = value
    except Exception as e:
        print(f"Error in set_face_property (prop={prop_name}, face={face_index}, value={value}): {e}")

class QuailEqgFaceProperties(bpy.types.PropertyGroup):
    """Properties for the current face in the UI"""
    passable: BoolProperty(
        name="Passable",
        description="Is this face passable?",
        default=False
    )

    collisionrequired: BoolProperty(
        name="Collision Required",
        description="Is collision required for this face?",
        default=False
    )

    transparent: BoolProperty(
        name="Transparent",
        description="Is this face transparent?",
        default=False
    )

    culled: BoolProperty(
        name="Culled",
        description="Is this face culled?",
        default=False
    )

    degenerate: BoolProperty(
        name="Degenerate",
        description="Is this face degenerate?",
        default=False
    )

def draw_eqgface_in_transform(self, context):
    """Draw UI for face properties"""
    try:
        obj = context.object
        if not obj:
            return

        if obj.get('quaildef') not in ('eqgmodeldef', 'eqgterdef'):
            return

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

            # Create temporary face properties in the scene
            scene = context.scene
            if not hasattr(scene, "quail_temp_face_props"):
                bpy.types.Scene.quail_temp_face_props = PointerProperty(type=QuailEqgFaceProperties)

            # Load properties from mesh attribute layers
            for prop_name in FACE_PROPS:
                value = get_face_property(mesh, face_index, prop_name)
                setattr(scene.quail_temp_face_props, prop_name, value)

            # Draw UI
            layout = self.layout
            box = layout.box()
            box.label(text="EQGFACE")

            for prop_name in FACE_PROPS:
                row = box.row()
                row.prop(scene.quail_temp_face_props, prop_name)

            # Add update button
            row = box.row()
            op = row.operator("mesh.quail_update_face_property", text="Apply")
            op.face_index = face_index

        except Exception as e:
            layout = self.layout
            box = layout.box()
            box.label(text=f"Error processing face data: {e}")

    except Exception as e:
        print(f"Error in draw_eqgface_in_transform: {e}")

class MESH_OT_quail_update_face_property(bpy.types.Operator):
    """Update face properties for the selected face"""
    bl_idname = "mesh.quail_update_face_property"
    bl_label = "Update Face Property"
    bl_options = {'REGISTER', 'UNDO'}

    face_index: IntProperty(default=-1)

    def execute(self, context):
        try:
            obj = context.object
            if not obj or not obj.data or self.face_index < 0:
                return {'CANCELLED'}

            # Store properties in mesh attributes
            mesh = obj.data
            ensure_face_layers(mesh)

            for prop_name in FACE_PROPS:
                value = getattr(context.scene.quail_temp_face_props, prop_name)
                set_face_property(mesh, self.face_index, prop_name, value)

            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error updating face property: {e}")
            return {'CANCELLED'}

# Update the decoder/eqgmodeldef.py code to use these functions
def decode_eqgmodeldef(ctx, eqgmodeldef, location):
    # ...existing code...

    mesh = bpy.data.meshes.new(eqgmodeldef.tag)
    # ...existing mesh creation code...

    # Ensure face property layers exist
    ensure_face_layers(mesh)

    # ...existing vertex/face creation...

    # When setting face properties
    for i, face in enumerate(eqgmodeldef.faces):
        poly = mesh.polygons[i]

        # Set material index
        if f"{eqgmodeldef.tag}_{face.material}" not in bpy.data.materials:
            return f"Material {eqgmodeldef.tag}_{face.material} not found"
        poly.material_index = bpy.data.materials.find(face.material)

        # Set face properties using custom layers
        set_face_property(mesh, i, "passable", face.passable)
        set_face_property(mesh, i, "collisionrequired", face.collisionrequired)
        set_face_property(mesh, i, "transparent", face.transparent)
        set_face_property(mesh, i, "culled", face.culled)
        set_face_property(mesh, i, "degenerate", face.degenerate)

# Register classes
def register():
    try:
        bpy.utils.register_class(QuailEqgFaceProperties)
        bpy.utils.register_class(MESH_OT_quail_update_face_property)
        bpy.types.Scene.quail_temp_face_props = PointerProperty(type=QuailEqgFaceProperties)
        bpy.types.OBJECT_PT_transform.prepend(draw_eqgface_in_transform)
        print("Successfully registered EQGFace panel")
    except Exception as e:
        print(f"Error registering EQGFace panel: {e}")

def unregister():
    try:
        bpy.types.OBJECT_PT_transform.remove(draw_eqgface_in_transform)
        if hasattr(bpy.types.Scene, "quail_temp_face_props"):
            del bpy.types.Scene.quail_temp_face_props
        bpy.utils.unregister_class(MESH_OT_quail_update_face_property)
        bpy.utils.unregister_class(QuailEqgFaceProperties)
        print("Successfully unregistered EQGFace panel")
    except Exception as e:
        print(f"Error unregistering EQGFace panel: {e}")