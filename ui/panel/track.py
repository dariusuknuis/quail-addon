# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
import statistics
from bpy.props import StringProperty, FloatProperty, FloatVectorProperty,BoolProperty, PointerProperty, IntProperty, EnumProperty, CollectionProperty
from bpy_extras import anim_utils

def update_sleep(self, context):
    obj = context.object
    if not obj or not obj.animation_data:
        return

    action = obj.animation_data.action
    if not action or not action.slots:
        return

    sleep = self.sleep
    if sleep <= 0:
        return

    fps = context.scene.render.fps
    new_step = max(1, (sleep / 1000.0) * fps)

    slot = action.slots[0]
    channelbag = anim_utils.action_ensure_channelbag_for_slot(action, slot)

    # ----------------------------------------
    # Find the group for this track
    # ----------------------------------------
    group = None
    for g in channelbag.groups:
        if g.name == self.tag:
            group = g
            break

    if not group:
        return

    # ----------------------------------------
    # Collect unique frame positions
    # ----------------------------------------
    frames = set()
    for fcurve in group.channels:
        for kp in fcurve.keyframe_points:
            frames.add(kp.co.x)

    if len(frames) < 2:
        return

    frames = sorted(frames)

    # ----------------------------------------
    # Compute deltas between frames
    # ----------------------------------------
    deltas = []
    for i in range(1, len(frames)):
        d = frames[i] - frames[i - 1]
        if d > 0.0001:  # ignore tiny float noise
            deltas.append(d)

    if not deltas:
        return

    # ----------------------------------------
    # Infer base step (robust)
    # ----------------------------------------
    try:
        base_step = statistics.median(deltas)
    except:
        base_step = min(deltas)

    if base_step <= 0:
        return

    # ----------------------------------------
    # Resnap keyframes to new spacing
    # ----------------------------------------
    start = frames[0]

    for fcurve in group.channels:
        for kp in fcurve.keyframe_points:

            # infer index
            i = round((kp.co.x - start) / base_step)

            # rebuild frame
            new_frame = start + i * new_step

            kp.co.x = new_frame
            kp.handle_left.x = new_frame
            kp.handle_right.x = new_frame

        fcurve.update()
class QuailTrackProperties(bpy.types.PropertyGroup):

    tag: StringProperty(name="DAG")

    track: StringProperty(name="Tag")

    interpolate: BoolProperty(name="Interpolate", default=False)
    reverse: BoolProperty(name="Reverse", default=False)

    has_sleep: BoolProperty(name="Has Sleep", default=False)
    sleep: IntProperty(name="Sleep", default=0, update=update_sleep)

    numframes: IntProperty(name="Num Frames", default=1)

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
            layout.label(text="Track not initialized")
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