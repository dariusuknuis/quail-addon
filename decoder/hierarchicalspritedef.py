# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from .context import Context
from ..wce.hierarchicalspritedef import hierarchicalspritedef
from .dmspritedef2 import decode_dmspritedef2
from .track import get_track


def decode_hierarchicalspritedef(ctx: Context, sprite: hierarchicalspritedef) -> str:

    # ------------------------------------------------
    # Create armature object
    # ------------------------------------------------

    arm_data = bpy.data.armatures.new(sprite.tag)
    arm_obj = bpy.data.objects.new(sprite.tag, arm_data)

    arm_obj.parent = ctx.parent
    ctx.collection.objects.link(arm_obj)

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    bones = {}
    bone_matrices = {}

    tail_len = 0.1

    # ------------------------------------------------
    # Remove Blender default bone
    # ------------------------------------------------

    if "Bone" in arm_data.edit_bones:
        arm_data.edit_bones.remove(arm_data.edit_bones["Bone"])

    # ------------------------------------------------
    # Create bones
    # ------------------------------------------------

    for dag in sprite.dags:

        bone = arm_data.edit_bones.new(dag.tag)

        bone.head = (0, 0, 0)
        bone.tail = (0, tail_len, 0)
        bone.use_connect = False

        bones[dag.tag] = bone

    # ------------------------------------------------
    # Build transform matrices from tracks
    # ------------------------------------------------

    for i, dag in enumerate(sprite.dags):

        bone = bones[dag.tag]

        track = get_track(dag.track)

        if track and track.frames:
            frame = track.frames[0]

            loc = mathutils.Vector(frame["translation"])
            rot = frame["rotation"]
            scale = frame["scale"]

        else:
            loc = mathutils.Vector((0, 0, 0))
            rot = mathutils.Quaternion((1, 0, 0, 0))
            scale = 1.0

        T = mathutils.Matrix.Translation(loc)
        R = rot.to_matrix().to_4x4()
        # S = mathutils.Matrix.Scale(scale, 4)

        local_matrix = T @ R #@ S

        parent_matrix = mathutils.Matrix.Identity(4)

        # find parent matrix using SUBDAGLIST
        for parent_dag in sprite.dags:

            if not parent_dag.subdaglist:
                continue

            count = int(parent_dag.subdaglist[0])
            children = [int(x) for x in parent_dag.subdaglist[1:1 + count]]

            if i in children:
                parent_matrix = bone_matrices.get(
                    parent_dag.tag,
                    mathutils.Matrix.Identity(4)
                )
                break

        world_matrix = parent_matrix @ local_matrix
        bone_matrices[dag.tag] = world_matrix

        head = world_matrix.to_translation()

        bone.head = head
        bone.tail = head + (world_matrix.to_3x3() @ mathutils.Vector((0, tail_len, 0)))

    # arm_obj["_wld_rest_matrices"] = {
    #     name: [list(row) for row in matrix]
    #     for name, matrix in bone_matrices.items()
    # }

    # ------------------------------------------------
    # Build hierarchy from SUBDAGLIST
    # ------------------------------------------------

    for dag in sprite.dags:

        parent_bone = bones.get(dag.tag)

        if not parent_bone:
            continue

        if not dag.subdaglist:
            continue

        child_count = int(dag.subdaglist[0])

        for child_index in dag.subdaglist[1:1 + child_count]:

            child_dag = sprite.dags[int(child_index)]
            child_bone = bones.get(child_dag.tag)

            if child_bone:
                child_bone.parent = parent_bone
                child_bone.use_connect = False

    # ------------------------------------------------
    # Set parent bone tails to first child head
    # ------------------------------------------------

    # for dag in sprite.dags:

    #     parent_bone = bones.get(dag.tag)
    #     if not parent_bone:
    #         continue

    #     if not dag.subdaglist:
    #         continue

    #     child_count = int(dag.subdaglist[0])
    #     if child_count == 0:
    #         continue

    #     # first child
    #     child_index = int(dag.subdaglist[1])
    #     child_dag = sprite.dags[child_index]

    #     child_bone = bones.get(child_dag.tag)
    #     if not child_bone:
    #         continue

    #     # prevent zero-length bones
    #     if (child_bone.head - parent_bone.head).length > 0.00001:
    #         parent_bone.tail = child_bone.head

    bpy.ops.object.mode_set(mode='OBJECT')

    # ------------------------------------------------
    # Decode skins and parent to bones
    # ------------------------------------------------

    for skin in sprite.attachedskins:

        tag = skin.dmsprite

        mesh_obj = bpy.data.objects.get(tag)

        if not mesh_obj:

            dmsprite = ctx.parser.dmspritedef2s.get(tag)

            if not dmsprite:
                return f"hsprite {sprite.tag} refers to dmsprite {tag} but not found"

            err = decode_dmspritedef2(ctx, dmsprite)
            if err:
                return err

            mesh_obj = bpy.data.objects.get(tag)

        mesh = mesh_obj.data

        for dag_tag, bone_matrix in bone_matrices.items():

            vg = mesh_obj.vertex_groups.get(dag_tag)
            if not vg:
                continue

            # get vertices belonging to this group
            for v in mesh.vertices:

                for g in v.groups:
                    if g.group == vg.index:

                        v.co = bone_matrix @ v.co
                        break

        if mesh_obj:

            mesh_obj.parent = arm_obj

    return ""