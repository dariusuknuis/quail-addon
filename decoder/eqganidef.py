# pyright: basic, reportGeneralTypeIssues=false

import bpy
import mathutils
from .context import Context
from ..wce.eqganidef import eqganidef


def decode_eqganidef(ctx: Context, ani: eqganidef) -> str:

    arm_obj = None
    ani_tag = ani.tag.lower()

    for obj in ctx.collection.objects:

        if obj.type != "ARMATURE":
            continue

        name = obj.name.lower()

        if name.endswith("_armature"):
            model = name[:-9]  # remove "_armature"
        else:
            model = name

        if ani_tag.startswith(model + "_") or ani_tag.endswith("_" + model):
            arm_obj = obj
            break

    if arm_obj is None:
        return "EQGANIDEF requires armature"

    if arm_obj.animation_data is None:
        arm_obj.animation_data_create()

    action = bpy.data.actions.new(ani.tag)
    arm_obj.animation_data.action = action

    fps = bpy.context.scene.render.fps

    # ------------------------------------------------
    # Iterate bones
    # ------------------------------------------------

    for bone in ani.bones:

        pb = arm_obj.pose.bones.get(bone.bone)

        if pb is None:
            continue

        pb.rotation_mode = 'QUATERNION'

        # -----------------------------------------
        # Compute rest transform (same as S3D)
        # -----------------------------------------

        b = arm_obj.data.bones[pb.name]

        rest_matrix = b.matrix_local.copy()

        if b.parent:
            rest_matrix = b.parent.matrix_local.inverted() @ rest_matrix

        rest_inv = rest_matrix.inverted()

        # -----------------------------------------
        # Frame loop
        # -----------------------------------------

        for frame in bone.frames:

            start_ms = bone.frames[0].milliseconds

            frame_number = ((frame.milliseconds - start_ms) / 1000.0) * fps + 1

            loc = mathutils.Vector(frame.translation)

            rot = mathutils.Quaternion((
                -frame.rotation[3],  # W
                 frame.rotation[0],
                 frame.rotation[1],
                 frame.rotation[2]
            ))

            scl = mathutils.Vector(frame.scale)

            T = mathutils.Matrix.Translation(loc)
            R = rot.to_matrix().to_4x4()
            S = mathutils.Matrix.Diagonal((scl.x, scl.y, scl.z, 1))

            local_anim = T @ R @ S

            pose_matrix = rest_inv @ local_anim

            pb.matrix_basis = pose_matrix

            pb.keyframe_insert("location", frame=frame_number)
            pb.keyframe_insert("rotation_quaternion", frame=frame_number)
            pb.keyframe_insert("scale", frame=frame_number)

    return ""