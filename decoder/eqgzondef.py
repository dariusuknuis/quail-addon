# pyright: basic, reportGeneralTypeIssues=false

import bpy
import mathutils

from .context import Context
from ..common.zone import ensure_eqg_area_material
from ..wce.eqgzondef import eqgzondef


def _create_area_box(
    collection: bpy.types.Collection,
    name: str,
    position: tuple[float, float, float],
    orientation: tuple[float, float, float],
    extents: tuple[float, float, float],
) -> bpy.types.Object:
    """Create an oriented box from an EQG ZON area record.

    EQG positions map directly to Blender XYZ. Orientations are already in
    radians but use the legacy RZ, RY, RX component order. Extents are treated
    as signed half-extents, so their absolute values determine box size.
    """

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

    obj.location = mathutils.Vector((
        float(position[0]),
        float(position[1]),
        float(position[2]),
    ))

    rz = float(orientation[0])
    ry = float(orientation[1])
    rx = float(orientation[2])

    obj.rotation_mode = "XYZ"
    obj.rotation_euler = mathutils.Euler((
        rx,
        -ry,
        rz,
    ), "XYZ")

    return obj

def decode_eqgzondef(ctx: Context, zon: eqgzondef) -> str:
    """Create Blender objects for every area volume in an EQGZONDEF."""

    if ctx.collection is None:
        return "EQGZONDEF requires a destination collection"

    # Keep all area-volume objects together.
    collection_name = f"{zon.tag}_AREAS"

    area_collection = bpy.data.collections.get(collection_name)
    if area_collection is None:
        area_collection = bpy.data.collections.new(collection_name)
        ctx.collection.children.link(area_collection)
    elif area_collection.name not in ctx.collection.children:
        # Usually unnecessary, but permits reuse of an existing collection.
        try:
            ctx.collection.children.link(area_collection)
        except RuntimeError:
            pass

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

        # Retain the source information independently of the property group.
        obj["eqg_area_index"] = index
        obj["eqg_area_name"] = area.area
        obj["eqg_area_position"] = tuple(area.position)
        obj["eqg_area_orientation"] = tuple(area.orientation)
        obj["eqg_area_extents"] = tuple(area.extents)

        # Helpful viewport settings for translucent zone volumes.
        obj.show_in_front = True

    return ""