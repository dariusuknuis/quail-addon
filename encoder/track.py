import bpy, re
import mathutils
from bpy_extras import anim_utils

regexAniPrefix = re.compile(r"^[CDLOPST](0[1-9]|[1-9][0-9])")

def encode_track(parser, context) -> str:

    errors = []

    # ----------------------------------------
    # Iterate armatures
    # ----------------------------------------
    for obj in bpy.data.objects:

        if obj.type != 'ARMATURE':
            continue

        anim_data = obj.animation_data
        if not anim_data or not anim_data.action:
            continue

        action = anim_data.action

        if not action.slots:
            continue

        slot = action.slots[0]
        channelbag = anim_utils.action_ensure_channelbag_for_slot(action, slot)

        # ----------------------------------------
        # Determine track type
        # ----------------------------------------
        is_animation = bool(regexAniPrefix.match(action.name))

        # POS vs animation labeling
        if is_animation:
            action_group = action.name  # e.g. C01_HUM
        else:
            action_group = f"POS_{obj.name[:3]}"

        # ----------------------------------------
        # Iterate groups (each = one track)
        # ----------------------------------------
        for group in channelbag.groups:

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

            if bone_name not in obj.pose.bones:
                continue

            pose_bone = obj.pose.bones[bone_name]
            bone = obj.data.bones[bone_name]

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
                    frame_set.add(round(kp.co.x))

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
            scene = bpy.context.scene

            for f in frames:

                scene.frame_set(int(f))

                # pose space (same as decode input)
                pose_matrix = pose_bone.matrix_basis.copy()

                # Undo decode transform
                local_anim = rest_matrix @ pose_matrix

                # ----------------------------------------
                # Decompose
                # ----------------------------------------
                loc, rot, scale_vec = local_anim.decompose()

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

                scale = int(scale_vec.x * 256)

                track_data["frames"].append(
                    (scale, x, y, z, qw, qx, qy, qz)
                )

            # ----------------------------------------
            # Build names
            # ----------------------------------------
            track_tag = track_data["tag"]
            trackdef_tag = f"{track_tag}DEF"

            # ----------------------------------------
            # Encode objects
            # ----------------------------------------
            try:
                td = encode_trackdefinition(trackdef_tag, track_data)
                ti = encode_trackinstance(track_tag, trackdef_tag, track_data)

                # store in parser
                parser.trackdefinitions[td.tag] = td
                parser.trackinstances[ti.tag] = ti

            except Exception as e:
                errors.append(f"Failed track encode {track_tag}: {e}")

    if errors:
        return "\n".join(errors)

    return ""