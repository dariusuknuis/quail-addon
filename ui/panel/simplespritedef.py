import bpy
import os
from bpy.props import StringProperty, FloatProperty, FloatVectorProperty,BoolProperty, PointerProperty, IntProperty, EnumProperty, CollectionProperty

def update_simplesprite_node(self, context):
    print("Updated simplesprite:", self.name)

def register_simplesprite_props():

    bpy.types.NodeTree.quail_ss_skipframes = BoolProperty(
        name="Skip Frames",
        default=False
    )

    bpy.types.NodeTree.quail_ss_sleep_enabled = BoolProperty(
        name="Use Sleep",
        default=False
    )

    bpy.types.NodeTree.quail_ss_sleep = IntProperty(
        name="Sleep",
        default=0,
        min=0
    )

    bpy.types.NodeTree.quail_ss_current_enabled = BoolProperty(
        name="Use Current Frame",
        default=False
    )

    bpy.types.NodeTree.quail_ss_current = IntProperty(
        name="Current Frame",
        default=0,
        min=0
    )

    bpy.types.NodeTree.quail_ss_frames = CollectionProperty(
        type=QuailSpriteFrame
    )

    bpy.types.NodeTree.quail_ss_active_frame = IntProperty(default=0)

class QuailSpriteFrameFile(bpy.types.PropertyGroup):
    filename: StringProperty(name="File")


class QuailSpriteFrame(bpy.types.PropertyGroup):
    name: StringProperty(name="Frame Name")

    files: CollectionProperty(type=QuailSpriteFrameFile)
    active_file_index: IntProperty(default=0)

class QUAIL_PT_simplesprite_nodepanel(bpy.types.Panel):
    bl_label = "SIMPLESPRITEDEF"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Quail'

    @classmethod
    def poll(cls, context):
        tree = context.space_data.edit_tree
        return tree and tree.get("quaildef") == "simplespritedef"

    def draw(self, context):
        layout = self.layout
        tree = context.space_data.edit_tree

        layout.label(text=f"Tag: {tree.name}")

        layout.prop(tree, "quail_ss_skipframes")

        self.draw_optional(layout, tree,
                           "Sleep",
                           "quail_ss_sleep_enabled",
                           "quail_ss_sleep")

        self.draw_optional(layout, tree,
                           "Current Frame",
                           "quail_ss_current_enabled",
                           "quail_ss_current")

        layout.separator()
        layout.label(text="Frames")

        layout.template_list(
            "UI_UL_list",
            "quail_ss_frames",
            tree,
            "quail_ss_frames",
            tree,
            "quail_ss_active_frame"
        )

        row = layout.row()
        row.operator("quail.add_frame", icon="ADD")
        row.operator("quail.remove_frame", icon="REMOVE")

        # Active frame detail
        if tree.quail_ss_frames and tree.quail_ss_active_frame < len(tree.quail_ss_frames):
            frame = tree.quail_ss_frames[tree.quail_ss_active_frame]

            box = layout.box()
            box.prop(frame, "name")

            box.label(text="Files")

            for file in frame.files:
                box.prop(file, "filename")

    def draw_optional(self, layout, tree, label, toggle, value):
        row = layout.row(align=True)
        row.prop(tree, toggle, text="")
        sub = row.row()
        sub.enabled = getattr(tree, toggle)
        sub.prop(tree, value, text=label)

def register():
    bpy.utils.register_class(QUAIL_PT_simplesprite_nodepanel)
    register_simplesprite_props()

def unregister():
    bpy.utils.unregister_class(QUAIL_PT_simplesprite_nodepanel)

    del bpy.types.NodeTree.quail_ss_frame
    del bpy.types.NodeTree.quail_ss_sleep
    del bpy.types.NodeTree.quail_ss_skip
