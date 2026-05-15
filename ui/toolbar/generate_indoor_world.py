import bpy
from .finalize_region_meshes import finalize_region_meshes
from ...common import ensure_worlddef_structure, find_worlddef_collection, create_worlddef_collection, find_layer_collection
from ...common.bsp import BSPContext, create_world_volume, recursive_indoor_bsp_split
from ...common.region import create_world_bounds_from_regions
from ...common.math_helpers import aabb_mesh_local
from ...common.mesh import bmesh_from_mesh
from ...wce.wce import wce
from ...wce.worlddef import worlddef
from ...wce.worldtree import worldtree
from ...decoder.region import decode_region
from ...decoder.worldtree import decode_worldtree


class OBJECT_OT_generate_indoor_world(bpy.types.Operator):
    bl_idname = "object.generate_indoor_world"
    bl_label = "Generate Indoor World"
    bl_description = "Generate traditional BSP indoor world"
    bl_options = {'REGISTER', 'UNDO'}

    max_faces_per_region: bpy.props.IntProperty(
        name="Max Faces Per Region",
        default=280,
        min=1,
    )

    max_depth: bpy.props.IntProperty(
        name="Max BSP Depth",
        default=64,
        min=1,
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        try:
            run_indoor_bsp_split(
                self.max_faces_per_region,
                self.max_depth,
            )

        except Exception as e:
            self.report({'ERROR'}, str(e))
            return {'CANCELLED'}

        self.report({'INFO'}, "Indoor BSP generation complete")
        return {'FINISHED'}

def run_indoor_bsp_split(
    max_faces_per_region=128,
    max_depth=64,
):

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

            print(f"Generating indoor BSP for {src.name}")

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
                max_depth_reached=0,
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

            bm_geo = bmesh_from_mesh(src)

            bounds_min, bounds_max = aabb_mesh_local(src)

            bm_vol = create_world_volume(
                bounds_min,
                bounds_max,
            )

            recursive_indoor_bsp_split(
                ctx,
                bm_geo,
                bm_vol,
                max_faces_per_region=max_faces_per_region,
                max_depth=max_depth,
                depth=0,
                depth_counters=None,
                backtree=False,
            )

            print(f"Max BSP depth reached: " f"{ctx.max_depth_reached}")

            for reg in parser.regions.values():
                decode_region(ctx, reg)

            lc = find_layer_collection(
                bpy.context.view_layer.layer_collection,
                regions_collection
            )

            if lc:
                lc.hide_viewport = True

            create_world_bounds_from_regions(
                ctx,
                parser,
            )

            decode_worldtree(ctx, wt)

            # Link regions to collection
            for obj in ctx.pending_region_meshes:

                if region_meshes_collection not in obj.users_collection:
                    region_meshes_collection.objects.link(obj)

            finalize_region_meshes(
                ctx.pending_region_meshes
            )

            print(f"Finished indoor BSP for {src.name}")

    finally:

        bpy.context.scene.render.use_lock_interface = False
        bpy.context.window_manager.progress_end()
        bpy.context.view_layer.update()

    print("Indoor BSP complete.")

