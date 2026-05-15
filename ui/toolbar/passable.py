# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import bmesh

VALID_QUAILDEFS = {
    "dmspritedef2",
}

# --------------------------------------------------------
# Helpers
# --------------------------------------------------------

def _supported_object(obj):

    if not obj:
        return False

    if obj.type != 'MESH':
        return False

    if obj.get("quaildef") not in VALID_QUAILDEFS:
        return False

    return True


def _bm_get_layer(me: bpy.types.Mesh):
    """
    Return (bm, layer) for PASSABLE face int layer in EDIT mode.
    Creates attribute if missing.
    """

    bm = bmesh.from_edit_mesh(me)

    layer = bm.faces.layers.int.get("PASSABLE")

    if layer is None:
        layer = bm.faces.layers.int.new("PASSABLE")

    return bm, layer


# --------------------------------------------------------
# Selected Face Checkbox
# --------------------------------------------------------

def _obj_get_passable_selected(obj):

    me = getattr(obj, "data", None)

    if not me:
        return False

    if obj.mode != 'EDIT':
        return False

    sel_mode = bpy.context.tool_settings.mesh_select_mode

    if not sel_mode[2]:
        return False

    bm, layer = _bm_get_layer(me)

    faces = [f for f in bm.faces if f.select]

    if not faces:
        return False

    return all(int(f[layer]) == 1 for f in faces)


def _obj_set_passable_selected(obj, value):

    me = getattr(obj, "data", None)

    if not me:
        return

    if obj.mode != 'EDIT':
        return

    sel_mode = bpy.context.tool_settings.mesh_select_mode

    if not sel_mode[2]:
        return

    bm, layer = _bm_get_layer(me)

    v = 1 if value else 0

    changed = False

    for f in bm.faces:

        if not f.select:
            continue

        f[layer] = v
        changed = True

    if changed:
        bmesh.update_edit_mesh(
            me,
            loop_triangles=False,
            destructive=False
        )


# --------------------------------------------------------
# Object Property
# --------------------------------------------------------

def _register_object_prop():

    if hasattr(bpy.types.Object, "passable_selected"):
        return

    bpy.types.Object.passable_selected = bpy.props.BoolProperty(
        name="Passable",
        description="Set PASSABLE on selected faces",
        get=_obj_get_passable_selected,
        set=_obj_set_passable_selected,
    )


def _unregister_object_prop():

    if hasattr(bpy.types.Object, "passable_selected"):
        del bpy.types.Object.passable_selected


# --------------------------------------------------------
# Scene Property
# --------------------------------------------------------

def _register_scene_flag():

    if hasattr(bpy.types.Scene, "passable_display_enabled"):
        return

    bpy.types.Scene.passable_display_enabled = bpy.props.BoolProperty(
        name="Passable Display",
        description="Show passable face overlay",
        default=False,
    )


def _unregister_scene_flag():

    if hasattr(bpy.types.Scene, "passable_display_enabled"):
        del bpy.types.Scene.passable_display_enabled


# --------------------------------------------------------
# Ensure Attribute
# --------------------------------------------------------

class MESH_OT_ensure_passable_attribute(bpy.types.Operator):

    bl_idname = "mesh.ensure_passable_attribute"
    bl_label = "Create PASSABLE Attribute"

    @classmethod
    def poll(cls, context):

        obj = context.object

        return _supported_object(obj)

    def execute(self, context):

        obj = context.object
        mesh = obj.data

        if mesh.attributes.get("PASSABLE") is None:

            mesh.attributes.new(
                name="PASSABLE",
                type='INT',
                domain='FACE'
            )

        self.report({'INFO'}, "PASSABLE attribute ensured")

        return {'FINISHED'}


# --------------------------------------------------------
# Toggle Display
# --------------------------------------------------------

class MESH_OT_toggle_passable_viewport(bpy.types.Operator):

    bl_idname = "mesh.toggle_passable_viewport"
    bl_label = "Toggle Passable Display"

    def execute(self, context):

        scene = context.scene

        scene.passable_display_enabled = (
            not scene.passable_display_enabled
        )

        state = "ON" if scene.passable_display_enabled else "OFF"

        self.report({'INFO'}, f"Passable display: {state}")

        return {'FINISHED'}


# --------------------------------------------------------
# Main Panel
# --------------------------------------------------------

class VIEW3D_PT_quail_passable(bpy.types.Panel):

    bl_label = "Passable"
    bl_idname = "VIEW3D_PT_quail_passable"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Quail"

    @classmethod
    def poll(cls, context):

        obj = context.object

        return _supported_object(obj)

    def draw(self, context):

        layout = self.layout

        scene = context.scene
        obj = context.object

        # ------------------------------------------------
        # Global Display Toggle
        # ------------------------------------------------

        row = layout.row(align=True)

        row.prop(
            scene,
            "passable_display_enabled",
            text="Display"
        )

        row.operator(
            "mesh.toggle_passable_viewport",
            text="",
            icon='HIDE_OFF'
        )

        # ------------------------------------------------
        # Face Edit Tools
        # ------------------------------------------------

        if obj.mode != 'EDIT':
            return

        sel_mode = context.tool_settings.mesh_select_mode

        if not sel_mode[2]:
            return

        layout.separator()

        if obj.data.attributes.get("PASSABLE") is None:

            layout.operator(
                "mesh.ensure_passable_attribute",
                icon='ADD'
            )

            return

        layout.prop(
            obj,
            "passable_selected",
            text="Selected Faces Passable"
        )


# --------------------------------------------------------
# Registration
# --------------------------------------------------------

def register():

    _register_object_prop()
    _register_scene_flag()


def unregister():

    _unregister_object_prop()
    _unregister_scene_flag()