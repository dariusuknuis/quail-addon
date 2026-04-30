from ..wce.region import region

def encode_region(parser, obj) -> str:

    if obj.get("quaildef") != "region":
        return ""

    props = obj.quail_region

    wce_region = region()

    # -------------------------
    # Basic fields
    # -------------------------
    wce_region.tag = obj.name

    wce_region.reverbvolume = props.reverbvolume if props.has_reverbvolume else None
    wce_region.reverboffset = props.reverboffset if props.has_reverboffset else None

    wce_region.regionfog = 1 if props.regionfog else 0
    wce_region.gourand2 = 1 if props.gouraud2 else 0
    wce_region.encodedvisibility = 1 if props.encodedvisibility else 0
    wce_region.vislistbytes = 1 if props.vislistbytes else 0

    # -------------------------
    # Sphere
    # -------------------------
    if props.has_sphere:
        wce_region.sphere = (
            props.sphere_x,
            props.sphere_y,
            props.sphere_z,
            props.sphere_r
        )
    else:
        wce_region.sphere = None

    # -------------------------
    # Userdata / sprite
    # -------------------------
    wce_region.userdata = props.userdata
    wce_region.sprite = props.sprite if props.has_sprite else None

    # ------------------------------------------------
    # VISNODES
    # ------------------------------------------------
    wce_region.visnodes = []

    for vn in props.visnodes:
        node = region.visnode()

        node.vnormalabcd = (
            vn.normal_x,
            vn.normal_y,
            vn.normal_z,
            vn.normal_w,
        )

        node.vislistindex = vn.vislistindex
        node.fronttree = vn.fronttree
        node.backtree = vn.backtree

        wce_region.visnodes.append(node)

    # ------------------------------------------------
    # VISLISTS (USE STORED RANGE DIRECTLY)
    # ------------------------------------------------
    wce_region.visiblelists = []

    for vis in props.vislists:

        vislist = region.vislist()

        if not vis.range:
            vislist.range = []
        else:
            # already formatted: "num_ranges byte0 byte1 ..."
            vislist.range = vis.range.split()

        wce_region.visiblelists.append(vislist)

    # ------------------------------------------------
    # Store in parser
    # ------------------------------------------------
    parser.regions[wce_region.tag] = wce_region

    return ""