import statistics
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
    new_step = (sleep / 1000.0) * fps

    if action.get("quail_tracks_snapped"):

        if new_step < 1.0:
            new_step = 1
        else:
            new_step = max(
                1,
                int(round(new_step))
            )

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