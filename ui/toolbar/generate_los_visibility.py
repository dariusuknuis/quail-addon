import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from ...common.region import rebuild_vislist_range


class OBJECT_OT_generate_los_visibility(bpy.types.Operator):
    """Generate line-of-sight visibility between regions"""

    bl_idname = "object.generate_los_visibility"
    bl_label = "Generate Line-Of-Sight Visibility"
    bl_options = {'REGISTER', 'UNDO'}

    search_radius: bpy.props.FloatProperty(
        name="Search Radius",
        default=2000.0,
        min=0.0,
    )

    sample_height_factor: bpy.props.FloatProperty(
        name="Sample Height Factor",
        description="Percent of cavity depth used for interior sampling",
        default=0.35,
        min=0.0,
        max=1.0,
    )

    min_offset: bpy.props.FloatProperty(
        name="Minimum Offset",
        default=4.0,
        min=0.0,
    )

    max_offset: bpy.props.FloatProperty(
        name="Maximum Offset",
        default=64.0,
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

            run_los_visibility(
                self.search_radius,
                self.sample_height_factor,
                self.min_offset,
                self.max_offset,
                self.use_rle
            )

        except Exception as e:

            self.report(
                {'ERROR'},
                f"LOS visibility failed: {e}"
            )

            return {'CANCELLED'}

        return {'FINISHED'}


# ------------------------------------------------------------
# Face sampling
# ------------------------------------------------------------

def get_region_sample_points(
    region,
    sample_height_factor=0.35,
    min_offset=4.0,
    max_offset=64.0
):

    samples = []

    props = region.quail_region

    sprite_name = props.sprite

    # --------------------------------------------------------
    # Region mesh sampling
    # --------------------------------------------------------

    if sprite_name:

        mesh_obj = bpy.data.objects.get(sprite_name)

        if (
            mesh_obj
            and mesh_obj.type == 'MESH'
            and len(mesh_obj.data.polygons) > 0
        ):

            mesh = mesh_obj.data

            wm = mesh_obj.matrix_world
            wm3 = wm.to_3x3()

            region_center = region.location

            sphere_radius = max(
                region.empty_display_size,
                min_offset
            )

            polys = mesh.polygons

            step = max(1, len(polys) // 16)

            classified = []

            cavity_candidates = []

            # ------------------------------------------------
            # Classify faces
            # ------------------------------------------------

            for i in range(0, len(polys), step):

                poly = polys[i]

                face_center = wm @ poly.center

                try:

                    face_normal = (
                        wm3 @ poly.normal
                    ).normalized()

                except:

                    face_normal = Vector((0, 0, 1))

                to_center = (
                    region_center - face_center
                )

                dist_to_center = to_center.length

                if dist_to_center > 1e-6:
                    to_center_dir = (
                        to_center / dist_to_center
                    )
                else:
                    to_center_dir = Vector((0, 0, 1))

                # ------------------------------------------------
                # dot > 0
                # face points toward region center
                # meaning region center is "in front" of face
                # (interior/cavity-facing)
                # ------------------------------------------------

                dot = face_normal.dot(to_center_dir)

                inward = (dot > 0.0)

                classified.append((
                    face_center,
                    face_normal,
                    inward,
                    to_center_dir,
                    dist_to_center
                ))

                # ------------------------------------------------
                # Build cavity candidate
                # ------------------------------------------------

                if inward:

                    edge_distance = max(
                        0.0,
                        sphere_radius - dist_to_center
                    )

                    cavity_depth = (
                        edge_distance *
                        sample_height_factor
                    )

                    cavity_depth = max(
                        min_offset,
                        min(cavity_depth, max_offset)
                    )

                    candidate = (
                        face_center +
                        (to_center_dir * cavity_depth)
                    )

                    cavity_candidates.append(candidate)

            # ------------------------------------------------
            # Shared cavity center
            # ------------------------------------------------

            cavity_center = region_center.copy()

            if cavity_candidates:

                cavity_center = (
                    sum(cavity_candidates, Vector()) /
                    len(cavity_candidates)
                )

            # ------------------------------------------------
            # Final samples
            # ------------------------------------------------

            for (
                face_center,
                face_normal,
                inward,
                to_center_dir,
                dist_to_center
            ) in classified:

                # ----------------------------------------
                # Interior/cavity-facing faces
                # ----------------------------------------

                if inward:

                    samples.append(cavity_center)

                # ----------------------------------------
                # Exterior-facing faces
                # ----------------------------------------

                else:

                    samples.append(
                        face_center +
                        (face_normal * min_offset)
                    )

            # ------------------------------------------------
            # Add cavity center
            # ------------------------------------------------

            samples.append(cavity_center)

            # ------------------------------------------------
            # Add region center
            # ------------------------------------------------

            samples.append(region_center)

            if samples:
                return samples

    # --------------------------------------------------------
    # Empty-region fallback
    # --------------------------------------------------------

    center = region.location

    r = max(
        region.empty_display_size * 0.25,
        1.0
    )

    samples.extend([
        center,
        center + Vector(( r, 0, 0)),
        center + Vector((-r, 0, 0)),
        center + Vector((0,  r, 0)),
        center + Vector((0, -r, 0)),
        center + Vector((0, 0,  r)),
    ])

    return samples


# ------------------------------------------------------------
# Region mesh BVHs
# ------------------------------------------------------------

def build_occluder_bvhs():

    bvhs = []

    region_mesh_collection = bpy.data.collections.get(
        "REGION_MESHES"
    )

    if not region_mesh_collection:
        return []

    region_meshes = [
        obj for obj in region_mesh_collection.objects
        if (
            obj.type == 'MESH'
            and len(obj.data.polygons) > 0
        )
    ]

    for obj in region_meshes:

        bm = None

        try:

            bm = bmesh.new()

            bm.from_mesh(obj.data)

            bvh = BVHTree.FromBMesh(
                bm,
                epsilon=0.0
            )

            bvhs.append((
                obj,
                bvh,
                obj.matrix_world,
                obj.matrix_world.inverted()
            ))

        finally:

            if bm:
                bm.free()

    return bvhs


# ------------------------------------------------------------
# Ray blocking
# ------------------------------------------------------------

def ray_blocked(start, end, bvhs, ignore_objects=None):

    if ignore_objects is None:
        ignore_objects = set()

    direction = end - start

    distance = direction.length

    if distance <= 1e-6:
        return False

    direction.normalize()

    epsilon = 0.05

    start = start + (direction * epsilon)

    max_distance = max(
        0.0,
        distance - (epsilon * 2.0)
    )

    for obj, bvh, wm, inv in bvhs:

        if obj in ignore_objects:
            continue

        local_start = inv @ start

        local_dir = (
            inv.to_3x3() @ direction
        ).normalized()

        hit = bvh.ray_cast(
            local_start,
            local_dir,
            max_distance
        )

        if hit[0] is not None:
            return True

    return False


# ------------------------------------------------------------
# Region visibility
# ------------------------------------------------------------

def regions_visible(
    region_a,
    region_b,
    bvhs,
    sample_height_factor,
    min_offset,
    max_offset
):

    samples_a = get_region_sample_points(
        region_a,
        sample_height_factor,
        min_offset,
        max_offset
    )

    samples_b = get_region_sample_points(
        region_b,
        sample_height_factor,
        min_offset,
        max_offset
    )

    ignore = set()

    sprite_a = region_a.quail_region.sprite
    sprite_b = region_b.quail_region.sprite

    if sprite_a:
        obj = bpy.data.objects.get(sprite_a)
        if obj:
            ignore.add(obj)

    if sprite_b:
        obj = bpy.data.objects.get(sprite_b)
        if obj:
            ignore.add(obj)

    for a in samples_a:

        for b in samples_b:

            if not ray_blocked(
                a,
                b,
                bvhs,
                ignore
            ):
                return True

    return False


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def run_los_visibility(
    search_radius=2000.0,
    sample_height_factor=0.35,
    min_offset=4.0,
    max_offset=64.0,
    use_rle=True
):

    regions_collection = bpy.data.collections.get("REGIONS")

    if not regions_collection:
        raise RuntimeError(
            "REGIONS collection not found"
        )

    regions = [
        obj for obj in regions_collection.objects
        if obj.get("quaildef") == "region"
    ]

    if not regions:
        raise RuntimeError(
            "No region objects found"
        )

    print("Building region BVHs...")

    bvhs = build_occluder_bvhs()

    print(f"Built {len(bvhs)} region BVHs")

    for i, region in enumerate(regions):

        print(
            f"LOS Visibility "
            f"{i+1}/{len(regions)} : "
            f"{region.name}"
        )

        props = region.quail_region

        props.vislistbytes = use_rle

        # ----------------------------------------------------
        # Ensure vislist exists
        # ----------------------------------------------------

        if len(props.vislists) == 0:
            props.vislists.add()

        vis = props.vislists[0]

        # ----------------------------------------------------
        # Clear visible regions
        # ----------------------------------------------------

        while len(vis.visible_regions) > 0:
            vis.visible_regions.remove(0)

        center = region.location

        existing = set()

        for other in regions:

            # ----------------------------------------
            # Distance cull
            # ----------------------------------------

            if (
                other.location - center
            ).length > search_radius:
                continue

            # ----------------------------------------
            # LOS test
            # ----------------------------------------

            visible = regions_visible(
                region,
                other,
                bvhs,
                sample_height_factor,
                min_offset,
                max_offset
            )

            if not visible:
                continue

            if other.name in existing:
                continue

            item = vis.visible_regions.add()

            item.region_name = other.name

            existing.add(other.name)

        rebuild_vislist_range(region)

    print(
        f"LOS visibility computed "
        f"for {len(regions)} regions."
    )