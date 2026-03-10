# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
import mathutils

def ensure_pivot():

    if bpy.data.objects.get("pivot"):
        return

    vertices = [
        (-0.1, -0.1, 0.1),
        (0.0, 0, 1.0),
        (0, 0, 0),
        (-0.1, 0.1, 0.1),
        (0.1, -0.1, 0.1),
        (0.1, 0.1, 0.1),
    ]

    faces = [
        (0, 3, 2),
        (2, 3, 5),
        (5, 4, 2),
        (4, 1, 0),
        (2, 4, 0),
        (5, 3, 1),
        (5, 1, 4),
        (0, 1, 3),
    ]

    mesh = bpy.data.meshes.new("pivot")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new("pivot", mesh)

    obj.hide_render = True
    obj.hide_viewport = True
    obj.hide_select = True

def apply_pivot_shapes(arm_obj):

    pivot = bpy.data.objects.get("pivot")

    if pivot is None:
        raise Exception("Pivot object named 'pivot' not found")

    if arm_obj is None or arm_obj.type != 'ARMATURE':
        raise Exception("apply_pivot_shapes requires an armature object")

    arm_center = mathutils.Vector((0, 0, 0))

    for pb in arm_obj.pose.bones:

        pb.custom_shape = pivot
        pb.custom_shape_translation = (0, 0, 0)
        pb.use_custom_shape_bone_size = False

        children = list(pb.children)

        chosen_child = None

        # ----------------------------------------
        # Choose child
        # ----------------------------------------

        if len(children) == 1:
            chosen_child = children[0]

        elif len(children) == 2:

            best_dist = float("inf")

            for c in children:
                d = (c.head - arm_center).length
                if d < best_dist:
                    chosen_child = c
                    best_dist = d

        elif len(children) > 2:

            avg = mathutils.Vector((0, 0, 0))

            for c in children:
                avg += (c.head - pb.head)

            if avg.length > 0:
                avg.normalize()

            best_dot = -999

            for c in children:

                v = (c.head - pb.head)
                if v.length == 0:
                    continue

                v.normalize()
                dot = v.dot(avg)

                if dot > best_dot:
                    chosen_child = c
                    best_dot = dot

        # ----------------------------------------
        # Apply pivot orientation
        # ----------------------------------------

        if chosen_child:

            head = pb.head
            child_head = chosen_child.head

            direction = child_head - head
            length = direction.length

            if length > 0:
                direction.normalize()

                bone_matrix = pb.matrix.to_3x3().normalized()
                direction_local = bone_matrix.inverted() @ direction

                pivot_axis = mathutils.Vector((0, 0, 1))
                rot = pivot_axis.rotation_difference(direction_local)

                pb.custom_shape_rotation_euler = rot.to_euler()
                pb.custom_shape_scale_xyz = (length, length, length)

        else:

            pb.custom_shape_rotation_euler = (0, 0, 0)
            pb.custom_shape_scale_xyz = (0.15, 0.15, 0.15)