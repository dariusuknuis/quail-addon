# decoder/dmtrackdef2.py

import bpy
from ..wce.dmtrackdef2 import dmtrackdef2
from .context import Context


def decode_dmtrackdef2(ctx:Context, obj, dmtrack:dmtrackdef2) -> str:

    if obj is None:
        return "no object provided for DMTRACKDEF2"

    if obj.type != 'MESH':
        return f"{obj.name}: DMTRACKDEF2 target is not a mesh"

    if obj.get("quaildef") != "dmspritedef2":
        return f"{obj.name}: DMTRACKDEF2 target is not dmspritedef2"

    mesh = obj.data

    if not dmtrack:
        return f"{obj.name}: no DMTRACKDEF2 provided"

    if len(dmtrack.frames) == 0:
        print(f"{obj.name}: DMTRACKDEF2 has no frames: {dmtrack.tag}")
        return ""

    vertex_count = len(mesh.vertices)

    # ------------------------------------------------
    # Shape key setup
    # ------------------------------------------------

    if mesh.shape_keys is None:
        obj.shape_key_add(name="Basis", from_mix=False)

    key_data = mesh.shape_keys
    key_data.use_relative = True

    # Only custom property
    key_data["quaildef"] = "dmtrackdef2"

    # ------------------------------------------------
    # Populate DMTRACKDEF2 property group on Key datablock
    # ------------------------------------------------

    props = key_data.quail_dmtrackdef2

    props.tag = dmtrack.tag
    props.sleep = dmtrack.sleep
    props.param2 = dmtrack.param2
    props.fpscale = dmtrack.fpscale
    props.size6 = dmtrack.size6
    props.numframes = len(dmtrack.frames)

    # ------------------------------------------------
    # Remove existing shape keys for this track if re-running
    # ------------------------------------------------

    for key in list(key_data.key_blocks):
        if key.name.startswith(dmtrack.tag + "_"):
            obj.shape_key_remove(key)

    shape_keys = []

    # ------------------------------------------------
    # Create shape keys from DMTRACKDEF2 frames
    # ------------------------------------------------

    for frame_index, frame in enumerate(dmtrack.frames):

        key_name = f"FRAME {frame_index + 1:03d}"

        shape_key = obj.shape_key_add(
            name=key_name,
            from_mix=False
        )

        frame_vertices = frame.vertices

        if len(frame_vertices) != vertex_count:
            print(
                f"{obj.name}: {dmtrack.tag} frame {frame_index + 1} "
                f"vertex count mismatch: mesh={vertex_count}, "
                f"track={len(frame_vertices)}"
            )

        count = min(vertex_count, len(frame_vertices))

        for i in range(count):
            shape_key.data[i].co = frame_vertices[i].xyz

        shape_keys.append(shape_key)

    # ------------------------------------------------
    # Animate shape key values
    # ------------------------------------------------

    fps = bpy.context.scene.render.fps

    sleep = dmtrack.sleep
    if sleep <= 0:
        sleep = 1000

    frames_per_sleep = (sleep / 1000.0) * fps
    if frames_per_sleep <= 0:
        frames_per_sleep = 1.0

    if key_data.animation_data:
        key_data.animation_data_clear()

    key_data.animation_data_create()

    action = bpy.data.actions.new(name=dmtrack.tag)
    key_data.animation_data.action = action

    current_frame = 1.0

    for active_key in shape_keys:

        for key in shape_keys:
            key.value = 0.0
            key.keyframe_insert(
                data_path="value",
                frame=current_frame
            )

        active_key.value = 1.0
        active_key.keyframe_insert(
            data_path="value",
            frame=current_frame
        )

        current_frame += frames_per_sleep

    return ""