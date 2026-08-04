# pyright: basic, reportGeneralTypeIssues=false

import bpy
import mathutils

from .context import Context
from ..common import ensure_child_collection
from ..common.zone import ensure_eqg_area_material
from ..wce.eqgzondef import eqgzondef


SKELETAL_OFFSET_GROUP = "EQG Skeletal Local Offset"
SKELETAL_OFFSET_MODIFIER = "EQG Skeletal Local Offset"
SKELETAL_LOCAL_OFFSET = (0.0, 0.0, -3.0)


# ======================================================================
# Shared helpers
# ======================================================================


def _tag_key(tag: str) -> str:
    """Remove a known EQG extension and normalize case."""

    value = str(tag or "").strip()

    for extension in (".lit", ".mod", ".ter", ".mds"):
        if value.casefold().endswith(extension):
            value = value[:-len(extension)]
            break

    return value.casefold()


# ======================================================================
# EQG area volumes
# ======================================================================


def _create_area_box(
    collection: bpy.types.Collection,
    name: str,
    position: tuple[float, float, float],
    orientation: tuple[float, float, float],
    extents: tuple[float, float, float],
) -> bpy.types.Object:
    """Create an oriented box from an EQG ZON area record."""

    # The first two extent components are exchanged for Blender.
    half_x = abs(float(extents[1]))
    half_y = abs(float(extents[0]))
    half_z = abs(float(extents[2]))

    vertices = [
        (-half_x, -half_y, -half_z),
        ( half_x, -half_y, -half_z),
        ( half_x,  half_y, -half_z),
        (-half_x,  half_y, -half_z),
        (-half_x, -half_y,  half_z),
        ( half_x, -half_y,  half_z),
        ( half_x,  half_y,  half_z),
        (-half_x,  half_y,  half_z),
    ]

    faces = [
        (0, 3, 2, 1),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    ]

    mesh = bpy.data.meshes.new(f"{name}_MESH")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)

    obj.location = (
        float(position[0]),
        float(position[1]),
        float(position[2]),
    )

    # EQG stores these values in legacy RZ, RY, RX order.
    rz = float(orientation[0])
    ry = float(orientation[1])
    rx = float(orientation[2])

    obj.rotation_mode = "XYZ"
    obj.rotation_euler = mathutils.Euler(
        (
            rx,
            ry,
            rz,
        ),
        "XYZ",
    )

    return obj


# ======================================================================
# EQG lights
# ======================================================================


def _create_eqg_light(
    collection: bpy.types.Collection,
    name: str,
    position: tuple[float, float, float],
    color: tuple[float, float, float],
    radius: float,
) -> bpy.types.Object:
    """Create a Blender point light from an EQG ZON light record."""

    light_data = bpy.data.lights.new(
        name=name,
        type="POINT",
    )

    light_data.color = (
        float(color[0]),
        float(color[1]),
        float(color[2]),
    )

    light_radius = max(float(radius), 0.0)

    # Match the Blender setup used by the S3D point-light decoder. EQG does
    # not provide a separate light-level value, so use the equivalent full
    # light level as the base energy.
    light_data.energy = 50.0
    light_data.exposure = 9.0
    light_data.shadow_soft_size = light_radius

    obj = bpy.data.objects.new(name, light_data)
    collection.objects.link(obj)

    obj.location = (
        float(position[1]),
        float(position[0]),
        float(position[2]),
    )

    obj["quaildef"] = "eqgzonlight"

    return obj


# ======================================================================
# EQG model instances
# ======================================================================


def _find_model_object(model_tag: str) -> bpy.types.Object | None:
    """Find the EQG model or terrain object named by MODELTAG."""

    wanted = _tag_key(model_tag)

    if not wanted:
        return None

    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue

        if obj.get("quaildef") not in {
            "eqgterdef",
            "eqgmodeldef",
        }:
            continue

        if obj.name.casefold() == wanted:
            return obj

    return None


def _find_source_armature(
    source: bpy.types.Object,
) -> bpy.types.Object | None:
    """Return the armature that deforms a source EQG mesh, if any."""

    for modifier in source.modifiers:
        if modifier.type == "ARMATURE" and modifier.object is not None:
            return modifier.object

    if source.parent is not None and source.parent.type == "ARMATURE":
        return source.parent

    return None


def _find_external_eqglit(
    ctx: Context,
    instance_tag: str,
):
    """Find the EQGLIT named for this zone model instance."""

    wanted = _tag_key(instance_tag)

    for eqg_lit in ctx.parser.eqglits.values():
        if _tag_key(eqg_lit.tag) == wanted:
            return eqg_lit

    return None


def _extract_lit_colors(
    lits,
) -> list[tuple[int, int, int, int]]:
    """Extract RGBA byte tuples from WCE LIT records."""

    return [
        (
            int(entry.lit[0]),
            int(entry.lit[1]),
            int(entry.lit[2]),
            int(entry.lit[3]),
        )
        for entry in lits
    ]


def _add_lit_color_layer(
    mesh: bpy.types.Mesh,
    colors: list[tuple[int, int, int, int]],
) -> None:
    """Add the EQG baked-light colors as a point-domain color layer."""

    old_attribute = mesh.attributes.get("lits")
    if old_attribute is not None:
        mesh.attributes.remove(old_attribute)

    attribute = mesh.attributes.new(
        name="lits",
        type="FLOAT_COLOR",
        domain="POINT",
    )

    flattened: list[float] = []

    for red, green, blue, alpha in colors:
        flattened.extend((
            red / 255.0,
            green / 255.0,
            blue / 255.0,
            alpha / 255.0,
        ))

    attribute.data.foreach_set("color", flattened)

    if hasattr(mesh, "color_attributes"):
        try:
            mesh.color_attributes.active_color = attribute
        except (AttributeError, TypeError):
            pass


def _create_regular_eqg_instance(
    source: bpy.types.Object,
    collection: bpy.types.Collection,
    name: str,
) -> bpy.types.Object:
    """Create a linked mesh instance sharing the source mesh datablock."""

    obj = source.copy()
    obj.data = source.data
    obj.parent = None

    obj.name = name
    obj["quaildef"] = "eqgzoninst"

    collection.objects.link(obj)

    return obj


def _create_realized_eqg_instance(
    source: bpy.types.Object,
    collection: bpy.types.Collection,
    name: str,
    colors: list[tuple[int, int, int, int]],
) -> bpy.types.Object:
    """Create an independent mesh copy with its own LIT color layer."""

    obj = source.copy()
    obj.data = source.data.copy()
    obj.parent = None

    obj.name = name
    obj.data.name = f"{name}_MESH"
    obj["quaildef"] = "eqgzoninst"

    collection.objects.link(obj)

    _add_lit_color_layer(obj.data, colors)

    return obj


def _get_skeletal_offset_node_group() -> bpy.types.GeometryNodeTree:
    """Return the single node group reused by all skeletal EQG instances."""

    node_group = bpy.data.node_groups.get(SKELETAL_OFFSET_GROUP)

    if node_group is not None:
        return node_group

    node_group = bpy.data.node_groups.new(
        SKELETAL_OFFSET_GROUP,
        "GeometryNodeTree",
    )

    node_group.interface.new_socket(
        name="Geometry",
        in_out="INPUT",
        socket_type="NodeSocketGeometry",
    )
    node_group.interface.new_socket(
        name="Geometry",
        in_out="OUTPUT",
        socket_type="NodeSocketGeometry",
    )

    group_input = node_group.nodes.new("NodeGroupInput")
    group_input.location = (-300, 0)

    transform = node_group.nodes.new("GeometryNodeTransform")
    transform.name = "Local Skeletal Offset"
    transform.label = "Local Skeletal Offset"
    transform.location = (0, 0)
    transform.inputs["Translation"].default_value = SKELETAL_LOCAL_OFFSET

    group_output = node_group.nodes.new("NodeGroupOutput")
    group_output.location = (300, 0)

    node_group.links.new(
        group_input.outputs["Geometry"],
        transform.inputs["Geometry"],
    )
    node_group.links.new(
        transform.outputs["Geometry"],
        group_output.inputs["Geometry"],
    )

    return node_group


def _add_skeletal_offset_modifier(obj: bpy.types.Object) -> None:
    """Add the shared local-space skeletal offset after deformation."""

    modifier = obj.modifiers.get(SKELETAL_OFFSET_MODIFIER)

    if modifier is None:
        modifier = obj.modifiers.new(
            name=SKELETAL_OFFSET_MODIFIER,
            type="NODES",
        )

    modifier.node_group = _get_skeletal_offset_node_group()

    # Keep the offset last so it translates the completed skinned result.
    current_index = obj.modifiers.find(modifier.name)
    last_index = len(obj.modifiers) - 1

    if current_index != last_index:
        obj.modifiers.move(current_index, last_index)


def _attach_instance_armature(
    source: bpy.types.Object,
    obj: bpy.types.Object,
    collection: bpy.types.Collection,
) -> bpy.types.Object | None:
    """Copy the source armature and parent its instance mesh beneath it."""

    source_armature = _find_source_armature(source)

    if source_armature is None:
        return None

    armature = source_armature.copy()
    armature.data = source_armature.data
    armature.parent = None
    armature.name = obj.name
    armature["quaildef"] = "eqgzoninst"

    collection.objects.link(armature)

    for modifier in obj.modifiers:
        if (
            modifier.type == "ARMATURE"
            and modifier.object == source_armature
        ):
            modifier.object = armature

    # Preserve the source mesh's transform relative to its armature. The
    # copied armature receives the ZON transform later; the mesh itself keeps
    # only this model-local relationship.
    source_relative_matrix = (
        source_armature.matrix_world.inverted_safe()
        @ source.matrix_world
    )

    obj.parent = armature
    obj.matrix_parent_inverse = mathutils.Matrix.Identity(4)
    obj.matrix_basis = source_relative_matrix

    _add_skeletal_offset_modifier(obj)

    return armature


def _apply_eqg_instance_transform(obj: bpy.types.Object, instance) -> None:
    """Apply an EQG ZON instance transform using the S3D convention."""

    obj.location = (
        float(instance.translation[0]),
        float(instance.translation[1]),
        float(instance.translation[2]),
    )

    # Stored in RZ, RY, RX order, just like the S3D instance representation.
    rz = float(instance.rotation[0])
    ry = float(instance.rotation[1])
    rx = float(instance.rotation[2])

    obj.rotation_mode = "XYZ"
    obj.rotation_euler = (
        rx,
        -ry,
        rz,
    )

    uniform_scale = float(instance.scale)
    obj.scale = (
        uniform_scale,
        uniform_scale,
        uniform_scale,
    )


def _cancel_ter_instance_transform(
    obj: bpy.types.Object,
    source: bpy.types.Object,
) -> None:
    """Display the TER source transform while retaining ZON local values."""

    constraint = obj.constraints.new("COPY_TRANSFORMS")
    constraint.name = "Ignore Failed TER Actor Transform"
    constraint.target = source
    constraint.owner_space = "WORLD"
    constraint.target_space = "WORLD"
    constraint.mix_mode = "REPLACE"


def _move_object_to_collection(
    obj: bpy.types.Object,
    collection: bpy.types.Collection,
) -> None:
    """Move an object into one collection without changing its transform."""

    if collection not in obj.users_collection:
        collection.objects.link(obj)

    for current_collection in list(obj.users_collection):
        if current_collection != collection:
            current_collection.objects.unlink(obj)


def _organize_eqg_source_objects(
    archive_collection: bpy.types.Collection,
) -> None:
    """Move and hide source models after their ZON instances are created."""

    # Take the snapshot before moving anything because all_objects changes as
    # objects are relinked into the new child collection.
    archive_objects = list(archive_collection.all_objects)

    source_models = [
        obj
        for obj in archive_objects
        if obj.get("quaildef") == "eqgmodeldef"
    ]

    if source_models:
        objects_collection = ensure_child_collection(
            archive_collection,
            "OBJECTS",
        )

        objects_to_move: set[bpy.types.Object] = set(source_models)

        for source in source_models:
            if source.parent is not None and source.parent.type == "ARMATURE":
                objects_to_move.add(source.parent)

        for obj in objects_to_move:
            _move_object_to_collection(
                obj,
                objects_collection,
            )

            # Hide the source object in the current view layer without
            # changing its render visibility or the collection visibility.
            obj.hide_set(True)

    # Terrain remains in the archive's existing collection because the client
    # effectively uses it as the zone base. Hide only the original TER object;
    # its copied eqgzoninst object is unaffected.
    for obj in archive_objects:
        if obj.get("quaildef") != "eqgterdef":
            continue

        obj.hide_set(True)


def _decode_eqg_instances(
    ctx: Context,
    zon: eqgzondef,
    collection: bpy.types.Collection,
) -> None:
    for index, instance in enumerate(zon.instances):
        model_tag = str(instance.modeltag or "").strip()
        instance_tag = str(instance.instancetag or "").strip()

        if not instance_tag:
            instance_tag = f"EQG_INSTANCE_{index:05d}"

        source = _find_model_object(model_tag)

        if source is None:
            print(
                f"[EQGZONDEF] Instance {instance_tag!r}: "
                f"model {model_tag!r} was not found"
            )
            continue

        lit_colors = _extract_lit_colors(instance.lits)
        lit_source = "embedded ZON data"

        # Use a separate EQGLIT only when the instance has no embedded LITs.
        if not lit_colors:
            external_lit = _find_external_eqglit(
                ctx,
                instance.instancetag,
            )

            if external_lit is not None:
                lit_colors = _extract_lit_colors(external_lit.lits)
                lit_source = f"EQGLIT {external_lit.tag!r}"

        if lit_colors:
            vertex_count = len(source.data.vertices)
            lit_count = len(lit_colors)

            if lit_count == vertex_count:
                obj = _create_realized_eqg_instance(
                    source,
                    collection,
                    instance_tag,
                    lit_colors,
                )
            else:
                print(
                    f"[EQGZONDEF] Instance {instance_tag!r}: "
                    f"{lit_source} contains {lit_count} LIT entries, "
                    f"but model {source.name!r} contains "
                    f"{vertex_count} vertices; creating a regular instance"
                )

                obj = _create_regular_eqg_instance(
                    source,
                    collection,
                    instance_tag,
                )
        else:
            obj = _create_regular_eqg_instance(
                source,
                collection,
                instance_tag,
            )

        # A copied mesh retains an Armature modifier that still points to the
        # source armature. Give every skeletal instance its own armature object
        # and retarget the modifier. The shared Geometry Nodes group supplies
        # the local -3 Z correction after armature deformation.
        armature = _attach_instance_armature(
            source,
            obj,
            collection,
        )

        if armature is not None:
            # Skeletal instances carry their imported ZON transform on the
            # armature. Their mesh children retain only model-local transforms.
            _apply_eqg_instance_transform(armature, instance)
        else:
            _apply_eqg_instance_transform(obj, instance)

        if source.get("quaildef") == "eqgterdef":
            _cancel_ter_instance_transform(obj, source)


# ======================================================================
# Public decoder
# ======================================================================


def decode_eqgzondef(ctx: Context, zon: eqgzondef) -> str:
    """Create EQG model instances and area volumes from an EQGZONDEF."""

    if ctx.collection is None:
        return "EQGZONDEF requires a destination collection"

    instance_collection = ensure_child_collection(
        ctx.collection,
        f"{zon.tag}_INSTANCES",
    )

    _decode_eqg_instances(
        ctx,
        zon,
        instance_collection,
    )

    area_collection = ensure_child_collection(
        ctx.collection,
        f"{zon.tag}_AREAS",
    )

    for index, area in enumerate(zon.areas):
        area_name = area.area.strip()

        if not area_name:
            area_name = f"EQG_AREA_{index:05d}"

        obj = _create_area_box(
            area_collection,
            area_name,
            area.position,
            area.orientation,
            area.extents,
        )

        ensure_eqg_area_material(obj, area_name)

        obj["quaildef"] = "eqgzonarea"

    # ------------------------------------------------
    # Point lights
    # ------------------------------------------------

    light_collection = ensure_child_collection(
        ctx.collection,
        f"{zon.tag}_LIGHTS",
    )

    for index, light in enumerate(zon.lights):
        light_name = str(light.light or "").strip()

        if not light_name:
            light_name = f"EQG_LIGHT_{index:05d}"

        _create_eqg_light(
            light_collection,
            light_name,
            light.lightpos,
            light.lightcolor,
            light.lightradius,
        )

    # Organize the source objects last so instance copies do not inherit
    # hidden object settings from their source meshes or armatures.
    _organize_eqg_source_objects(ctx.collection)

    return ""
