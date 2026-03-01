# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
import os
from bpy.props import StringProperty, FloatProperty, FloatVectorProperty, BoolProperty, PointerProperty, IntProperty, EnumProperty, CollectionProperty

def update_simplesprite_node(self, context):
    print("Updated simplesprite:", self.name)

def sync_numframes(self, context):
    target = self.numframes
    frames = self.frames

    # Add frames
    while len(frames) < target:
        frame = frames.add()
        frame.name = f"Frame_{len(frames)}"

    # Remove frames
    while len(frames) > target:
        frames.remove(len(frames) - 1)

    # Clamp active index
    if self.active_frame >= len(frames):
        self.active_frame = max(0, len(frames) - 1)

def sync_numfiles(self, context):
    target = self.numfiles
    files = self.files

    while len(files) < target:
        files.add()

    while len(files) > target:
        files.remove(len(files) - 1)

    if self.active_file_index >= len(files):
        self.active_file_index = max(0, len(files) - 1)

class QuailSimpleSpriteFrameFile(bpy.types.PropertyGroup):

    filename: bpy.props.StringProperty(
        name="File"
    )


class QuailSimpleSpriteFrame(bpy.types.PropertyGroup):

    name: StringProperty(
        name="Frame Name"
    )

    numfiles: IntProperty(
        name="Num Files",
        default=0,
        min=0,
        update=sync_numfiles
    )

    files: CollectionProperty(
        type=QuailSimpleSpriteFrameFile
    )

    active_file_index: IntProperty(
        default=1
    )

class QuailSimpleSpriteProperties(bpy.types.PropertyGroup):

    skipframes: BoolProperty(
        name="Skip Frames",
        description="Flag for Skip Frames",
        default=False
    )

    has_sleep: BoolProperty(
        name="Has Sleep",
        description="If not set, Sleep is NULL",
        default=False
    )

    sleep: IntProperty(
        name="Sleep",
        description="Time, in milliseconds, between frames",
        default=0,
        min=0
    )

    has_current_frame: BoolProperty(
        name="Has Current Frame",
        description="If not set, Current Frame is NULL",
        default=False
    )

    current_frame: IntProperty(
        name="Current Frame",
        description="Sets Current Frame?",
        default=0,
        min=0
    )

    numframes: IntProperty(
        name="Num Frames",
        description="Number of frames for an animated texture",
        default=0,
        min=0,
        update=sync_numframes
    )

    frames: CollectionProperty(
        type=QuailSimpleSpriteFrame
    )

    active_frame: IntProperty(
        default=1
    )

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
        tree = context.space_data.edit_tree
        layout = self.layout
        props = tree.quail_simplesprite

        layout.prop(props, "skipframes")

        self.draw_optional(layout, props,
                           "Sleep",
                           "has_sleep",
                           "sleep")

        self.draw_optional(layout, props,
                           "Current Frame",
                           "has_current_frame",
                           "current_frame")
        layout.prop(props, "numframes")

        layout.separator()
        layout.label(text="Frames")

        layout.template_list(
            "UI_UL_list",
            "QUAIL_UL_frames",
            props,
            "frames",
            props,
            "active_frame"
        )

        row = layout.row()
        row.operator("quail.add_frame", icon="ADD")
        row.operator("quail.remove_frame", icon="REMOVE")

        # Active frame detail
        if props.frames and props.active_frame < len(props.frames):
            frame = props.frames[props.active_frame]

            box = layout.box()
            box.prop(frame, "name")

            # ---- NUMFILES FIELD ----
            box.prop(frame, "numfiles")

            box.separator()
            box.label(text="Files")

            # ---- FILE LIST ----
            if frame.files:
                for file in frame.files:
                    box.prop(file, "filename")

    def draw_optional(self, layout, props, label, toggle, value):
        row = layout.row(align=True)
        row.prop(props, toggle, text="")
        sub = row.row()
        sub.enabled = getattr(props, toggle)
        sub.prop(props, value, text=label)

def register():

    bpy.types.NodeTree.quail_simplesprite = PointerProperty(
        type=QuailSimpleSpriteProperties)


def unregister():

    del bpy.types.NodeTree.quail_simplesprite