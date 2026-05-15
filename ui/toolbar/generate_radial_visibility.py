import bpy
from ...common.region import rebuild_vislist_range

class OBJECT_OT_generate_radial_visibility(bpy.types.Operator):
    """Run a radial visibility pass on all regions"""

    bl_idname = "object.generate_radial_visibility"
    bl_label = "Generate Radial Visibility"
    bl_options = {'REGISTER', 'UNDO'}

    search_radius: bpy.props.FloatProperty(
        name="Search Radius",
        default=2000.0,
        min=0.0,
    )

    use_rle: bpy.props.BoolProperty(
        name="Use RLE VisLists",
        description="Encode visibility lists as run-length encoded bytes",
        default=True,
    )

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):

        try:
            run_radial_visibility(
                self.search_radius,
                self.use_rle
            )

        except Exception as e:
            self.report({'ERROR'}, f"Radial visibility failed: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}

def run_radial_visibility(search_radius=2000.0, use_rle=True):

    regions_collection = bpy.data.collections.get("REGIONS")

    if not regions_collection:
        raise RuntimeError("REGIONS collection not found")

    regions = [
        obj for obj in regions_collection.objects
        if obj.get("quaildef") == "region"
    ]

    for region in regions:

        props = region.quail_region

        # ----------------------------------------
        # Set encoding mode
        # ----------------------------------------

        props.vislistbytes = use_rle

        center = region.location

        # ----------------------------------------
        # Ensure vislist exists
        # ----------------------------------------

        if len(props.vislists) == 0:
            props.vislists.add()

        vis = props.vislists[0]

        # ----------------------------------------
        # Clear current visible regions
        # ----------------------------------------

        while len(vis.visible_regions) > 0:
            vis.visible_regions.remove(0)

        # ----------------------------------------
        # Find nearby regions
        # ----------------------------------------

        neighbors = [
            other for other in regions
            if (
                (other.location - center).length <= search_radius
            )
        ]

        # ----------------------------------------
        # Add visible regions
        # ----------------------------------------

        existing = set()

        for neighbor in neighbors:

            if neighbor.name in existing:
                continue

            item = vis.visible_regions.add()
            item.region_name = neighbor.name

            existing.add(neighbor.name)

        # ----------------------------------------
        # Rebuild encoded RANGE string
        # ----------------------------------------

        rebuild_vislist_range(region)

    print(f"Radial visibility computed for {len(regions)} regions.")