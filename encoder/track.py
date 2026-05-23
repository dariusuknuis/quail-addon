import bpy, re
import mathutils
from bpy_extras import anim_utils
from ..wce.track import track

regexAniPrefix = re.compile(r"^[CDLOPST](0[1-9]|[1-9][0-9])")

def encode_track(parser, actions, context) -> str:

    errors = []

    # ----------------------------------------
    # Iterate armatures
    # ----------------------------------------
    for action in actions:

        errors = []

        armature_obj = None

        # Extract model code from action name (POS_AVI, C05_AVI, etc.)
        parts = action.name.split("_")
        model_code = parts[-1] if len(parts) > 1 else None

        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and model_code and obj.name.startswith(model_code):
                armature_obj = obj
                break

        if not armature_obj:
            print(f"[SKIP] No armature for action {action.name}")
            continue

        if not action.slots:
            continue

        slot = action.slots[0]
        channelbag = anim_utils.action_ensure_channelbag_for_slot(action, slot)

        # ----------------------------------------
        # Determine track type
        # ----------------------------------------
        is_animation = not action.name.startswith("POS_")

        action_group = action.name

        # ----------------------------------------
        # Iterate groups (each = one track)
        # ----------------------------------------
        for group in channelbag.groups:
            try:
                # ----------------------------------------
                # Find props
                # ----------------------------------------
                track_props = None
                for t in action.quail_tracks:
                    if t.tag == group.name:
                        track_props = t
                        break

                if not track_props:
                    continue

                bone_name = group.name

                if bone_name not in armature_obj.pose.bones:
                    continue

                pose_bone = armature_obj.pose.bones[bone_name]
                bone = armature_obj.data.bones[bone_name]

                # ----------------------------------------
                # Rebuild rest matrix (same as decode)
                # ----------------------------------------
                rest_matrix = bone.matrix_local.copy()

                if bone.parent:
                    rest_matrix = bone.parent.matrix_local.inverted() @ rest_matrix

                # ----------------------------------------
                # Collect frame times
                # ----------------------------------------
                frame_set = set()

                for fcurve in group.channels:
                    for kp in fcurve.keyframe_points:
                        frame_set.add(kp.co.x)

                if not frame_set:
                    continue

                frames = sorted(frame_set)

                # ----------------------------------------
                # Build Track-style data
                # ----------------------------------------
                track_data = {
                    "tag": track_props.track,
                    "action": action_group,
                    "interpolate": 1 if track_props.interpolate else 0,
                    "reverse": 1 if track_props.reverse else 0,
                    "sleep": track_props.sleep if track_props.has_sleep else None,
                    "frames": []
                }

                # ----------------------------------------
                # Evaluate each frame
                # ----------------------------------------
                for f in frames:

                    loc = [0.0, 0.0, 0.0]
                    rot = [1.0, 0.0, 0.0, 0.0]
                    scale_x = 1.0

                    for fc in group.channels:
                        path = fc.data_path

                        if path.endswith("location"):
                            loc[fc.array_index] = fc.evaluate(f)

                        elif path.endswith("rotation_quaternion"):
                            rot[fc.array_index] = fc.evaluate(f)

                        elif path.endswith("scale") and fc.array_index == 0:
                            scale_x = fc.evaluate(f)

                    if bone_name == "DWMPE_DAG" and action.name == "T07_DWM":
                        print(f"  Frame {int(f):3d} RAW FCurve: W={rot[0]:+.9f} X={rot[1]:+.9f} Y={rot[2]:+.9f} Z={rot[3]:+.9f}")

                    if bone_name == "DWMPE_DAG" and action.name == "T07_DWM":
                        print(f"rest_matrix:\n{rest_matrix}")
                    # ----------------------------------------
                    # Rebuild pose_matrix
                    # ----------------------------------------

                    q = mathutils.Quaternion(rot)
                    q.normalize()

                    T = mathutils.Matrix.Translation(loc)
                    R = q.to_matrix().to_4x4()
                    pose_matrix = T @ R

                    # ----------------------------------------
                    # Apply rest transform
                    # ----------------------------------------
                    bone = pose_bone.bone

                    rest_matrix = bone.matrix_local.copy()
                    if bone.parent:
                        rest_matrix = bone.parent.matrix_local.inverted() @ rest_matrix

                    local_anim = rest_matrix @ pose_matrix

                    # ----------------------------------------
                    # Extract final values
                    # ----------------------------------------
                    loc = local_anim.to_translation()
                    rot = local_anim.to_quaternion()

                    if bone_name == "DWMPE_DAG" and action.name == "T07_DWM":
                        print(f"  Frame {int(f):3d} POST-MULT: W={rot.w:+.9f} X={rot.x:+.9f} Y={rot.y:+.9f} Z={rot.z:+.9f}")

                    # ----------------------------------------
                    # Convert BACK to WCE format
                    # ----------------------------------------

                    x = int(loc.x * 256)
                    y = int(loc.y * 256)
                    z = int(loc.z * 256)

                    qw = int(rot.w * 16384)
                    qx = int(rot.x * 16384)
                    qy = int(rot.y * 16384)
                    qz = int(rot.z * 16384)

                    scale = int(scale_x * 256)

                    track_data["frames"].append(
                        (scale, x, y, z, qw, qx, qy, qz)
                    )

                # ----------------------------------------
                # Build names
                # ----------------------------------------
                track_tag = track_data["tag"]

                t = track()

                # ----------------------------------------
                # Identity
                # ----------------------------------------
                t.tag = track_tag
                if "_TRACK." in track_tag:
                    t.trackdef = track_tag.replace(
                        "_TRACK.",
                        "_TRACKDEF."
                    )

                elif track_tag.endswith("_TRACK"):
                    t.trackdef = (
                        track_tag[:-len("_TRACK")] +
                        "_TRACKDEF"
                    )

                else:
                    t.trackdef = f"{track_tag}_TRACKDEF"

                # ----------------------------------------
                # Instance values
                # ----------------------------------------
                t.interpolate = track_data["interpolate"]
                t.reverse = track_data["reverse"]
                t.sleep = track_data["sleep"]

                # ----------------------------------------
                # Definition values
                # ----------------------------------------
                t.frames = track_data["frames"]
                t.legacyframes = []

                # ----------------------------------------
                # Metadata (NOT written)
                # ----------------------------------------
                t.animation = track_data["action"]
                t.is_pose = not is_animation

                # ----------------------------------------
                # Store
                # ----------------------------------------
                parser.tracks[t.tag] = t

            except Exception as e:
                import traceback
                traceback.print_exc()
                errors.append(f"Failed track encode {track_tag}: {e}")

    if errors:
        return "\n".join(errors)

    return ""