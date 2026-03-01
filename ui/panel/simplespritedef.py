import bpy
import os
from bpy.props import StringProperty, FloatProperty, FloatVectorProperty, BoolProperty, PointerProperty, IntProperty, EnumProperty, CollectionProperty

def update_simplesprite_node(self, context):
    print("Updated simplesprite:", self.name)

def sync_numframes(self, context):
    target = self.quail_ss_numframes
    frames = self.quail_ss_frames

    # Add frames
    while len(frames) < target:
        frame = frames.add()
        frame.name = f"Frame_{len(frames)}"

    # Remove frames
    while len(frames) > target:
        frames.remove(len(frames) - 1)

    # Clamp active index
    if self.quail_ss_active_frame >= len(frames):
        self.quail_ss_active_frame = max(0, len(frames) - 1)

class QuailSpriteFrameFile(bpy.types.PropertyGroup):
    filename: bpy.props.StringProperty(name="File")


class QuailSpriteFrame(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Frame Name")
    files: bpy.props.CollectionProperty(type=QuailSpriteFrameFile)
    active_file_index: bpy.props.IntProperty(default=0)

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
        layout.prop(tree, "quail_ss_numframes")

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

    # Attach properties to NodeTree

    bpy.types.NodeTree.quail_ss_skipframes = bpy.props.BoolProperty(
        name="Skip Frames",
        default=False
    )

    bpy.types.NodeTree.quail_ss_sleep_enabled = bpy.props.BoolProperty(
        name="Use Sleep",
        default=False
    )

    bpy.types.NodeTree.quail_ss_sleep = bpy.props.IntProperty(
        name="Sleep",
        default=0,
        min=0
    )

    bpy.types.NodeTree.quail_ss_current_enabled = bpy.props.BoolProperty(
        name="Use Current Frame",
        default=False
    )

    bpy.types.NodeTree.quail_ss_current = bpy.props.IntProperty(
        name="Current Frame",
        default=0,
        min=0
    )

    bpy.types.NodeTree.quail_ss_numframes = bpy.props.IntProperty(
        name="Num Frames",
        default=0,
        min=0,
        update=sync_numframes
    )

    bpy.types.NodeTree.quail_ss_frames = bpy.props.CollectionProperty(
        type=QuailSpriteFrame
    )

    bpy.types.NodeTree.quail_ss_active_frame = bpy.props.IntProperty(default=0)


def unregister():

    if hasattr(bpy.types.NodeTree, "quail_ss_skipframes"):
        del bpy.types.NodeTree.quail_ss_skipframes
        del bpy.types.NodeTree.quail_ss_sleep_enabled
        del bpy.types.NodeTree.quail_ss_sleep
        del bpy.types.NodeTree.quail_ss_current_enabled
        del bpy.types.NodeTree.quail_ss_current
        del bpy.types.NodeTree.quail_ss_frames
        del bpy.types.NodeTree.quail_ss_active_frame