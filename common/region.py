import bpy, re, mathutils

REGION_MESH_PATTERN = re.compile(r"^R\d+_DMSPRITEDEF")

def create_world_bounds_from_regions(ctx, parser):

    regions = list(parser.regions.values())

    if not regions:
        print("No regions found.")
        return None

    # Only regions with spheres
    spheres = [r.sphere for r in regions if r.sphere is not None]

    if not spheres:
        print("No region spheres found.")
        return None

    # ----------------------------------------
    # Compute bounds
    # ----------------------------------------
    min_x = min(s[0] - s[3] for s in spheres)
    max_x = max(s[0] + s[3] for s in spheres)

    min_y = min(s[1] - s[3] for s in spheres)
    max_y = max(s[1] + s[3] for s in spheres)

    min_z = min(s[2] - s[3] for s in spheres)
    max_z = max(s[2] + s[3] for s in spheres)

    center = mathutils.Vector((
        (min_x + max_x) / 2,
        (min_y + max_y) / 2,
        (min_z + max_z) / 2
    ))

    extent_x = (max_x - min_x) / 2
    extent_y = (max_y - min_y) / 2
    extent_z = (max_z - min_z) / 2

    # ----------------------------------------
    # Create bounding empty
    # ----------------------------------------
    obj = bpy.data.objects.new("WORLD_BOUNDS", None)
    obj["quaildef"] = "worldbounds"

    obj.empty_display_type = 'CUBE'
    obj.location = center
    obj.empty_display_size = 1.0
    obj.scale = (extent_x, extent_y, extent_z)

    ctx.collection.objects.link(obj)

    print(f"Created WORLD_BOUNDS at {center} scale {obj.scale}")

    return obj

def encode_raw_pairs(indices):
    data = []
    for rid in indices:
        idx0 = rid - 1  # convert to 0-based
        data.append(idx0 & 0xFF)
        data.append((idx0 >> 8) & 0xFF)
    return data

def encode_vislist(regions):
    """Run-length encode a sorted 1-based region list into compact bytes."""
    if not regions:
        return []
    max_reg = regions[-1]
    groups = []
    cur = 1
    start = 1
    vis = (regions[0] == 1)
    while cur <= max_reg:
        is_vis = cur in regions
        if is_vis != vis:
            groups.append((vis, cur - start))
            vis = is_vis
            start = cur
        cur += 1
    groups.append((vis, cur - start))

    out = []
    i = 0
    while i < len(groups):
        vis_flag, cnt = groups[i]
        nxt = groups[i+1] if i+1 < len(groups) else (None, None)
        if vis_flag:
            # visible run
            if nxt[0] is False and cnt <= 7 and nxt[1] <= 7:
                out.append(0x80 | (cnt << 3) | nxt[1])
                i += 2
                continue
            elif cnt <= 62:
                out.append(0xC0 + cnt)
            else:
                out.extend([0xFF, cnt & 0xFF, (cnt >> 8) & 0xFF])
        else:
            # invisible run
            if nxt[0] is True and cnt <= 7 and nxt[1] <= 7:
                out.append(0x40 | (cnt << 3) | nxt[1])
                i += 2
                continue
            elif cnt <= 62:
                out.append(cnt)
            else:
                out.extend([0x3F, cnt & 0xFF, (cnt >> 8) & 0xFF])
        i += 1
    return out

def get_region_indices(vis):
    indices = []

    for item in vis.visible_regions:
        if not item.region:
            continue

        name = item.region.name
        if name.startswith("R"):
            try:
                idx = int(name[1:])
                indices.append(idx)
            except:
                pass

    return sorted(set(indices))

def is_region_mesh(tag: str) -> bool:
    return bool(REGION_MESH_PATTERN.match(tag))


def is_zone_collection(collection) -> bool:
    if not collection:
        return False

    props = getattr(collection, "quail_worlddef", None)
    return bool(props and props.zone)

def decode_vislist(vislistbytes, ranges):
    regions = []
    current = 1

    i = 0
    while i < len(ranges):
        b = ranges[i]

        if vislistbytes:
            if b <= 0x3E:
                current += b

            elif b == 0x3F:
                count = (ranges[i+2] << 8) | ranges[i+1]
                current += count
                i += 2

            elif 0x40 <= b <= 0x7F:
                skip = (b & 0b00111000) >> 3
                take = b & 0b00000111
                current += skip
                for _ in range(take):
                    regions.append(current)
                    current += 1

            elif 0x80 <= b <= 0xBF:
                take = (b & 0b00111000) >> 3
                for _ in range(take):
                    regions.append(current)
                    current += 1
                current += (b & 0b00000111)

            elif 0xC0 <= b <= 0xFE:
                take = b - 0xC0
                for _ in range(take):
                    regions.append(current)
                    current += 1

            elif b == 0xFF:
                count = (ranges[i+2] << 8) | ranges[i+1]
                for _ in range(count):
                    regions.append(current)
                    current += 1
                i += 2

            i += 1

        else:
            idx = (ranges[i+1] << 8) | ranges[i]
            regions.append(idx + 1)
            i += 2
            continue

    return regions

def resolve_region_visibility():

    region_objs = [
        o for o in bpy.data.objects
        if o.get("quaildef") == "region"
    ]

    for obj in region_objs:
        props = obj.quail_region

        for vis in props.vislists:

            if not vis.range:
                continue

            # convert string → ints
            try:
                parts = [int(x) for x in vis.range.split()]
                num_ranges = parts[0]
                ranges = parts[1:]
            except:
                continue

            indices = decode_vislist(
                props.vislistbytes,
                ranges
            )

            # clear
            while len(vis.visible_regions) > 0:
                vis.visible_regions.remove(0)

            # assign references
            region_map = {}

            for o in region_objs:
                name = o.name
                if name.startswith("R"):
                    try:
                        idx = int(name[1:])
                        region_map[idx] = o
                    except:
                        pass

            for idx in indices:
                obj = region_map.get(idx)
                if obj:
                    ref = vis.visible_regions.add()
                    ref.region_name = obj.name