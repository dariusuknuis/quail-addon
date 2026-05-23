# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
import os
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator
from bpy.props import StringProperty, FloatProperty, FloatVectorProperty, BoolProperty, PointerProperty, IntProperty, EnumProperty, CollectionProperty
from ...decoder.simplespritedef import add_texture_animation, create_frame_nodegroup
from ...common import state
from ...common.image_loader import load_s3d_image

def ensure_frame_connected(tree, frame):
    nodes = tree.nodes
    links = tree.links

    node = next((n for n in nodes if n.get("frame_id") == frame.frame_id), None)
    output = next((n for n in nodes if n.type == "GROUP_OUTPUT"), None)

    if not node or not node.node_tree or not output:
        return

    # remove existing links to output
    for l in list(links):
        if l.to_node == output:
            links.remove(l)

    # reconnect
    links.new(node.outputs["Color"], output.inputs["sRGB Texture"])
    links.new(node.outputs["Alpha"], output.inputs["Alpha"])

def update_file_values(self, context):

    if state.QUAIL_UPDATING:
        return

    state.QUAIL_UPDATING = True

    tree = self.id_data
    props = tree.quail_simplesprite

    # find frame
    frame = next(
        (
            f for f in props.frames
            if any(file == self for file in f.files)
        ),
        None
    )
    if not frame:
        state.QUAIL_UPDATING = False
        return

    # find node instance
    node = next((n for n in tree.nodes if n.get("frame_id") == frame.frame_id), None)
    if not node or not node.node_tree:
        state.QUAIL_UPDATING = False
        return

    nt = node.node_tree

    # ------------------------------------------------
    # DETAIL
    # ------------------------------------------------
    if self.texture_mode == 'DETAIL':
        if "Detail Scale" in node.inputs:
            node.inputs["Detail Scale"].default_value = self.scale

    # ------------------------------------------------
    # TILED
    # ------------------------------------------------
    elif self.texture_mode == 'TILED':
        tiled_index = self.file_index - 1
        socket_name = f"Tiled {tiled_index} Scale"

        if socket_name in node.inputs:
            node.inputs[socket_name].default_value = self.scale

    state.QUAIL_UPDATING = False

def update_texture_mode(self, context):

    if state.QUAIL_UPDATING:
        return

    state.QUAIL_UPDATING = True

    tree = self.id_data
    props = tree.quail_simplesprite

    frame = None
    for f in props.frames:
        for f2 in f.files:
            if f2 == self:
                frame = f
                break
        if frame:
            break

    if not frame:
        state.QUAIL_UPDATING = False
        return

    new_group = create_frame_nodegroup(None, frame, tree.name, force_rebuild=True)
    frame.frame_node_name = new_group.name

    index = list(tree.quail_simplesprite.frames).index(frame)

    node = next((n for n in tree.nodes if n.get("frame_id") == frame.frame_id), None)
    if node:
        for socket in node.inputs:
            socket.hide = True

    if index == 0:
        ensure_frame_connected(tree, frame)

    if props.has_sleep:
        add_texture_animation(tree)

    if self.file_index >= 2 and self.texture_mode != 'TILED':
        self.texture_mode = 'TILED'
        self.palette_index = self.file_index - 1

    state.QUAIL_UPDATING = False

def update_frame_file_image(self, context):

    if state.QUAIL_UPDATING:
        return

    tree = self.id_data
    props = tree.quail_simplesprite

    frame = None
    for f in props.frames:
        for f2 in f.files:
            if f2 == self:
                frame = f
                break
        if frame:
            break

    if not frame:
        return

    state.QUAIL_UPDATING = True

    new_group = create_frame_nodegroup(None, frame, tree.name, force_rebuild=True)
    frame.frame_node_name = new_group.name

    state.QUAIL_UPDATING = False

    index = list(tree.quail_simplesprite.frames).index(frame)

    node = None
    for n in tree.nodes:
        if n.get("frame_id") == frame.frame_id:
            node = n
            break

    if node:
        for socket in node.inputs:
            socket.hide = True

    if index == 0:
        ensure_frame_connected(tree, frame)

    if props.has_sleep:
        add_texture_animation(tree)

    if self.file_index >= 2 and self.texture_mode != 'TILED':
        self.texture_mode = 'TILED'
        self.palette_index = self.file_index - 1

def update_frame_node(self, context):

    if state.QUAIL_UPDATING:
        return

    state.QUAIL_UPDATING = True

    tree = self.id_data
    props = tree.quail_simplesprite

    node_tree = bpy.data.node_groups.get(self.frame_node_name)

    if node_tree:
        self.frame_name = node_tree.name
    else:
        self.frame_name = "Frame"

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

    node.node_tree = node_tree

    # -----------------------------------
    # Sync panel data FROM frame nodegroup
    # -----------------------------------
    if node_tree:
        node.name = node_tree.name
        node.label = node_tree.name

        # Collect image nodes inside the group
        image_nodes = [
            n for n in node_tree.nodes
            if n.type == 'TEX_IMAGE'
        ]

        # Update numfiles (this will resize collection)
        self.numfiles = len(image_nodes)

        # Now populate files
        for i, img_node in enumerate(image_nodes):
            file = self.files[i]

            file.image_name = img_node.image.name if img_node.image else ""

            # Infer mode (basic version)
            if i == 0:
                file.texture_mode = 'BASE'
            else:
                mode = node_tree.get("mode")

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
        ensure_frame_connected(tree, self)

    if props.has_sleep:
        add_texture_animation(tree)

    state.QUAIL_UPDATING = False

def update_active_frame(self, context):

    if state.QUAIL_UPDATING:
        return

    state.QUAIL_UPDATING = True

    tree = self.id_data
    frame = self.frames[self.active_frame]

    node = next(
        (n for n in tree.nodes if n.get("frame_id") == frame.frame_id),
        None
    )

    if node and node.node_tree:
        frame.frame_node_name = node.node_tree.name

    state.QUAIL_UPDATING = False

def update_frame_name(self, context):
    if state.QUAIL_UPDATING:
        return

    state.QUAIL_UPDATING = True

    tree = self.id_data
    if not tree or tree.get("quaildef") != "simplespritedef":
        state.QUAIL_UPDATING = False
        return

    new_name = self.frame_name

    self.name = new_name

    node_tree = bpy.data.node_groups.get(self.frame_node_name)

    if node_tree:
        node_tree.name = new_name
        self.frame_node_name = node_tree.name

    for n in tree.nodes:
        if n.type == 'GROUP' and n.node_tree == node_tree:
            n.name = new_name
            n.label = new_name
            break

    state.QUAIL_UPDATING = False

def update_has_sleep(self, context):
    if state.QUAIL_UPDATING:
        return

    state.QUAIL_UPDATING = True

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

    state.QUAIL_UPDATING = False

def update_simplesprite_node(self, context):
    print("Updated simplesprite:", self.name)

def update_numframes(self, context):
    if state.QUAIL_UPDATING:
        return
    target = self.numframes
    frames = self.frames

    # -----------------------------
    # Add frames
    # -----------------------------
    state.QUAIL_UPDATING = True

    while len(frames) < target:
        frame = frames.add()
        frame.frame_id = len(frames) - 1
        frame.frame_name = f"Frame_{frame.frame_id}"

    state.QUAIL_UPDATING = False
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

def update_numfiles(self, context):
    target = self.numfiles
    files = self.files

    while len(files) < target:
        files.add()

    while len(files) > target:
        files.remove(len(files) - 1)

    if self.active_file_index >= len(files):
        self.active_file_index = max(0, len(files) - 1)

    for i, f in enumerate(files):
        f.file_index = i

class QUAIL_OT_load_image(Operator, ImportHelper):
    bl_idname = "quail.load_image"
    bl_label = "Load Image"

    filename_ext = ".dds;.bmp;.png;.tga"
    filter_glob: bpy.props.StringProperty(
        default="*.dds;*.bmp;*.png;*.tga",
        options={'HIDDEN'}
    )

    # 👇 pass context info
    frame_index: bpy.props.IntProperty()
    file_index: bpy.props.IntProperty()

    def execute(self, context):

        tree = context.space_data.edit_tree
        props = tree.quail_simplesprite

        frame = props.frames[self.frame_index]
        file = frame.files[self.file_index]

        # Load image
        ctx = type("Ctx", (), {"parser": type("Parser", (), {"assets_path": os.path.dirname(self.filepath)})()})()

        filename = bpy.path.basename(self.filepath)

        img, err = load_s3d_image(ctx, filename)

        if err or not img:
            self.report({'ERROR'}, err or "Failed to load image")
            return {'CANCELLED'}

        # Assign
        file.image_name = img.name
        file.file_name = bpy.path.basename(self.filepath)

        return {'FINISHED'}

class QuailSimpleSpriteFrameFile(bpy.types.PropertyGroup):

    file_index: IntProperty()

    raw_string: StringProperty()

    file_name: StringProperty()

    image_name: bpy.props.StringProperty(
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
        default='BASE',
        update=update_texture_mode
    )

    palette_index: IntProperty(default=0)
    scale: FloatProperty(
        default=1.0,
        update=update_file_values
    )

    blend: FloatProperty(default=0.0)

class QuailSimpleSpriteFrame(bpy.types.PropertyGroup):

    frame_name: StringProperty(
        name="Frame Name",
        update=update_frame_name
    )

    frame_id: IntProperty(default=-1)

    def get_frame_nodes(self, context):
        return [
            (ng.name, ng.name, "")
            for ng in bpy.data.node_groups
            if ng.get("quaildef") == "simplesprite_frame"
        ]

    frame_node_name: EnumProperty(
        items=get_frame_nodes,
        update=update_frame_node
    )

    numfiles: IntProperty(
        name="Num Files",
        default=0,
        min=0,
        update=update_numfiles
    )

    files: CollectionProperty(
        type=QuailSimpleSpriteFrameFile
    )

    active_file_index: IntProperty(
        default=0
    )

class QuailSimpleSpriteProperties(bpy.types.PropertyGroup):

    variation: BoolProperty (
        name="Variation",
        default=False
    )

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
        update=update_numframes
    )

    frames: CollectionProperty(
        type=QuailSimpleSpriteFrame
    )

    active_frame: IntProperty(
        default=0,
        update=update_active_frame
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
            box.prop(frame, "frame_node_name")

            # ---- NUMFILES FIELD ----
            box.prop(frame, "numfiles")

            box.separator()
            box.label(text="Files")

            # ---- FILE LIST ----
            if frame.files:
                for i, file in enumerate(frame.files):

                    file_box = box.box()

                    row = file_box.row(align=True)
                    row.prop_search(
                        file,
                        "image_name",
                        bpy.data,
                        "images",
                        text="Image"
                    )

                    op = row.operator("quail.load_image", text="", icon='FILE_FOLDER')
                    op.frame_index = props.active_frame
                    op.file_index = i

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