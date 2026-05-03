from ..wce.rgbdeformationtrackdef import rgbdeformationtrackdef


def encode_rgbdeformationtrackdef(parser, obj) -> str:

    if obj.get("quaildef") != "rgbdeformationtrackdef":
        return ""

    # -------------------------
    # Remap name
    # -------------------------
    new_name = parser._dmrgbtrack_map.get(obj.name)
    if not new_name:
        return ""  # not referenced by any actorinst

    props = obj.quail_rgbdeformationtrackdef
    mesh = obj.data

    # -------------------------
    # Create WCE object
    # -------------------------
    wce_track = rgbdeformationtrackdef()
    wce_track.tag = new_name

    wce_track.sleep = int(props.sleep)
    wce_track.data4 = int(props.data4)
    wce_track.usealpha = 1 if props.usealpha else 0

    # -------------------------
    # Frames
    # -------------------------
    wce_track.rgbdeformationframes = []

    # only frame 0 for now (matches your decoder)
    attr_name = "rgbatrack_000"
    attr = mesh.attributes.get(attr_name)

    if not attr:
        return ""  # no data

    frame = rgbdeformationtrackdef.numrgbas()

    for v in mesh.vertices:
        rgba = rgbdeformationtrackdef.numrgbas.rgba()

        c = attr.data[v.index].color

        r = int(c[0] * 255)
        g = int(c[1] * 255)
        b = int(c[2] * 255)
        a = int(c[3] * 255) if props.usealpha else 255

        rgba.rgba = (r, g, b, a)
        frame.rgbas.append(rgba)

    wce_track.rgbdeformationframes.append(frame)

    # -------------------------
    # Store
    # -------------------------
    parser.rgbdeformationtrackdefs[wce_track.tag] = wce_track

    return ""