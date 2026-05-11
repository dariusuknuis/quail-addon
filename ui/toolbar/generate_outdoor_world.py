# pyright: basic, reportGeneralTypeIssues=false

import bpy
from ...common.bsp import BSPContext, normalize_bounds, create_world_volume, recursive_bsp_split, aabb_mesh_world, build_volume_planes, point_inside_convex
from ...common.region import create_world_bounds_from_regions
from ...common.math_helpers import aabb_mesh_local
from ...common.mesh import bmesh_from_mesh
from ...wce.wce import wce
from ...wce.worlddef import worlddef
from ...wce.worldtree import worldtree
from ...decoder.region import decode_region
from ...decoder.worldtree import decode_worldtree
from ...common import find_layer_collection


AABB_EPS = 0.001

class OBJECT_OT_generate_outdoor_world(bpy.types.Operator):
    bl_idname = "object.generate_outdoor_world"
    bl_label = "Generate Outdoor World"
    bl_description = "Generate BSP regions and world tree"
    bl_options = {'REGISTER', 'UNDO'}

    target_size: bpy.props.FloatProperty(
        name="Target Size",
        default=282.0,
        min=0.01,
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        try:
            run_outdoor_bsp_split(self.target_size)

        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        self.report({'INFO'}, "Outdoor BSP generation complete")
        return {'FINISHED'}

# ------------------------------------------------------------
# Collection helpers
# ------------------------------------------------------------

def ensure_child_collection(parent: bpy.types.Collection, name: str):

    collection = parent.children.get(name)

    if collection:
        return collection

    collection = bpy.data.collections.new(name)
    parent.children.link(collection)

    return collection


def ensure_worlddef_structure(worlddef_collection):

    worlddef_collection["quaildef"] = "worlddef"

    regions = ensure_child_collection(
        worlddef_collection,
        "REGIONS"
    )

    region_meshes = ensure_child_collection(
        worlddef_collection,
        "REGION_MESHES"
    )

    worldtree = ensure_child_collection(
        worlddef_collection,
        "WORLDTREE"
    )

    zones = ensure_child_collection(
        worlddef_collection,
        "ZONES"
    )

    return {
        "regions": regions,
        "region_meshes": region_meshes,
        "worldtree": worldtree,
        "zones": zones,
    }


# ------------------------------------------------------------
# Worlddef lookup helpers
# ------------------------------------------------------------

def find_parent_collection(child_collection):

    for collection in bpy.data.collections:

        if child_collection.name in collection.children:
            return collection

    return None


def find_worlddef_collection(obj):

    visited = set()

    def walk(collection):

        if not collection:
            return None

        if collection in visited:
            return None

        visited.add(collection)

        if collection.get("quaildef") == "worlddef":
            return collection

        parent = find_parent_collection(collection)

        if parent:
            return walk(parent)

        return None

    for collection in obj.users_collection:

        found = walk(collection)

        if found:
            return found

    return None


def create_worlddef_collection(name):

    collection = bpy.data.collections.new(name)

    bpy.context.scene.collection.children.link(collection)

    collection["quaildef"] = "worlddef"

    return collection


# ------------------------------------------------------------
# Main BSP split
# ------------------------------------------------------------

def run_outdoor_bsp_split(target_size=282.0):

    bpy.context.preferences.view.show_splash = False
    bpy.context.scene.render.use_lock_interface = True
    bpy.context.view_layer.depsgraph.update()
    bpy.context.window_manager.progress_begin(0, 100)

    try:
        selected_objs = [
            obj for obj in bpy.context.selected_objects
            if (
                obj.type == 'MESH'
                and obj.get("Formatted Terrain") is True
                and "_ZONE" not in obj.name
            )
        ]

        if not selected_objs:
            raise RuntimeError(
                "No valid formatted terrain mesh selected."
            )

        zone_volumes = [
            obj for obj in bpy.data.objects
            if (
                obj.type == 'MESH'
                and "_ZONE" in obj.name
            )
        ]

        for src in selected_objs:
            print(f"Generating BSP world for {src.name}")

            # Find or create WORLDDEF collection
            worlddef_collection = find_worlddef_collection(src)
            if not worlddef_collection:
                base = src.name.split("_")[0]
                worlddef_collection = create_worlddef_collection(
                    f"{base}_WORLDDEF"
                )

            collections = ensure_worlddef_structure(
                worlddef_collection
            )

            regions_collection = collections["regions"]
            region_meshes_collection = collections["region_meshes"]
            worldtree_collection = collections["worldtree"]
            zones_collection = collections["zones"]

            # Link zones into ZONES collection
            for zone in zone_volumes:
                if zones_collection not in zone.users_collection:
                    zones_collection.objects.link(zone)

            # Create parser + BSP context
            parser = wce("")

            ctx = BSPContext(
                parser=parser,
                collection=worlddef_collection,
                parent=None,
                worlddef_collection=worlddef_collection,
                region_collection=regions_collection,
                region_mesh_collection=region_meshes_collection,
                worldtree_collection=worldtree_collection,
                zone_collection=zones_collection,
                source_object=src,
                zone_volumes=zone_volumes,
                region_counter=[1],
                worldnode_counter=[1],
                region_centroids={},
                pending_region_meshes=[],
            )

            wd = worlddef()
            wd.newworld = 0
            wd.zone = 1
            wd.eqgversion = None
            parser.worlddefs["WORLD"] = wd

            wt = worldtree()
            wt.tag = "WORLDTREE"
            parser.worldtrees[wt.tag] = wt

            # BSP setup
            bounds_min, bounds_max = aabb_mesh_local(src)

            vol_min, vol_max = normalize_bounds(
                bounds_min,
                bounds_max,
                target_size
            )

            bm = bmesh_from_mesh(src)

            bm_vol = create_world_volume(
                vol_min,
                vol_max
            )

            recursive_bsp_split(
                ctx,
                bm,
                bm_vol,
                target_size,
                depth=0,
                depth_counters=None,
                backtree=False,
            )

            # Decode generated regions and worldnodes
            for reg in parser.regions.values():

                decode_region(ctx, reg)

            lc = find_layer_collection(
                bpy.context.view_layer.layer_collection,
                regions_collection
            )

            if lc:
                lc.hide_viewport = True


            create_world_bounds_from_regions(ctx, parser)

            decode_worldtree(ctx, wt)

            # Link regions to collection
            for obj in ctx.pending_region_meshes:

                if region_meshes_collection not in obj.users_collection:
                    region_meshes_collection.objects.link(obj)

            # Region -> Zone membership

            zone_boxes = {
                zone: aabb_mesh_world(zone)
                for zone in zone_volumes
            }

            zone_planes = {
                zone: build_volume_planes(zone)
                for zone in zone_volumes
            }

            for zone in zone_volumes:
                minb, maxb = zone_boxes[zone]
                planes = zone_planes[zone]
                region_idxs = []
                for region_index, centroid in ctx.region_centroids.items():
                    pt = centroid

                    # AABB test
                    if (
                        pt.x < minb.x - AABB_EPS or
                        pt.x > maxb.x + AABB_EPS or
                        pt.y < minb.y - AABB_EPS or
                        pt.y > maxb.y + AABB_EPS or
                        pt.z < minb.z - AABB_EPS or
                        pt.z > maxb.z + AABB_EPS
                    ):
                        continue

                    # Convex volume test
                    if point_inside_convex(pt, planes):

                        region_idxs.append(
                            region_index - 1
                        )

                props = zone.quail_zone

                while len(props.regionlist) > 0:
                    props.regionlist.remove(0)

                for region_index in region_idxs:
                    region_tag = f"R{region_index + 1:06d}"
                    item = props.regionlist.add()
                    item.region_name = region_tag

            print(f"Finished BSP world for {src.name}")

    finally:
        bpy.context.scene.render.use_lock_interface = False
        bpy.context.window_manager.progress_end()
        bpy.context.view_layer.update()

    print("BSP splitting complete.")