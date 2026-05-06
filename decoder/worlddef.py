import bpy
from .context import Context
from ..wce.worlddef import worlddef
from ..common.region import is_region_mesh, create_world_bounds_from_regions

def find_layer_collection(layer_coll, target):
    if layer_coll.collection == target:
        return layer_coll
    for child in layer_coll.children:
        found = find_layer_collection(child, target)
        if found:
            return found
    return None

def decode_worlddef(ctx: Context, wd: worlddef) -> str:

    col = ctx.collection

    # ----------------------------------------
    # Rename collection if RGB tracks exist
    # ----------------------------------------

    if getattr(ctx.parser, "rgbdeformationtrackdefs", None):
        if len(ctx.parser.rgbdeformationtrackdefs) > 0:
            col.name = "_objects"

    if getattr(ctx.parser, "pointlights", None):
        if len(ctx.parser.pointlights) > 0:
            col.name = "_lights"

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

        # Create region bounding empty

        create_world_bounds_from_regions(ctx, ctx.parser)

        # ----------------------------------------
        # REGIONS collection
        # ----------------------------------------
        if len(ctx.parser.regions) > 0:

            region_collection = col.children.get("REGIONS")

            if not region_collection:
                region_collection = bpy.data.collections.new("REGIONS")
                col.children.link(region_collection)

            ctx.region_collection = region_collection
            lc = find_layer_collection(bpy.context.view_layer.layer_collection, region_collection)
            if lc:
                lc.hide_viewport = True
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
            lc = find_layer_collection(bpy.context.view_layer.layer_collection, region_collection)
            if lc:
                lc.hide_viewport = True

        # ----------------------------------------
        # ZONES collection
        # ----------------------------------------

        if len(ctx.parser.zones) > 0:

            zone_collection = col.children.get("ZONES")

            if not zone_collection:
                zone_collection = bpy.data.collections.new("ZONES")
                col.children.link(zone_collection)

            ctx.zone_collection = zone_collection

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