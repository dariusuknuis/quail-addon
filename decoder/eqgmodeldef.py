# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils

from ..common.armature import ensure_pivot, apply_pivot_shapes
from ..common.mesh import get_vertex_normal_nodegroup
from ..common.eqgmesh import eqg_piece_root
from ..wce.eqgmodeldef import eqgmodeldef
from ..wce.eqganidef import eqganidef
from .eqganidef import decode_eqganidef
from .eqgmaterialdef import decode_eqgmaterialdef
from .context import Context
from ..ui.panel.eqgface import set_face_property


MODULAR_EXCLUDED_PREFIXES = ("obj", "obp")


def _find_modular_model_set(
    ctx: Context,
) -> tuple[eqgmodeldef, dict[str, str]] | None:
    """
    Find the main race model and its recognized multipart pieces.

    The returned dictionary maps each recognized model tag to its
    attachment bone on the main armature.
    """

    modeldefs = list(ctx.parser.eqgmodeldefs.values())

    if len(modeldefs) <= 1:
        return None

    archive_name = (
        str(ctx.parser.archive_name or "")
        .strip()
        .casefold()
        .replace("\\", "/")
        .rsplit("/", 1)[-1]
    )

    if archive_name.endswith(".wce"):
        archive_name = archive_name[:-4]

    base_candidates = [
        model
        for model in modeldefs
        if (
            len(str(model.tag or "").strip()) == 3
            and str(model.tag or "").strip()[0].isalpha()
            and str(model.tag or "").strip().isalnum()
            and len(model.bones) > 0
        )
    ]

    # Prefer the model whose tag matches the archive name.
    main_model = next(
        (
            model
            for model in base_candidates
            if (
                str(model.tag or "")
                .strip()
                .casefold()
                == archive_name
            )
        ),
        None,
    )

    # This handles imports through a file named _root.wce.
    if main_model is None:
        if len(base_candidates) != 1:
            return None

        main_model = base_candidates[0]

    race_tag = (
        str(main_model.tag or "")
        .strip()
        .casefold()
    )

    piece_roots: dict[str, str] = {}

    for model in modeldefs:
        model_tag = (
            str(model.tag or "")
            .strip()
            .casefold()
        )

        if model_tag == race_tag:
            continue

        attachment_root = eqg_piece_root(
            model_tag,
            race_tag,
        )

        if attachment_root is not None:
            piece_roots[model_tag] = attachment_root

    if not piece_roots:
        return None

    return main_model, piece_roots


def _build_parent_map(model_bones) -> dict[str, str]:
    """Build child-name -> parent-name from CHILDINDEX/NEXT chains."""

    parent_map: dict[str, str] = {}

    for parent_bone in model_bones:
        if parent_bone.children <= 0 or parent_bone.childindex < 0:
            continue

        child_index = parent_bone.childindex

        for _ in range(parent_bone.children):
            if child_index < 0 or child_index >= len(model_bones):
                break

            child = model_bones[child_index]
            parent_map[child.bone] = parent_bone.bone
            child_index = child.next

    return parent_map


def _find_shared_armature(
    collection: bpy.types.Collection,
    main_model_tag: str,
) -> bpy.types.Object | None:
    """Find a shared modular armature created from the base model."""

    expected_name = f"{main_model_tag}_armature".casefold()

    for candidate in collection.all_objects:
        if (
            candidate.type == "ARMATURE"
            and candidate.name.casefold() == expected_name
        ):
            return candidate

    return None


def _merge_vertex_group(
    obj: bpy.types.Object,
    source_name: str,
    target_name: str,
) -> None:
    """Rename a vertex group, merging it when the target already exists."""

    source_group = obj.vertex_groups.get(source_name)

    if source_group is None or source_name == target_name:
        return

    target_group = obj.vertex_groups.get(target_name)

    if target_group is None:
        source_group.name = target_name
        return

    source_index = source_group.index

    for vertex in obj.data.vertices:
        for assignment in vertex.groups:
            if assignment.group == source_index:
                target_group.add([vertex.index], assignment.weight, "ADD")
                break

    obj.vertex_groups.remove(source_group)


def _retarget_mesh_to_main_armature(
    obj: bpy.types.Object,
    main_armature: bpy.types.Object,
    root_replacement: str | None,
) -> None:
    """Retarget one modular mesh without combining its geometry."""

    if root_replacement is not None:
        _merge_vertex_group(
            obj,
            "ROOT_BONE",
            root_replacement,
        )

    armature_modifier = None

    for modifier in obj.modifiers:
        if modifier.type == "ARMATURE":
            armature_modifier = modifier
            break

    if armature_modifier is None:
        armature_modifier = obj.modifiers.new("Armature", "ARMATURE")

    armature_modifier.object = main_armature

    world_matrix = obj.matrix_world.copy()
    obj.parent = main_armature
    obj.matrix_world = world_matrix


def _create_armature(
    ctx: Context,
    model: eqgmodeldef,
    location: mathutils.Vector,
) -> bpy.types.Object:
    """Create one Blender armature from an EQGMODELDEF bone list."""

    ensure_pivot()

    armature = bpy.data.armatures.new(model.tag + "_armature")
    armature_obj = bpy.data.objects.new(model.tag + "_armature", armature)
    armature_obj["quaildef"] = "eqgmodarmature"
    ctx.collection.objects.link(armature_obj)
    armature_obj.location = location

    bpy.context.view_layer.objects.active = armature_obj
    armature_obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")

    edit_bones = armature.edit_bones
    bones = {}
    bone_matrices = {}
    tail_len = 1.0

    for source_bone in model.bones:
        bone = edit_bones.new(source_bone.bone)
        bone.head = (0, 0, 0)
        bone.tail = (0, tail_len, 0)
        bone.use_connect = False
        bones[source_bone.bone] = bone

    parent_map = _build_parent_map(model.bones)
    ordered_bones = []
    added = set()

    while len(ordered_bones) < len(model.bones):
        added_this_pass = False

        for source_bone in model.bones:
            name = source_bone.bone

            if name in added:
                continue

            parent_name = parent_map.get(name)

            if parent_name is None or parent_name in added:
                ordered_bones.append(source_bone)
                added.add(name)
                added_this_pass = True

        if not added_this_pass:
            # Malformed hierarchy: append the remaining bones rather than
            # hanging the import forever.
            for source_bone in model.bones:
                if source_bone.bone not in added:
                    ordered_bones.append(source_bone)
                    added.add(source_bone.bone)
            break

    for source_bone in ordered_bones:
        bone = bones[source_bone.bone]
        location_matrix = mathutils.Matrix.Translation(
            mathutils.Vector(source_bone.pivot)
        )
        rotation = mathutils.Quaternion((
            -source_bone.quaternion[3],
            source_bone.quaternion[0],
            source_bone.quaternion[1],
            source_bone.quaternion[2],
        ))
        local_matrix = location_matrix @ rotation.to_matrix().to_4x4()

        parent_name = parent_map.get(source_bone.bone)
        parent_matrix = bone_matrices.get(
            parent_name,
            mathutils.Matrix.Identity(4),
        )
        world_matrix = parent_matrix @ local_matrix
        bone_matrices[source_bone.bone] = world_matrix
        bone.matrix = world_matrix
        bone.length = tail_len

    for child_name, parent_name in parent_map.items():
        if child_name in bones and parent_name in bones:
            bones[child_name].parent = bones[parent_name]

    bpy.ops.object.mode_set(mode="OBJECT")
    apply_pivot_shapes(armature_obj)

    return armature_obj


def _decode_model_pose(
    ctx: Context,
    model: eqgmodeldef,
) -> str:
    """Create the model's one-frame POS animation through the ANI decoder."""

    action_tag = f"POS_{model.tag}"

    # A modular archive can encounter a piece before its main model. The
    # shared-armature path may therefore request the same POS action again
    # when the main model itself is decoded later.
    existing_action = bpy.data.actions.get(action_tag)

    if (
        existing_action is not None
        and existing_action.get("quaildef") == "eqganidef"
    ):
        return ""

    ani = eqganidef()
    ani.tag = action_tag
    ani.version = model.version
    ani.strict = False
    ani.bones = []

    for source_bone in model.bones:
        ani_bone = type(ani).bone()
        ani_bone.bone = source_bone.bone
        ani_bone.frames = []

        frame = type(ani_bone).frame()
        frame.milliseconds = 0
        frame.translation = tuple(source_bone.pivot)
        frame.rotation = tuple(source_bone.quaternion)
        frame.scale = tuple(source_bone.scale)

        ani_bone.frames.append(frame)
        ani.bones.append(ani_bone)

    return decode_eqganidef(ctx, ani)


def _get_or_create_shared_armature(
    ctx: Context,
    main_model: eqgmodeldef,
    location: mathutils.Vector,
) -> tuple[bpy.types.Object | None, str]:
    """Create the base-model armature once, regardless of decode order."""

    armature_obj = _find_shared_armature(
        ctx.collection,
        main_model.tag,
    )

    if armature_obj is not None:
        return armature_obj, ""

    armature_obj = _create_armature(
        ctx,
        main_model,
        location,
    )

    err = _decode_model_pose(ctx, main_model)

    if err:
        return None, f"decode POS_{main_model.tag}: {err}"

    return armature_obj, ""


def _add_skinning_data(
    obj: bpy.types.Object,
    model: eqgmodeldef,
) -> None:
    """Create the model's vertex groups and assign its stored weights."""

    for source_bone in model.bones:
        if obj.vertex_groups.get(source_bone.bone) is None:
            obj.vertex_groups.new(name=source_bone.bone)

    for vertex_index, vertex in enumerate(model.vertices):
        for weight in vertex.weights:
            bone_index, value = weight.weight

            if 0 <= bone_index < len(model.bones):
                bone_name = model.bones[bone_index].bone
                group = obj.vertex_groups.get(bone_name)

                if group is not None:
                    group.add([vertex_index], value, "ADD")


def decode_eqgmodeldef(
    ctx: Context,
    eqgmodeldef: eqgmodeldef,
    location: mathutils.Vector,
) -> str:
    mesh = bpy.data.meshes.new(eqgmodeldef.tag)
    obj = bpy.data.objects.new(eqgmodeldef.tag, mesh)
    ctx.collection.objects.link(obj)

    obj.parent = ctx.parent
    obj.location = location
    obj["quaildef"] = "eqgmodeldef"
    obj.quail_eqgmodeldef.version = str(eqgmodeldef.version)  # type: ignore

    flip_tex = len(eqgmodeldef.bones) == 0

    for mat in eqgmodeldef.materials:
        properties = [
            (prop.property[0], prop.property[1], prop.property[2])
            for prop in mat.properties
        ]
        # textures = [tex.texture for tex in mat.animtextures]
        err = decode_eqgmaterialdef(
            ctx,
            mesh,
            eqgmodeldef.tag,
            mat.materialtag,
            mat.shadertag,
            properties,
            flip_tex,
        )

        if err != "":
            return f"decode {mat.materialtag}: {err}"

    faces_for_creation = [face.triangle for face in eqgmodeldef.faces]
    vertices = [
        mathutils.Vector(vertex.xyz)
        for vertex in eqgmodeldef.vertices
    ]
    mesh.from_pydata(vertices, [], faces_for_creation)
    mesh.update()

    normal_attribute = mesh.attributes.new(
        name="vertex_normals",
        type="FLOAT_VECTOR",
        domain="POINT",
    )

    for index, vertex in enumerate(eqgmodeldef.vertices):
        normal_attribute.data[index].vector = vertex.normal

    color_attribute = mesh.color_attributes.new(
        name="vertex_colors",
        domain="POINT",
        type="FLOAT_COLOR",
    )

    for index, vertex in enumerate(eqgmodeldef.vertices):
        color_attribute.data[index].color = (
            vertex.tint[0] / 255.0,
            vertex.tint[1] / 255.0,
            vertex.tint[2] / 255.0,
            vertex.tint[3] / 255.0,
        )

    uv_layer = mesh.uv_layers.new(name="UVMap")
    uv2_layer = mesh.uv_layers.new(name="UVMap2")

    for triangle in mesh.polygons:
        for corner, vertex_index in enumerate(triangle.vertices):
            source_vertex = eqgmodeldef.vertices[vertex_index]
            loop_index = triangle.loop_indices[corner]
            uv_layer.data[loop_index].uv = source_vertex.uv
            uv2_layer.data[loop_index].uv = source_vertex.uv2

    for index, face in enumerate(eqgmodeldef.faces):
        polygon = mesh.polygons[index]
        polygon.material_index = mesh.materials.find(
            f"{eqgmodeldef.tag}_{face.material}"
        )

        if polygon.material_index == -1:
            return f"Material {eqgmodeldef.tag}_{face.material} not found"

        set_face_property(mesh, index, "passable", face.passable)
        set_face_property(
            mesh,
            index,
            "collisionrequired",
            face.collisionrequired,
        )
        set_face_property(mesh, index, "transparent", face.transparent)
        set_face_property(mesh, index, "culled", face.culled)
        set_face_property(mesh, index, "degenerate", face.degenerate)

    if len(eqgmodeldef.bones) > 0:
        _add_skinning_data(obj, eqgmodeldef)

        modular_set = _find_modular_model_set(ctx)
        current_tag = (
            str(eqgmodeldef.tag or "")
            .strip()
            .casefold()
        )

        main_model = None
        main_tag = ""
        attachment_root = None
        use_shared_armature = False

        if modular_set is not None:
            main_model, piece_roots = modular_set

            main_tag = (
                str(main_model.tag or "")
                .strip()
                .casefold()
            )

            if current_tag == main_tag:
                # The base model owns the complete shared armature.
                use_shared_armature = True

            else:
                attachment_root = piece_roots.get(
                    current_tag
                )

                # Only recognized standard pieces are retargeted.
                if attachment_root is not None:
                    use_shared_armature = True

        if use_shared_armature and main_model is not None:
            main_armature, err = _get_or_create_shared_armature(
                ctx,
                main_model,
                location,
            )

            if err:
                return err

            if main_armature is None:
                return (
                    f"Could not create armature for "
                    f"{main_model.tag}"
                )

            root_replacement = None

            if current_tag != main_tag:
                if main_armature.data.bones.get(
                    attachment_root
                ) is None:
                    return (
                        f"EQGMODELDEF {eqgmodeldef.tag} "
                        f"expects attachment bone "
                        f"{attachment_root}, but it is not "
                        f"present in {main_model.tag}"
                    )

                root_replacement = attachment_root

            _retarget_mesh_to_main_armature(
                obj,
                main_armature,
                root_replacement,
            )

        else:
            # This includes unrecognized model names. They retain their
            # own WCE skeleton rather than joining the race armature.
            armature_obj = _create_armature(
                ctx,
                eqgmodeldef,
                location,
            )

            err = _decode_model_pose(
                ctx,
                eqgmodeldef,
            )

            if err:
                return (
                    f"decode POS_{eqgmodeldef.tag}: {err}"
                )

            armature_modifier = obj.modifiers.new(
                "Armature",
                "ARMATURE",
            )
            armature_modifier.object = armature_obj
            obj.parent = armature_obj

        nodegroup = get_vertex_normal_nodegroup()
        normal_modifier = obj.modifiers.new("VertexNormals", "NODES")
        normal_modifier.node_group = nodegroup

    mesh.update()
    return ""
