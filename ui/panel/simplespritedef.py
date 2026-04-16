# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
import os
from bpy.props import StringProperty, FloatProperty, FloatVectorProperty, BoolProperty, PointerProperty, IntProperty, EnumProperty, CollectionProperty
from ...decoder.simplespritedef import add_texture_animation
from ...common import state

def update_has_sleep(self, context):
    tree = self.id_data

    if not tree or tree.get("quaildef") != "simplespritedef":
        return

    if self.has_sleep:
        add_texture_animation(tree)
    else:
        nodes = tree.nodes
        links = tree.links

        # ----------------------------------------
        # 1. Remove TEXANIM node
        # ----------------------------------------
        for n in list(nodes):
            if n.get("texanim_node"):
                nodes.remove(n)

        # ----------------------------------------
        # 2. Find first frame node (frame_id == 0)
        # ----------------------------------------
        first_frame_node = None
        for n in nodes:
            if n.get("frame_id") == 0:
                first_frame_node = n
                break

        # ----------------------------------------
        # 3. Reconnect to output
        # ----------------------------------------
        output = next((n for n in nodes if n.type == "GROUP_OUTPUT"), None)

        if output and first_frame_node:
            # Remove existing links to output
            for l in list(links):
                if l.to_node == output:
                    links.remove(l)

            # Reconnect first frame
            links.new(first_frame_node.outputs["Color"], output.inputs["sRGB Texture"])
            links.new(first_frame_node.outputs["Alpha"], output.inputs["Alpha"])

def update_frame_file_image(self, context):

    if state.QUAIL_UPDATING:
        return

    # print("UPDATE CALLED")
    tree = self.id_data
    props = tree.quail_simplesprite

    # 🔹 find parent frame
    frame = None
    for f in props.frames:
        for f2 in f.files:
            if f2 == self:
                frame = f
                break
        if frame:
            break

    if not frame or not frame.frame_node:
        return

    frame_group = frame.frame_node

    # 🔹 match node by index
    for n in frame_group.nodes:
        if n.type == 'TEX_IMAGE' and n.get("file_index") == self.file_index:
            n.image = self.image
            break

    # Rebuild anim if needed
    props = tree.quail_simplesprite
    if props.has_sleep:
        add_texture_animation(tree)

def update_frame_name(self, context):
    if state.QUAIL_UPDATING:
        return

    tree = self.id_data
    if not tree or tree.get("quaildef") != "simplespritedef":
        return

    new_name = self.frame_name

    # ----------------------------------------
    # 1. Mirror into Blender name (optional)
    # ----------------------------------------
    self.name = new_name

    # ----------------------------------------
    # 2. Rename node group (picker field)
    # ----------------------------------------
    if self.frame_node:
        self.frame_node.name = new_name

    # ----------------------------------------
    # 3. Rename node instance
    # ----------------------------------------
    for n in tree.nodes:
        if n.type == 'GROUP' and n.node_tree == self.frame_node:
            n.name = new_name
            n.label = new_name
            break

def update_frame_node(self, context):

    if state.QUAIL_UPDATING:
        return

    tree = self.id_data

    # --- your existing logic below ---
    if self.frame_node:
        self.frame_name = self.frame_node.name
    else:
        self.name = "Frame"

    nodes = tree.nodes
    links = tree.links

    node = None
    for n in nodes:
        if n.get("frame_id") == self.frame_id:
            node = n
            break

    if not node:
        node = nodes.new("ShaderNodeGroup")
        node["frame_id"] = self.frame_id

    node.node_tree = self.frame_node

    # -----------------------------------
    # Sync panel data FROM frame nodegroup
    # -----------------------------------
    if self.frame_node:
        node.name = self.frame_node.name
        node.label = self.frame_node.name

        # Collect image nodes inside the group
        image_nodes = [
            n for n in self.frame_node.nodes
            if n.type == 'TEX_IMAGE' and n.image
        ]

        # Update numfiles (this will resize collection)
        self.numfiles = len(image_nodes)

        # Now populate files
        for i, img_node in enumerate(image_nodes):
            file = self.files[i]

            file.image = img_node.image

            # Infer mode (basic version)
            if i == 0:
                file.texture_mode = 'BASE'
            else:
                mode = self.frame_node.get("mode")

                if mode == "DETAIL" and i == 1:
                    file.texture_mode = 'DETAIL'
                elif mode == "LAYER" and i == 1:
                    file.texture_mode = 'LAYER'
                elif mode == "PALETTE":
                    if i == 1:
                        file.texture_mode = 'PALETTE'
                    else:
                        file.texture_mode = 'TILED'
                else:
                    file.texture_mode = 'TILED'

    index = list(tree.quail_simplesprite.frames).index(self)
    node.location = (0, -200 * index)

    for socket in node.inputs:
        socket.hide = True

    if index == 0:
        # Connect to output
        output = next((n for n in nodes if n.type == "GROUP_OUTPUT"), None)
        if output and self.frame_node:
            for l in list(links):
                if l.to_node == output:
                    links.remove(l)

            links.new(node.outputs["Color"], output.inputs["sRGB Texture"])
            links.new(node.outputs["Alpha"], output.inputs["Alpha"])

    # -----------------------------------
    # Always update TEXANIM after changes
    # -----------------------------------
    props = tree.quail_simplesprite
    if props.has_sleep:
        add_texture_animation(tree)

def update_simplesprite_node(self, context):
    print("Updated simplesprite:", self.name)

def sync_numframes(self, context):
    target = self.numframes
    frames = self.frames

    # -----------------------------
    # Add frames
    # -----------------------------
    while len(frames) < target:
        frame = frames.add()
        frame.frame_name = f"Frame_{len(frames)}"
        frame.frame_id = len(frames) - 1

    # -----------------------------
    # Remove frames
    # -----------------------------
    while len(frames) > target:
        frames.remove(len(frames) - 1)

    # -----------------------------
    # Clamp active index
    # -----------------------------
    if self.active_frame >= len(frames):
        self.active_frame = max(0, len(frames) - 1)

    # ==================================================
    # Remove norphaned nodes
    # ==================================================
    tree = self.id_data
    nodes = tree.nodes

    valid_ids = {i for i in range(len(frames))}

    for n in list(nodes):
        if "frame_id" in n:
            if n["frame_id"] not in valid_ids:
                nodes.remove(n)

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

    file_index: IntProperty()

    raw_string: StringProperty()

    image: PointerProperty(
        type=bpy.types.Image,
        update=update_frame_file_image
    )

    texture_mode: EnumProperty(
        items=[
            ('BASE', 'Base', ''),
            ('LAYER', 'Layer', ''),
            ('DETAIL', 'Detail', ''),
            ('PALETTE', 'Palette', ''),
            ('TILED', 'Tiled', ''),
        ],
        default='BASE'
    )

    palette_index: IntProperty(default=0)
    scale: FloatProperty(default=1.0)
    blend: FloatProperty(default=0.0)

class QuailSimpleSpriteFrame(bpy.types.PropertyGroup):

    frame_name: StringProperty(
        name="Frame Name",
        update=update_frame_name
    )

    frame_id: IntProperty(default=-1)

    frame_node: PointerProperty(
        name="Frame Node",
        type=bpy.types.NodeTree,
        poll=lambda self, nt: nt.get("quaildef") == "simplesprite_frame",
        update=update_frame_node
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
        default=0
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
        default=False,
        update=update_has_sleep
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
        default=0
    )

class QUAIL_UL_frames(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        frame = item

        row = layout.row(align=True)

        row.prop(frame, "frame_name", text="", emboss=False, icon='NONE')

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
            "QUAIL_UL_frames",
            "",
            props,
            "frames",
            props,
            "active_frame"
        )

        # Active frame detail
        if props.frames and props.active_frame < len(props.frames):
            frame = props.frames[props.active_frame]

            box = layout.box()
            box.prop(frame, "frame_node")

            # ---- NUMFILES FIELD ----
            box.prop(frame, "numfiles")

            box.separator()
            box.label(text="Files")

            # ---- FILE LIST ----
            if frame.files:
                for i, file in enumerate(frame.files):

                    file_box = box.box()
                    file_box.prop(file, "image")

                    # FILE 0 — BASE
                    if i == 0:
                        file_box.label(text="Mode: BASE")

                    # FILE 1 — LAYER / DETAIL / PALETTE
                    elif i == 1:
                        row = file_box.row(align=True)
                        row.prop_enum(file, "texture_mode", "LAYER")
                        row.prop_enum(file, "texture_mode", "DETAIL")
                        row.prop_enum(file, "texture_mode", "PALETTE")

                        if file.texture_mode == 'DETAIL':
                            file_box.prop(file, "scale")

                    # FILE 2+ — TILED
                    else:
                        file_box.label(text=f"Tiled Index: {i-1}")
                        file_box.prop(file, "scale")
                        file_box.prop(file, "blend")

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