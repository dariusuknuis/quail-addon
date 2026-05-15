import bpy
import bmesh
import random
import numpy as np
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

    standing_height: bpy.props.FloatProperty(
        name="Standing Height",
        description="Height above walkable surfaces",
        default=32.0,
        min=0.0,
    )

    wall_offset: bpy.props.FloatProperty(
        name="Wall Offset",
        description="Distance projected away from walls",
        default=8.0,
        min=0.0,
    )

    rays_per_point: bpy.props.IntProperty(
        name="Rays Per Point",
        default=128,
        min=1,
    )

    min_hit_count: bpy.props.IntProperty(
        name="Minimum Hit Count",
        description="Minimum ray hits required to mark a region visible",
        default=1,
        min=1,
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
                self.standing_height,
                self.wall_offset,
                self.rays_per_point,
                self.min_hit_count,
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
# Sample points from region
# ------------------------------------------------------------

def get_region_sample_points(
    region,
    standing_height=32.0,
    wall_offset=8.0
):

    samples = []

    props = region.quail_region

    sprite_name = props.sprite

    world_up = Vector((0, 0, 1))

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

            polys = mesh.polygons

            step = max(1, len(polys) // 24)

            for i in range(0, len(polys), step):

                poly = polys[i]

                face_center = wm @ poly.center

                try:
                    face_normal = (wm3 @ poly.normal).normalized()
                except:
                    face_normal = world_up.copy()

                upness = face_normal.dot(world_up)

                if upness >= 0.707:

                    sample_dir = (
                        (face_normal * 0.25) + (world_up * 0.75)
                    ).normalized()

                    samples.append(
                        face_center + (sample_dir * standing_height)
                    )

                else:

                    samples.append(
                        face_center + (face_normal * wall_offset)
                    )

            if samples:
                return samples

    # Fallback: region center only
    samples.append(
        region.location + Vector((0, 0, standing_height))
    )

    return samples


# ------------------------------------------------------------
# Build a SINGLE merged WORLD-SPACE occluder BVH
#
# Merging all meshes into one BVH means one ray_cast call
# per ray instead of N (one per mesh object). This is the
# single biggest speed-up for scenes with multiple occluder
# meshes.
# ------------------------------------------------------------

def build_occluder_bvh():

    region_mesh_collection = bpy.data.collections.get("REGION_MESHES")

    if not region_mesh_collection:
        return None

    merged_bm = bmesh.new()

    any_added = False

    for obj in region_mesh_collection.objects:

        if (
            obj.type != 'MESH'
            or len(obj.data.polygons) == 0
        ):
            continue

        temp_bm = bmesh.new()

        temp_bm.from_mesh(obj.data)

        # Bake world transform into geometry
        temp_bm.transform(obj.matrix_world)

        # Append into merged bmesh
        src_verts = [
            merged_bm.verts.new(v.co)
            for v in temp_bm.verts
        ]

        for face in temp_bm.faces:

            try:
                merged_bm.faces.new([
                    src_verts[v.index]
                    for v in face.verts
                ])
            except Exception:
                pass

        temp_bm.free()

        any_added = True

    if not any_added:
        merged_bm.free()
        return None

    bvh = BVHTree.FromBMesh(merged_bm, epsilon=0.0)

    merged_bm.free()

    return bvh


# ------------------------------------------------------------
# Region AABBs — stored as plain tuples for fast access
# ------------------------------------------------------------

def build_region_boxes(regions):

    region_boxes = []

    for region in regions:

        # Cache location once — obj.location copies on each access
        loc = region.location.copy()

        radius = max(region.empty_display_size, 1.0)

        minb = (
            loc.x - radius,
            loc.y - radius,
            loc.z - radius,
        )

        maxb = (
            loc.x + radius,
            loc.y + radius,
            loc.z + radius,
        )

        region_boxes.append((
            region,
            region.name,
            loc,
            minb,
            maxb,
        ))

    return region_boxes


# ------------------------------------------------------------
# Generate all ray directions at once with numpy.
#
# random_direction() called N times in a loop is slow.
# Drawing from a 3D normal distribution and normalising
# gives uniform random unit vectors in one vectorised op.
# ------------------------------------------------------------

def random_directions_batch(n):

    vecs = np.random.randn(n, 3).astype(np.float32)

    norms = np.linalg.norm(vecs, axis=1, keepdims=True)

    # Extremely unlikely but guard against zero vectors
    norms = np.where(norms < 1e-6, 1.0, norms)

    return vecs / norms


# ------------------------------------------------------------
# Point inside AABB — plain tuple version (no Vector overhead)
# ------------------------------------------------------------

def point_inside_aabb(px, py, pz, minb, maxb):

    return (
        minb[0] <= px <= maxb[0]
        and minb[1] <= py <= maxb[1]
        and minb[2] <= pz <= maxb[2]
    )


# ------------------------------------------------------------
# Ray / AABB — plain tuple version
# ------------------------------------------------------------

def intersect_ray_aabb(ox, oy, oz, dx, dy, dz, minb, maxb):

    tmin = -1e20
    tmax =  1e20

    for o, d, lo, hi in (
        (ox, dx, minb[0], maxb[0]),
        (oy, dy, minb[1], maxb[1]),
        (oz, dz, minb[2], maxb[2]),
    ):

        if abs(d) < 1e-8:

            if o < lo or o > hi:
                return None

            continue

        inv = 1.0 / d

        t1 = (lo - o) * inv
        t2 = (hi - o) * inv

        if t1 > t2:
            t1, t2 = t2, t1

        tmin = max(tmin, t1)
        tmax = min(tmax, t2)

        if tmin > tmax:
            return None

    if tmax < 0.0:
        return None

    return tmax if tmin < 0.0 else tmin


# ------------------------------------------------------------
# Compute visible regions from one sample point
# ------------------------------------------------------------

def get_visible_regions_from_point(
    src_pos,
    bvh,
    region_boxes,
    rays_per_point,
    search_radius,
    reachable_boxes,
):

    visible_regions = {}

    EPSILON = 0.5

    # Generate all directions in one numpy call
    directions = random_directions_batch(rays_per_point)

    sx, sy, sz = src_pos.x, src_pos.y, src_pos.z

    for i in range(rays_per_point):

        dx, dy, dz = float(directions[i, 0]), float(directions[i, 1]), float(directions[i, 2])

        rx = sx + dx * EPSILON
        ry = sy + dy * EPSILON
        rz = sz + dz * EPSILON

        ray_start = Vector((rx, ry, rz))
        direction  = Vector((dx, dy, dz))

        # ----------------------------------------------------
        # Single ray_cast against the merged occluder BVH
        # ----------------------------------------------------

        nearest_block_dist = search_radius

        if bvh is not None:

            hit_co, _, _, _ = bvh.ray_cast(
                ray_start,
                direction,
                search_radius
            )

            if hit_co is not None:

                dist = (hit_co - ray_start).length

                if dist >= 0.5:
                    nearest_block_dist = dist

        # ----------------------------------------------------
        # Test only region boxes within search_radius of this
        # sample point — prefiltered per sample in caller
        # ----------------------------------------------------

        for region, name, loc, minb, maxb in reachable_boxes:

            if point_inside_aabb(rx, ry, rz, minb, maxb):

                visible_regions[name] = visible_regions.get(name, 0) + 1

                continue

            hit_dist = intersect_ray_aabb(
                rx, ry, rz,
                dx, dy, dz,
                minb, maxb
            )

            if hit_dist is None:
                continue

            if hit_dist > nearest_block_dist:
                continue

            visible_regions[name] = visible_regions.get(name, 0) + 1

    return visible_regions


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def run_los_visibility(
    search_radius=2000.0,
    standing_height=32.0,
    wall_offset=8.0,
    rays_per_point=128,
    min_hit_count=4,
    use_rle=True
):

    regions_collection = bpy.data.collections.get("REGIONS")

    if not regions_collection:
        raise RuntimeError("REGIONS collection not found")

    regions = [
        obj for obj in regions_collection.objects
        if obj.get("quaildef") == "region"
    ]

    if not regions:
        raise RuntimeError("No region objects found")

    # --------------------------------------------------------
    # Build a single merged BVH for all occluder geometry
    # --------------------------------------------------------

    print("Building merged WORLD-SPACE BVH...")

    bvh = build_occluder_bvh()

    print(f"Merged BVH built ({'' if bvh else 'no occluders found'})")

    region_boxes = build_region_boxes(regions)

    print(f"Built {len(region_boxes)} region AABBs")

    search_radius_sq = search_radius * search_radius

    # --------------------------------------------------------
    # Main region loop
    # --------------------------------------------------------

    for i, region in enumerate(regions):

        print(
            f"\nLOS Visibility "
            f"{i+1}/{len(regions)} : "
            f"{region.name}"
        )

        props = region.quail_region

        props.vislistbytes = use_rle

        if len(props.vislists) == 0:
            props.vislists.add()

        vis = props.vislists[0]

        while len(vis.visible_regions) > 0:
            vis.visible_regions.remove(0)

        existing = set()

        samples = get_region_sample_points(
            region,
            standing_height,
            wall_offset
        )

        print(f"Sample Points: {len(samples)}")

        # ----------------------------------------------------
        # Prefilter region boxes once per source region:
        # discard any box whose centre is beyond search_radius.
        # This shrinks the inner per-ray loop.
        # ----------------------------------------------------

        region_loc = region.location

        reachable_boxes = [
            box for box in region_boxes
            if (box[2] - region_loc).length_squared <= search_radius_sq
        ]

        print(f"Reachable regions: {len(reachable_boxes)}")

        # ----------------------------------------------------
        # Cast rays from all sample points
        # ----------------------------------------------------

        combined_hits = {}

        for sample in samples:

            hits = get_visible_regions_from_point(
                sample,
                bvh,
                region_boxes,
                rays_per_point,
                search_radius,
                reachable_boxes,
            )

            for region_name, count in hits.items():
                combined_hits[region_name] = (
                    combined_hits.get(region_name, 0) + count
                )

        # ----------------------------------------------------
        # Sort by strongest visibility, apply threshold
        # ----------------------------------------------------

        sorted_hits = sorted(
            combined_hits.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for region_name, count in sorted_hits:

            if count < min_hit_count:
                continue

            other = bpy.data.objects.get(region_name)

            if not other:
                continue

            if (
                other.location - region.location
            ).length > search_radius:
                continue

            if region_name in existing:
                continue

            item = vis.visible_regions.add()
            item.region_name = region_name
            existing.add(region_name)

        rebuild_vislist_range(region)

    print(f"\nLOS visibility computed for {len(regions)} regions.")