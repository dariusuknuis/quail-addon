import bpy
import re
from .context import Context
from ..wce.worlddef import worlddef
from ..common.region import is_region_mesh


def decode_worlddef(ctx: Context, wd: worlddef) -> str:

    col = ctx.collection

    # Tag collection
    col["quaildef"] = "worlddef"

    props = col.quail_worlddef

    # ----------------------------------------
    # Direct mappings
    # ----------------------------------------
    props.newworld = bool(wd.newworld)
    props.zone = bool(wd.zone)

    # ----------------------------------------
    # Optional EQG
    # ----------------------------------------
    if wd.eqgversion is None:
        props.use_eqg = False
        props.eqgversion = 0
    else:
        props.use_eqg = True
        props.eqgversion = wd.eqgversion

    # ========================================
    # ZONE LOGIC
    # ========================================
    if props.zone:

        # ----------------------------------------
        # REGIONS collection
        # ----------------------------------------
        if len(ctx.parser.regions) > 0:

            region_collection = col.children.get("REGIONS")

            if not region_collection:
                region_collection = bpy.data.collections.new("REGIONS")
                col.children.link(region_collection)

            ctx.region_collection = region_collection
            (next((lc for lc in bpy.context.view_layer.layer_collection.children
                for lc in [lc] + list(lc.children)
                if lc.collection == region_collection), None)).hide_viewport = True
        # ----------------------------------------
        # REGION_MESHES collection
        # ----------------------------------------
        has_region_mesh = any(
            is_region_mesh(tag)
            for tag in ctx.parser.dmspritedef2s.keys()
        ) or any(
            is_region_mesh(tag)
            for tag in ctx.parser.dmspritedefinitions.keys()
        )

        if has_region_mesh:

            region_mesh_collection = col.children.get("REGION_MESHES")

            if not region_mesh_collection:
                region_mesh_collection = bpy.data.collections.new("REGION_MESHES")
                col.children.link(region_mesh_collection)

            ctx.region_mesh_collection = region_mesh_collection

        # ----------------------------------------
        # WORLDTREE collection
        # ----------------------------------------

        if len(ctx.parser.worldtrees) > 0:

            worldtree_collection = col.children.get("WORLDTREE")

            if not worldtree_collection:
                worldtree_collection = bpy.data.collections.new("WORLDTREE")
                col.children.link(worldtree_collection)

            ctx.worldtree_collection = worldtree_collection
            (next((lc for lc in bpy.context.view_layer.layer_collection.children
                for lc in [lc] + list(lc.children)
                if lc.collection == worldtree_collection), None)).hide_viewport = True

        # ----------------------------------------
        # Set 3D View clip distance
        # ----------------------------------------
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:

                if area.type == 'VIEW_3D':
                    for space in area.spaces:
                        if space.type == 'VIEW_3D':
                            space.clip_end = 10000.0

    return ""