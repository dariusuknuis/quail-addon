# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy, statistics
from bpy.props import StringProperty, IntProperty, PointerProperty
from bpy_extras import anim_utils


def update_sleep(self, context):
    key_data = self.id_data

    if not key_data or key_data.get("quaildef") != "dmtrackdef2":
        return

    if not key_data.animation_data:
        return

    action = key_data.animation_data.action
    if not action:
        return

    sleep = self.sleep
    if sleep <= 0:
        return

    fps = context.scene.render.fps
    new_step = max(1, (sleep / 1000.0) * fps)

    # ----------------------------------------
    # Get fcurves from shape key action
    # ----------------------------------------
    fcurves = []

    if hasattr(action, "slots") and action.slots:
        slot = action.slots[0]
        channelbag = anim_utils.action_ensure_channelbag_for_slot(action, slot)
        fcurves = list(channelbag.fcurves) if hasattr(channelbag, "fcurves") else list(channelbag.channels)
    else:
        fcurves = list(action.fcurves)

    if not fcurves:
        return

    # ----------------------------------------
    # Collect unique frame positions
    # ----------------------------------------
    frames = set()

    for fcurve in fcurves:
        for kp in fcurve.keyframe_points:
            frames.add(kp.co.x)

    if len(frames) < 2:
        return

    frames = sorted(frames)

    # ----------------------------------------
    # Infer current spacing
    # ----------------------------------------
    deltas = []

    for i in range(1, len(frames)):
        d = frames[i] - frames[i - 1]
        if d > 0.0001:
            deltas.append(d)

    if not deltas:
        return

    try:
        base_step = statistics.median(deltas)
    except:
        base_step = min(deltas)

    if base_step <= 0:
        return

    start = frames[0]

    # ----------------------------------------
    # Resnap all shape key value keyframes
    # ----------------------------------------
    for fcurve in fcurves:
        for kp in fcurve.keyframe_points:
            index = round((kp.co.x - start) / base_step)
            new_frame = start + index * new_step

            kp.co.x = new_frame
            kp.handle_left.x = new_frame
            kp.handle_right.x = new_frame

        fcurve.update()

class QUAIL_OT_dmtrackdef2_add_frame(bpy.types.Operator):
    bl_idname = "quail.dmtrackdef2_add_frame"
    bl_label = "Add DMTRACKDEF2 Frame"

    def execute(self, context):
        obj = context.object

        if not obj or obj.type != 'MESH':
            return {'CANCELLED'}

        key_data = obj.data.shape_keys

        if not key_data or key_data.get("quaildef") != "dmtrackdef2":
            return {'CANCELLED'}

        props = key_data.quail_dmtrackdef2

        key_data.animation_data_create()

        if not key_data.animation_data.action:
            key_data.animation_data.action = bpy.data.actions.new(name=props.tag)

        shape_keys = [
            key for key in key_data.key_blocks
            if key.name != "Basis"
        ]

        new_index = len(shape_keys) + 1
        key_name = f"FRAME {new_index:03d}"

        new_key = obj.shape_key_add(
            name=key_name,
            from_mix=False
        )

        shape_keys.append(new_key)

        fps = context.scene.render.fps

        sleep = props.sleep
        if sleep <= 0:
            sleep = 1000

        frame_step = max(1, (sleep / 1000.0) * fps)

        if props.numframes <= 0:
            new_frame = 1
        else:
            new_frame = 1 + (props.numframes * frame_step)

        action = key_data.animation_data.action

        if hasattr(action, "slots") and action.slots:
            slot = action.slots[0]
            channelbag = anim_utils.action_ensure_channelbag_for_slot(action, slot)
            fcurves = list(channelbag.fcurves) if hasattr(channelbag, "fcurves") else list(channelbag.channels)
        else:
            fcurves = list(action.fcurves)

        existing_frames = []

        for fcurve in fcurves:
            for kp in fcurve.keyframe_points:
                existing_frames.append(kp.co.x)

        existing_frames = sorted(set(existing_frames))

        # New key should be OFF for all existing frames
        for frame in existing_frames:
            new_key.value = 0.0
            new_key.keyframe_insert(
                data_path="value",
                frame=frame
            )

        # At the new frame, all keys are OFF first
        for key in shape_keys:
            key.value = 0.0
            key.keyframe_insert(
                data_path="value",
                frame=new_frame
            )

        # Then the new key is ON
        new_key.value = 1.0
        new_key.keyframe_insert(
            data_path="value",
            frame=new_frame
        )

        # Force CONSTANT interpolation
        if hasattr(action, "slots") and action.slots:
            slot = action.slots[0]
            channelbag = anim_utils.action_ensure_channelbag_for_slot(action, slot)
            fcurves = list(channelbag.fcurves) if hasattr(channelbag, "fcurves") else list(channelbag.channels)
        else:
            fcurves = list(action.fcurves)

        for fcurve in fcurves:
            for kp in fcurve.keyframe_points:
                kp.interpolation = 'CONSTANT'
            fcurve.update()

        props.numframes = len(shape_keys)
        props.active_frame = props.numframes - 1

        obj.active_shape_key_index = len(key_data.key_blocks) - 1

        return {'FINISHED'}

class QUAIL_OT_dmtrackdef2_remove_frame(bpy.types.Operator):
    bl_idname = "quail.dmtrackdef2_remove_frame"
    bl_label = "Remove Selected DMTRACKDEF2 Frame"

    def execute(self, context):
        obj = context.object

        if not obj or obj.type != 'MESH':
            return {'CANCELLED'}

        key_data = obj.data.shape_keys

        if not key_data or key_data.get("quaildef") != "dmtrackdef2":
            return {'CANCELLED'}

        index = obj.active_shape_key_index

        if index <= 0 or index >= len(key_data.key_blocks):
            return {'CANCELLED'}

        shape_key = key_data.key_blocks[index]
        key_name = shape_key.name

        # ----------------------------------------
        # Remove FCurves for this shape key value
        # ----------------------------------------
        if key_data.animation_data and key_data.animation_data.action:
            action = key_data.animation_data.action

            data_path = f'key_blocks["{key_name}"].value'

            if hasattr(action, "slots") and action.slots:
                slot = action.slots[0]
                channelbag = anim_utils.action_ensure_channelbag_for_slot(action, slot)

                if hasattr(channelbag, "fcurves"):
                    for fcurve in list(channelbag.fcurves):
                        if fcurve.data_path == data_path:
                            channelbag.fcurves.remove(fcurve)
            else:
                for fcurve in list(action.fcurves):
                    if fcurve.data_path == data_path:
                        action.fcurves.remove(fcurve)

        # ----------------------------------------
        # Remove the actual shape key
        # ----------------------------------------
        obj.shape_key_remove(shape_key)

        props = key_data.quail_dmtrackdef2

        shape_keys = [
            key for key in key_data.key_blocks
            if key.name != "Basis"
        ]

        props.numframes = len(shape_keys)

        obj.active_shape_key_index = min(
            index,
            len(key_data.key_blocks) - 1
        )

        return {'FINISHED'}

class QuailDMTrackDef2Properties(bpy.types.PropertyGroup):

    tag: StringProperty(name="Tag", default="")

    sleep: IntProperty(name="Sleep", default=0, update=update_sleep)
    param2: IntProperty(name="Param2", default=0)
    size6: IntProperty(name="SIZE6", default=0)

    numframes: IntProperty(name="Num Frames", default=0)

    active_frame: IntProperty(name="Frame", default=0, min=0)


class QUAIL_PT_dmtrackdef2_data(bpy.types.Panel):

    bl_label = "DMTRACKDEF2"
    bl_idname = "QUAIL_PT_dmtrackdef2_data"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "data"

    @classmethod
    def poll(cls, context):
        obj = context.object

        if not obj or obj.type != 'MESH':
            return False

        if obj.get("quaildef") != "dmspritedef2":
            return False

        key_data = obj.data.shape_keys

        if not key_data:
            return False

        return key_data.get("quaildef") == "dmtrackdef2"

    def draw(self, context):
        layout = self.layout

        obj = context.object
        key_data = obj.data.shape_keys
        props = key_data.quail_dmtrackdef2

        box = layout.box()
        box.label(text="DMTRACKDEF2")

        box.prop(props, "tag")
        box.prop(props, "sleep")
        box.prop(props, "param2")
        box.prop(props, "size6")

        box.label(text=f"Frames: {props.numframes}")
        row = box.row(align=True)
        row.operator("quail.dmtrackdef2_add_frame", text="Add Frame", icon='ADD')
        row.operator("quail.dmtrackdef2_remove_frame", text="Remove Selected", icon='REMOVE')


def register():

    bpy.types.Key.quail_dmtrackdef2 = PointerProperty(
        type=QuailDMTrackDef2Properties
    )


def unregister():

    del bpy.types.Key.quail_dmtrackdef2