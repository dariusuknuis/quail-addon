# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from .context import Context
from ..wce.hierarchicalspritedef import hierarchicalspritedef
from .dmspritedef2 import decode_dmspritedef2


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

    tail_len = 0.1

    # ------------------------------------------------
    # Create bones
    # ------------------------------------------------

    for dag in sprite.dags:

        bone = arm_data.edit_bones.new(dag.tag)

        bone.head = (0, 0, 0)
        bone.tail = (0, tail_len, 0)

        bones[dag.tag] = bone

    # ------------------------------------------------
    # Build hierarchy from SUBDAGLIST
    # ------------------------------------------------

    for i, dag in enumerate(sprite.dags):

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

        if mesh_obj:

            bone_tag = sprite.dags[skin.linkskinupdatestodagindex].tag

            mesh_obj.parent = arm_obj
            mesh_obj.parent_type = 'BONE'
            mesh_obj.parent_bone = bone_tag

    return ""
