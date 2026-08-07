# pyright: basic, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false

import bpy, math
import mathutils

from .context import Context
from ..wce.eqgparticlepointdef import eqgparticlepointdef


def decode_eqgparticlepointdef(
    ctx: Context,
    particlepointdef: eqgparticlepointdef,
) -> str:

    # ------------------------------------------------
    # Find the corresponding armature
    # ------------------------------------------------
    armature_name = f"{particlepointdef.tag}_armature"
    armature_obj = bpy.data.objects.get(armature_name)

    if armature_obj is None:
        return f"Armature {armature_name} not found"

    if armature_obj.type != 'ARMATURE':
        return f"Object {armature_name} is not an armature"

    # Validate the bone references before creating anything.
    for point in particlepointdef.points:
        if not armature_obj.data.bones.get(point.bonename):
            return (
                f"Particle point {point.point}: "
                f"bone {point.bonename} not found in "
                f"armature {armature_name}"
            )

    # ------------------------------------------------
    # Create particle-point empties
    # ------------------------------------------------
    for point in particlepointdef.points:
        obj = bpy.data.objects.new(point.point, None)

        obj.empty_display_type = 'PLAIN_AXES'
        obj.empty_display_size = 0.25

        obj['quaildef'] = 'eqgparticlepointdef'

        # Parent the object beneath the armature in the Outliner.
        obj.parent = armature_obj
        obj.matrix_parent_inverse = mathutils.Matrix.Identity(4)

        # ------------------------------------------------
        # Apply point-local transform
        # ------------------------------------------------
        obj.location = (
            float(point.translation[0]),
            float(point.translation[1]),
            float(point.translation[2]),
        )

        obj.rotation_mode = 'XYZ'
        obj.rotation_mode = 'XYZ'
        obj.rotation_euler = (
            float(point.rotation[0]) * (2.0 * math.pi / 512.0),
            float(point.rotation[1]) * (2.0 * math.pi / 512.0),
            float(point.rotation[2]) * (2.0 * math.pi / 512.0),
        )

        obj.scale = (
            float(point.scale[0]),
            float(point.scale[1]),
            float(point.scale[2]),
        )

        # ------------------------------------------------
        # Follow the specified armature bone
        # ------------------------------------------------
        constraint = obj.constraints.new(type='CHILD_OF')
        constraint.name = point.bonename
        constraint.target = armature_obj
        constraint.subtarget = point.bonename

        # The object is already parented to the armature object, so apply the
        # bone transform in the object's armature-local coordinate space.
        constraint.owner_space = 'LOCAL'
        constraint.target_space = 'POSE'
        constraint.inverse_matrix = mathutils.Matrix.Identity(4)

        ctx.collection.objects.link(obj)

    return ""