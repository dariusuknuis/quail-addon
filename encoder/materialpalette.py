from ..wce.materialpalette import materialpalette

def encode_materialpalette(parser, obj) -> str:

    if obj.get("quaildef") != "materialpalette":
        return ""

    props = obj.quail_materialpalette

    # ------------------------------------------------
    # Create WCE object
    # ------------------------------------------------
    wce = materialpalette()

    # -------------------------
    # Tag
    # -------------------------
    # Prefer panel tag if set, fallback to object name
    wce.tag = props.tag if props.tag else obj.name

    # -------------------------
    # Materials
    # -------------------------
    wce.materials = []

    for item in props.materials:

        # Skip empty slots (important)
        if not item.material:
            continue

        m = materialpalette.material()

        # Blender Material → tag string
        m.material = item.material.name

        wce.materials.append(m)

    # ------------------------------------------------
    # Store in parser
    # ------------------------------------------------
    parser.materialpalettes[wce.tag] = wce

    return ""