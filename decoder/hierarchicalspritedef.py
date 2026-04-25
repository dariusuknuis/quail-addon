# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from .context import Context
from ..common.armature import ensure_pivot, apply_pivot_shapes, attach_object_to_dag
from ..common.s3dobject import attach_collision_volume, create_bounding_radius_empty
from ..wce.hierarchicalspritedef import hierarchicalspritedef
from .track import get_track


def decode_hierarchicalspritedef(ctx: Context, sprite: hierarchicalspritedef) -> str:

    # -----------------------------------------------------------
    # Create pivot for making nice bones or get if already exists
    # -----------------------------------------------------------

    ensure_pivot()

    # ------------------------------------------------
    # Create armature object
    # ------------------------------------------------

    arm_data = bpy.data.armatures.new(sprite.tag)
    arm_obj = bpy.data.objects.new(sprite.tag, arm_data)

    arm_obj.parent = ctx.parent
    ctx.collection.objects.link(arm_obj)
    arm_obj['quaildef'] = 'hierarchicalspritedef'

    # ------------------------------------------------
    # Populate properties for panel
    # ------------------------------------------------

    props = arm_obj.quail_hierarchicalspritedef

    while len(props.dags) > 0:
        props.dags.remove(0)

    for dag in sprite.dags:
        d = props.dags.add()

        d.tag = dag.tag
        obj = bpy.data.objects.get(dag.spritetag)
        if obj:
            d.spritetag = obj
        else:
            d.spritetag = None
        d.track = dag.track or ""

        while len(d.subdags) > 0:
            d.subdags.remove(0)

        if dag.subdaglist:
            count = int(dag.subdaglist[0])
            children = [int(x) for x in dag.subdaglist[1:1 + count]]

            for child_idx in children:
                item = d.subdags.add()
                item.dag_index = child_idx

    props.haveattachedskins = bool(sprite.haveattachedskins)

    props.numattachedskins = len(sprite.attachedskins)

    while len(props.attachedskins) > 0:
        props.attachedskins.remove(0)

    for skin in sprite.attachedskins:
        s = props.attachedskins.add()

        s.linkdagindex = skin.linkskinupdatestodagindex

        obj = bpy.data.objects.get(skin.dmsprite)
        if obj:
            s.dmsprite = obj

    if sprite.centeroffset is not None:
        props.has_centeroffset = True

        x, y, z = sprite.centeroffset
        props.center_x = x
        props.center_y = y
        props.center_z = z
    else:
        props.has_centeroffset = False

    if sprite.boundingradius is not None:
        props.has_boundingradius = True
        props.boundingradius = sprite.boundingradius
    else:
        props.has_boundingradius = False
        props.boundingradius = 1.0

    props.polyhedron = bpy.data.objects.get(sprite.sprite)

    props.dagcollisions = bool(sprite.dagcollisions)

    # ------------------------------------------------
    # Initialize dictionaries
    # ------------------------------------------------

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    bones = {}
    bone_matrices = {}

    bounding_radius = sprite.boundingradius if sprite.boundingradius is not None else 1.0
    tail_len = round(bounding_radius / 10, 2)

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

        else:
            loc = mathutils.Vector((0, 0, 0))
            rot = mathutils.Quaternion((1, 0, 0, 0))

        T = mathutils.Matrix.Translation(loc)
        R = rot.to_matrix().to_4x4()

        local_matrix = T @ R

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

        # 🔹 Correct way to build the bone
        bone.matrix = world_matrix
        bone.length = tail_len

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

    bpy.ops.object.mode_set(mode='OBJECT')

    # -------------------------------------------------------------
    # Get attachedskins and variations of those and apply transforms
    # -------------------------------------------------------------

    for mesh_obj in bpy.data.objects:

        if mesh_obj.type != 'MESH':
            continue

        if mesh_obj.get("quaildef") not in {"dmspritedef2", "dmspritedefinition"}:
            continue

        if mesh_obj.get("hsprite") != sprite.tag:
            continue

        mesh = mesh_obj.data

        for dag_tag, bone_matrix in bone_matrices.items():

            vg = mesh_obj.vertex_groups.get(dag_tag)
            if not vg:
                continue

            rot_mat = bone_matrix.to_3x3()

            # get vertices belonging to this group
            for v in mesh.vertices:

                for g in v.groups:
                    if g.group == vg.index:

                        v.co = bone_matrix @ v.co

                         # Transform normal (if exists)
                        if "vertex_normals" in mesh.attributes:
                            normal_attr = mesh.attributes["vertex_normals"]
                            n = mathutils.Vector(normal_attr.data[v.index].vector)

                            n = rot_mat @ n
                            # n.normalize()

                            normal_attr.data[v.index].vector = n
                        break

        if mesh_obj:

            mesh_obj.parent = arm_obj
            arm_mod = mesh_obj.modifiers.new(name="Armature", type='ARMATURE')
            arm_mod.object = arm_obj

            bpy.context.view_layer.objects.active = mesh_obj
            for _ in range(len(mesh_obj.modifiers)):
                bpy.ops.object.modifier_move_up(modifier=arm_mod.name)

    bpy.context.view_layer.update()

    # ----------------------------------------------------------
    # Get objects attached to DAGs and add "Child Of" constraint
    # ----------------------------------------------------------

    for dag in sprite.dags:
        if not dag.spritetag:
            continue

        obj = bpy.data.objects.get(dag.spritetag)
        if not obj:
            continue

        attach_object_to_dag(obj, arm_obj, dag.tag)

    # ------------------------------------------------
    # Build fake bones to look nice
    # ------------------------------------------------

    apply_pivot_shapes(arm_obj)

    # ------------------------------------------------
    # Add bouding radius empty
    # ------------------------------------------------

    create_bounding_radius_empty(
        parent_obj=arm_obj,
        radius=bounding_radius,
        collection=ctx.collection
    )

    # ------------------------------------------------
    # Attach collision volume (polyhedron)
    # ------------------------------------------------

    if sprite.sprite:
        attach_collision_volume(
            parent_obj=arm_obj,
            poly_tag=sprite.sprite
        )

    return ""