# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
import statistics
from bpy.props import StringProperty, FloatProperty, FloatVectorProperty,BoolProperty, PointerProperty, IntProperty, EnumProperty, CollectionProperty
from bpy_extras import anim_utils
from ...common.animation import update_sleep


class QuailTrackProperties(bpy.types.PropertyGroup):

    tag: StringProperty(name="DAG")

    track: StringProperty(name="Tag")

    interpolate: BoolProperty(name="Interpolate", default=False)
    reverse: BoolProperty(name="Reverse", default=False)

    has_sleep: BoolProperty(name="Has Sleep", default=False)
    sleep: IntProperty(name="Sleep", default=0, update=update_sleep)

    numframes: IntProperty(name="Num Frames", default=1)

class POSE_OT_add_default_quail_track(bpy.types.Operator):

    bl_idname = "pose.add_default_quail_track"
    bl_label = "Set Quail Track"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        obj = context.object

        return (
            obj and
            obj.type == 'ARMATURE' and
            context.active_pose_bone and
            obj.animation_data and
            obj.animation_data.action
        )

    def execute(self, context):

        obj = context.object
        bone = context.active_pose_bone
        action = obj.animation_data.action

        if not action.slots:

            action.fcurve_ensure_for_datablock(
                obj,
                f'pose.bones["{bone.name}"].location',
                index=0
            )

        slot = action.slots[0]

        channelbag = anim_utils.action_ensure_channelbag_for_slot(
            action,
            slot
        )

        # ----------------------------------------
        # Ensure group exists
        # ----------------------------------------

        group = channelbag.groups.get(bone.name)

        if not group:
            group = channelbag.groups.new(name=bone.name)

        # ----------------------------------------
        # Already initialized?
        # ----------------------------------------

        for t in action.quail_tracks:

            if t.tag == bone.name:

                self.report(
                    {'INFO'},
                    "Track already exists"
                )

                return {'CANCELLED'}

        # ----------------------------------------
        # Collect frame positions
        # ----------------------------------------

        frames = set()

        for fcurve in group.channels:

            for kp in fcurve.keyframe_points:
                frames.add(kp.co.x)

        frames = sorted(frames)

        # ----------------------------------------
        # Create default track props
        # ----------------------------------------

        track = action.quail_tracks.add()

        track.tag = bone.name

        # ----------------------------------------
        # Reconstruct track tag
        # ----------------------------------------

        action_name = action.name

        base_name = bone.name

        # AVIHE_DAG.001 -> AVIHE_TRACK.001
        if "DAG." in base_name:

            base_name = base_name.replace(
                "DAG.",
                "TRACK."
            )

        # AVIHE_DAG -> AVIHE_TRACK
        elif base_name.endswith("_DAG"):

            base_name = (
                base_name[:-4] +
                "_TRACK"
            )

        else:

            base_name = (
                f"{base_name}_TRACK"
            )

        if action_name.startswith("POS_"):

            track.track = base_name

        else:

            parts = action_name.split("_", 1)

            if len(parts) == 2:

                ani_prefix = parts[0]

                # remove TRACK before prefixing
                if "TRACK." in base_name:

                    track.track = (
                        f"{ani_prefix}" +
                        base_name
                    )

                elif base_name.endswith("_TRACK"):

                    track.track = (
                        f"{ani_prefix}" +
                        base_name
                    )

                else:

                    track.track = (
                        f"{ani_prefix}{base_name}"
                    )

            else:

                track.track = base_name

        track.interpolate = False
        track.reverse = False

        track.numframes = len(frames)

        # ----------------------------------------
        # Infer sleep
        # ----------------------------------------

        if len(frames) > 1:

            deltas = []

            for i in range(1, len(frames)):

                delta = frames[i] - frames[i - 1]

                if delta > 0.0001:
                    deltas.append(delta)

            if deltas:

                try:
                    base_step = statistics.median(deltas)
                except:
                    base_step = min(deltas)

                fps = context.scene.render.fps

                track.has_sleep = True

                # Match update_sleep behavior
                track.sleep = int(
                    round((base_step / fps) * 1000.0)
                )

            else:

                track.has_sleep = False
                track.sleep = 0

        else:

            track.has_sleep = False
            track.sleep = 0

        action["quaildef"] = "track"

        self.report(
            {'INFO'},
            f"Initialized Quail Track for {bone.name}"
        )

        return {'FINISHED'}

class QUAIL_PT_track_panel(bpy.types.Panel):
    bl_label = "Quail Track"
    bl_space_type = 'DOPESHEET_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'Quail'

    @classmethod
    def poll(cls, context):
        obj = context.object

        if not obj or obj.type != 'ARMATURE':
            return False

        anim_data = obj.animation_data
        if not anim_data or not anim_data.action:
            return False

        action = anim_data.action

        # Ensure there is at least one slot
        if not action.slots:
            return False

        return True

    def draw(self, context):
        layout = self.layout

        obj = context.object
        bone = context.active_pose_bone

        if not obj or not obj.animation_data:
            return

        action = obj.animation_data.action
        if not action or not action.slots:
            return

        slot = action.slots[0]

        from bpy_extras import anim_utils
        channelbag = anim_utils.action_ensure_channelbag_for_slot(action, slot)

        # ----------------------------------------
        # Resolve group (bone OR fallback)
        # ----------------------------------------

        group = None

        if bone:
            group = channelbag.groups.get(bone.name)

        if not group and channelbag.groups:
            group = channelbag.groups[0]

        if not group:
            layout.label(text="No track selected")
            return

        # ----------------------------------------
        # Track props (READ ONLY)
        # ----------------------------------------

        track = None
        for t in action.quail_tracks:
            if t.tag == group.name:
                track = t
                break

        if not track:

            layout.operator(
                "pose.add_default_quail_track",
                text="Set Quail Track"
            )

            return

        # ----------------------------------------
        # DAG (sync with group name)
        # ----------------------------------------

        layout.prop(group, "name", text="DAG")
        layout.prop(track, "track", text="Tag")

        # ----------------------------------------
        # Track properties
        # ----------------------------------------

        box = layout.box()
        box.label(text="Track Properties")

        box.prop(track, "interpolate")
        box.prop(track, "reverse")

        row = box.row(align=True)
        row.prop(track, "has_sleep", text="")
        sub = row.row()
        sub.enabled = track.has_sleep
        sub.prop(track, "sleep", text="Sleep")

        # ----------------------------------------
        # Derived
        # ----------------------------------------

        layout.separator()

        num_frames = self.get_num_frames(group)
        layout.label(text=f"Num Frames: {num_frames}")

    def get_num_frames(self, group):
        if not group:
            return 0

        frame_set = set()

        for fcurve in group.channels:  # <-- IMPORTANT: groups use .channels, not .fcurves
            for kp in fcurve.keyframe_points:
                frame_set.add(kp.co.x)

        return len(frame_set)

def register():
    bpy.types.Action.quail_tracks = CollectionProperty(type=QuailTrackProperties)
    bpy.types.Action.quail_active_track = IntProperty(default=-1)


def unregister():
    del bpy.types.Action.quail_tracks
    del bpy.types.Action.quail_active_track