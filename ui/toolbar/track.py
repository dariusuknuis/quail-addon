import bpy
from bpy.types import Operator
from bpy_extras import anim_utils
from ...common.animation import update_sleep


class VIEW3D_PT_quail_track_tools(bpy.types.Panel):

    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Quail"
    bl_label = "Track Tools"

    @classmethod
    def poll(cls, context):

        obj = context.object

        if not obj:
            return False

        if obj.type != 'ARMATURE':
            return False

        if not obj.animation_data:
            return False

        if not obj.animation_data.action:
            return False

        return True

    def draw(self, context):

        layout = self.layout

        action = context.object.animation_data.action

        # ----------------------------------------
        # Visual snapped indicator
        # ----------------------------------------

        if action.get("quail_tracks_snapped"):

            box = layout.box()

            row = box.row()

            row.alert = True

            row.label(
                text="Tracks Snapped",
                icon='SNAP_ON'
            )

        # ----------------------------------------
        # Toggle operator
        # ----------------------------------------

        layout.operator(
            "quail.snap_track_frames",
            icon='SNAP_ON',
        )


class QUAIL_OT_snap_track_frames(Operator):

    bl_idname = "quail.snap_track_frames"
    bl_label = "Snap Track Frames"
    bl_description = (
        "Toggle snapping selected track "
        "keyframes to scene frame intervals"
    )

    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        obj = context.object
        if not obj:
            return False

        if obj.type != 'ARMATURE':
            return False

        if not obj.animation_data:
            return False

        if not obj.animation_data.action:
            return False

        return True

    def execute(self, context):
        obj = context.object
        action = obj.animation_data.action
        if not action.slots:
            self.report(
                {'WARNING'},
                "Action has no slots"
            )

            return {'CANCELLED'}

        slot = action.slots[0]
        channelbag = anim_utils.action_ensure_channelbag_for_slot(
            action,
            slot
        )

        for fcurve in channelbag.fcurves:
            has_selected_keys = False
            for kp in fcurve.keyframe_points:
                if (
                    kp.select_control_point or
                    kp.select_left_handle or
                    kp.select_right_handle
                ):
                    has_selected_keys = True
                    break

            if not has_selected_keys:
                continue

            fcurve.select = True
            data_path = fcurve.data_path
            if 'pose.bones["' in data_path:
                bone_name = (
                    data_path
                    .split('pose.bones["')[1]
                    .split('"]')[0]
                )

                group = channelbag.groups.get(bone_name)
                if group:
                    group.select = True

        # TOGGLE OFF
        if action.get("quail_tracks_snapped"):
            del action["quail_tracks_snapped"]
            restored = 0
            for group in channelbag.groups:
                selected = False
                for fcurve in group.channels:
                    if fcurve.select:
                        selected = True
                        break

                if not selected:
                    continue

                track_props = None
                for t in action.quail_tracks:
                    if t.tag == group.name:
                        track_props = t
                        break

                if not track_props:
                    continue

                if not track_props.has_sleep:
                    continue

                update_sleep(track_props, context)
                restored += 1

            self.report(
                {'INFO'},
                f"Restored {restored} track(s)"
            )

            return {'FINISHED'}

        # TOGGLE ON
        processed = 0
        for group in channelbag.groups:
            selected = False
            for fcurve in group.channels:
                if fcurve.select:
                    selected = True
                    break

            if not selected:
                continue

            frames = set()
            for fcurve in group.channels:
                for kp in fcurve.keyframe_points:
                    frames.add(kp.co.x)

            frames = sorted(frames)
            if len(frames) < 2:
                continue

            raw_step = frames[1] - frames[0]
            if raw_step <= 0.0001:
                continue

            if raw_step < 1.0:
                snapped_step = 1
            else:
                snapped_step = max(
                    1,
                    int(round(raw_step))
                )

            start = round(frames[0])
            for fcurve in group.channels:
                for kp in fcurve.keyframe_points:
                    i = round(
                        (kp.co.x - frames[0]) / raw_step
                    )

                    new_frame = (
                        start +
                        (i * snapped_step)
                    )

                    kp.co.x = new_frame
                    kp.handle_left.x = new_frame
                    kp.handle_right.x = new_frame
                fcurve.update()
            processed += 1

        if processed > 0:
            action["quail_tracks_snapped"] = True

        self.report(
            {'INFO'},
            f"Snapped {processed} track(s)"
        )

        return {'FINISHED'}