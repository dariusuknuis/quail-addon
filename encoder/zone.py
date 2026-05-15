from ..wce.zone import zone

def encode_zone(parser, obj) -> str:

    if obj.get("quaildef") != "zone":
        return ""

    props = obj.quail_zone

    wce_zone = zone()

    # -------------------------
    # Basic fields
    # -------------------------
    wce_zone.tag = obj.name
    wce_zone.userdata = props.userdata

    # -------------------------
    # REGIONLIST
    # UI stores region tags: R000001, R000002, etc.
    # WCE stores: count, then zero-based region indices
    # -------------------------
    indices = []

    for item in props.regionlist:
        name = item.region_name

        if not name:
            continue

        if not name.startswith("R"):
            print(f"ZONE {obj.name}: skipping invalid region name {name}")
            continue

        try:
            idx = int(name[1:]) - 1
        except ValueError:
            print(f"ZONE {obj.name}: skipping invalid region name {name}")
            continue

        if idx < 0:
            print(f"ZONE {obj.name}: skipping invalid region index {name}")
            continue

        indices.append(idx)

    # keep panel order, but remove duplicates
    seen = set()
    ordered_indices = []

    for idx in indices:
        if idx in seen:
            continue

        seen.add(idx)
        ordered_indices.append(idx)

    wce_zone.regionlist = [str(len(ordered_indices))]

    for idx in ordered_indices:
        wce_zone.regionlist.append(str(idx))

    # -------------------------
    # Store in parser
    # -------------------------
    parser.zones[wce_zone.tag] = wce_zone

    return ""