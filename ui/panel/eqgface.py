# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
import os
import bmesh

from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty, EnumProperty

# Define property names for face attributes
FACE_PROPS = ["passable", "collisionrequired", "transparent", "culled", "degenerate"]

# Create custom data layers for face properties using the new attributes system
def ensure_face_layers(mesh):
    """Ensure all required face Boolean layers exist."""

    try:
        if mesh.is_editmode:
            bm = bmesh.from_edit_mesh(mesh)

            for prop_name in FACE_PROPS:
                layer_name = f"quail_{prop_name}"

                if bm.faces.layers.bool.get(layer_name) is None:
                    bm.faces.layers.bool.new(layer_name)

            bmesh.update_edit_mesh(
                mesh,
                loop_triangles=False,
                destructive=False,
            )

        else:
            for prop_name in FACE_PROPS:
                layer_name = f"quail_{prop_name}"

                if layer_name not in mesh.attributes:
                    mesh.attributes.new(
                        name=layer_name,
                        type='BOOLEAN',
                        domain='FACE',
                    )

    except Exception as e:
        print(f"Error in ensure_face_layers: {e}")

# Helper functions to get/set face properties
def get_face_property(mesh, face_index, prop_name):
    """Read a Boolean face property in either Edit or Object Mode."""

    try:
        layer_name = f"quail_{prop_name}"

        if mesh.is_editmode:
            bm = bmesh.from_edit_mesh(mesh)
            bm.faces.ensure_lookup_table()

            layer = bm.faces.layers.bool.get(layer_name)

            if layer is None:
                return False

            if 0 <= face_index < len(bm.faces):
                return bool(bm.faces[face_index][layer])

            return False

        attribute = mesh.attributes.get(layer_name)

        if (
            attribute is not None
            and 0 <= face_index < len(attribute.data)
        ):
            return bool(attribute.data[face_index].value)

        return False

    except Exception as e:
        print(
            f"Error in get_face_property "
            f"(prop={prop_name}, face={face_index}): {e}"
        )
        return False

def set_face_property(mesh, face_index, prop_name, value):
    """Write a Boolean face property in either Edit or Object Mode."""

    try:
        layer_name = f"quail_{prop_name}"

        if mesh.is_editmode:
            bm = bmesh.from_edit_mesh(mesh)
            bm.faces.ensure_lookup_table()

            layer = bm.faces.layers.bool.get(layer_name)

            if layer is None:
                layer = bm.faces.layers.bool.new(layer_name)

            if 0 <= face_index < len(bm.faces):
                bm.faces[face_index][layer] = bool(value)

                bmesh.update_edit_mesh(
                    mesh,
                    loop_triangles=False,
                    destructive=False,
                )

            return

        attribute = mesh.attributes.get(layer_name)

        if attribute is None:
            attribute = mesh.attributes.new(
                name=layer_name,
                type='BOOLEAN',
                domain='FACE',
            )

        if 0 <= face_index < len(attribute.data):
            attribute.data[face_index].value = bool(value)
            mesh.update()

    except Exception as e:
        print(
            f"Error in set_face_property "
            f"(prop={prop_name}, face={face_index}, "
            f"value={value}): {e}"
        )

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

# Register classes
def register():
    try:
        ## bpy.utils.register_class(QuailEqgFaceProperties)
        ## bpy.utils.register_class(MESH_OT_quail_update_face_property)
        bpy.types.Scene.quail_temp_face_props = PointerProperty(type=QuailEqgFaceProperties)
    except Exception as e:
        print(f"Error registering EQGFace panel: {e}")

def unregister():
    try:
        if hasattr(bpy.types.Scene, "quail_temp_face_props"):
            del bpy.types.Scene.quail_temp_face_props
        ## bpy.utils.unregister_class(MESH_OT_quail_update_face_property)
        ## bpy.utils.unregister_class(QuailEqgFaceProperties)
    except Exception as e:
        print(f"Error unregistering EQGFace panel: {e}")