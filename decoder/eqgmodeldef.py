# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
import math
from ..common.armature import ensure_pivot, apply_pivot_shapes
from ..wce.eqgmodeldef import eqgmodeldef
from .eqgmaterialdef import decode_eqgmaterialdef
from .context import Context
from ..ui.panel.eqgface import set_face_property

EQ_TO_BLENDER = (
    mathutils.Matrix.Rotation(math.radians(-90), 4, 'X') @
    mathutils.Matrix.Rotation(math.radians(90), 4, 'Z')
)

def decode_eqgmodeldef(ctx:Context, eqgmodeldef:eqgmodeldef, location:mathutils.Vector) -> str:
    mesh = bpy.data.meshes.new(eqgmodeldef.tag)
    obj = bpy.data.objects.new(eqgmodeldef.tag, mesh)
    ctx.collection.objects.link(obj)

    obj.parent = ctx.parent
    obj.location = location
    obj['quaildef'] = 'eqgmodeldef'
    obj.quail_eqgmodeldef.version = str(eqgmodeldef.version) # type: ignore

    for _, mat in enumerate(eqgmodeldef.materials):
        properties = []
        for _, prop in enumerate(mat.properties):
            properties.append((prop.property[0], prop.property[1], prop.property[2]))
        textures = []
        for _, tex in enumerate(mat.animtextures):
            textures.append(tex.texture)
        err = decode_eqgmaterialdef(ctx, mesh, eqgmodeldef.tag, mat.materialtag, mat.shadertag, mat.hexoneflag, properties, mat.animsleep, textures)
        if err != "":
            return f"decode {mat.materialtag}: {err}"

    faces_for_creation = []
    for face in eqgmodeldef.faces:
        faces_for_creation.append(face.triangle)

    vertices = []
    for _, vertex in enumerate(eqgmodeldef.vertices):
        vertices.append(mathutils.Vector(vertex.xyz))
    mesh.from_pydata(vertices, [], faces_for_creation)
    mesh.update()

    uvlayer = mesh.uv_layers.new(name=eqgmodeldef.tag+"_uv")
    for _, triangle in enumerate(mesh.polygons):
        vertices = list(triangle.vertices)
        for j, vertex in enumerate(vertices):
            src_vert = eqgmodeldef.vertices[vertex]
            uvlayer.data[triangle.loop_indices[j]].uv = (src_vert.uv[0], src_vert.uv[1])

    for i, face in enumerate(eqgmodeldef.faces):
        poly = mesh.polygons[i]

        poly.material_index = mesh.materials.find(f"{eqgmodeldef.tag}_{face.material}")
        if poly.material_index == -1:
            return f"Material {eqgmodeldef.tag}_{face.material} not found"

        set_face_property(mesh, i, "passable", face.passable)
        set_face_property(mesh, i, "collisionrequired", face.collisionrequired)
        set_face_property(mesh, i, "transparent", face.transparent)
        set_face_property(mesh, i, "culled", face.culled)
        set_face_property(mesh, i, "degenerate", face.degenerate)

    # ---------------------------------------------------------
    # Create Armature if bones exist
    # ---------------------------------------------------------
    armature_obj = None

    if len(eqgmodeldef.bones) > 0:

        ensure_pivot()

        armature = bpy.data.armatures.new(eqgmodeldef.tag + "_armature")
        armature_obj = bpy.data.objects.new(eqgmodeldef.tag + "_armature", armature)
        ctx.collection.objects.link(armature_obj)

        armature_obj.location = location
        obj.parent = armature_obj

        bpy.context.view_layer.objects.active = armature_obj
        bpy.ops.object.mode_set(mode='EDIT')

        edit_bones = armature.edit_bones

        bone_map = []

        # -----------------------------------------------------
        # Create bones
        # -----------------------------------------------------
        bones = {}
        bone_matrices = {}

        tail_len = 0.1

        # -----------------------------------------------------
        # Create bones (temporary positions)
        # -----------------------------------------------------
        for bone in eqgmodeldef.bones:

            b = edit_bones.new(bone.bone)

            b.head = (0, 0, 0)
            b.tail = (0, tail_len, 0)
            b.use_connect = False

            bones[bone.bone] = b

        # -----------------------------------------------------
        # Build transform matrices
        # -----------------------------------------------------
        for i, bone in enumerate(eqgmodeldef.bones):

            b = bones[bone.bone]

            loc = mathutils.Vector(bone.pivot)

            rot = mathutils.Quaternion((
                bone.quaternion[3],
                bone.quaternion[0],
                bone.quaternion[1],
                bone.quaternion[2]
            ))

            scale_vec = mathutils.Vector(bone.scale)

            T = mathutils.Matrix.Translation(loc)
            R = rot.to_matrix().to_4x4()
            S = mathutils.Matrix.Diagonal(scale_vec).to_4x4()

            local_matrix = EQ_TO_BLENDER @ (T @ R @ S) @ EQ_TO_BLENDER.inverted()

            parent_matrix = mathutils.Matrix.Identity(4)

            # find parent
            for parent_index, parent_bone in enumerate(eqgmodeldef.bones):

                if parent_bone.children <= 0 or parent_bone.childindex < 0:
                    continue

                child_index = parent_bone.childindex

                for _ in range(parent_bone.children):

                    if child_index == i:

                        parent_matrix = bone_matrices.get(
                            parent_bone.bone,
                            mathutils.Matrix.Identity(4)
                        )
                        break

                    child_index = eqgmodeldef.bones[child_index].next

            world_matrix = parent_matrix @ local_matrix

            bone_matrices[bone.bone] = world_matrix

            # apply transform
            b.matrix = world_matrix
            b.length = tail_len

        # -----------------------------------------------------
        # Parent bones using CHILDINDEX + NEXT chain
        # -----------------------------------------------------
        for i, bone in enumerate(eqgmodeldef.bones):

            if bone.children <= 0 or bone.childindex < 0:
                continue

            child_index = bone.childindex

            for _ in range(bone.children):

                if child_index < 0 or child_index >= len(eqgmodeldef.bones):
                    break

                child_name = eqgmodeldef.bones[child_index].bone
                parent_name = bone.bone

                bones[child_name].parent = bones[parent_name]

                child_index = eqgmodeldef.bones[child_index].next

        bpy.ops.object.mode_set(mode='OBJECT')

        # -----------------------------------------------------
        # Add armature modifier
        # -----------------------------------------------------
        mod = obj.modifiers.new("Armature", 'ARMATURE')
        mod.object = armature_obj

        obj.parent = armature_obj

        # -----------------------------------------------------
        # Create vertex groups
        # -----------------------------------------------------
        for bone in eqgmodeldef.bones:
            obj.vertex_groups.new(name=bone.bone)

        # -----------------------------------------------------
        # Assign weights
        # -----------------------------------------------------
        for v_index, vertex in enumerate(eqgmodeldef.vertices):

            for weight in vertex.weights:

                bone_index, w = weight.weight

                if bone_index < len(eqgmodeldef.bones):

                    bone_name = eqgmodeldef.bones[bone_index].bone

                    group = obj.vertex_groups.get(bone_name)

                    if group:
                        group.add([v_index], w, 'ADD')

        apply_pivot_shapes(armature_obj)

    mesh.update()
    return ""


