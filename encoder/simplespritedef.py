from ..wce.simplespritedef import simplespritedef

def build_simplesprite_file_string(file) -> str:

    if not file.file_name:
        return ""

    name = file.file_name

    # BASE
    if file.file_index == 0:
        return name

    mode = file.texture_mode

    # LAYER
    if mode == 'LAYER':
        return f"{name}_LAYER"

    # DETAIL
    if mode == 'DETAIL':
        return f"{name}_DETAIL_{file.scale}"

    # PALETTE
    if mode == 'PALETTE':
        return name

    # TILED
    if mode == 'TILED':
        return f"{file.palette_index}, {file.scale}, {file.blend}, {name}"

    return name

def encode_simplespritedef(parser, tree) -> str:

    # NodeTree, not Object
    if not tree or tree.get("quaildef") != "simplespritedef":
        return ""

    props = tree.quail_simplesprite

    # ------------------------------------------------
    # Create WCE object
    # ------------------------------------------------
    wce = simplespritedef()

    # -------------------------
    # Tag
    # -------------------------
    wce.tag = tree.name

    # -------------------------
    # Variation (not exposed → default)
    # -------------------------
    wce.variation = 0

    # -------------------------
    # SkipFrames (bool → int)
    # -------------------------
    wce.skipframes = 1 if props.skipframes else 0

    # -------------------------
    # Sleep
    # -------------------------
    if props.has_sleep:
        wce.sleep = int(props.sleep)
    else:
        wce.sleep = None

    # -------------------------
    # Current Frame
    # -------------------------
    if props.has_current_frame:
        wce.currentframe = int(props.current_frame)
    else:
        wce.currentframe = None

    # -------------------------
    # Frames
    # -------------------------
    wce.frames = []

    for frame in props.frames:

        f = simplespritedef.frame()

        # FRAME name
        f.frame = frame.frame_name if frame.frame_name else f"Frame_{frame.frame_id}"

        f.files = []

        for file in frame.files:

            file_str = build_simplesprite_file_string(file)

            if not file_str:
                continue

            ff = simplespritedef.frame.file()
            ff.file = file_str

            f.files.append(ff)

        wce.frames.append(f)

    # ------------------------------------------------
    # Store in parser
    # ------------------------------------------------
    parser.simplespritedefs[wce.tag] = wce

    return ""