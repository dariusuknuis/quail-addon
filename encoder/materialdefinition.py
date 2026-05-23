from ..wce.materialdefinition import materialdefinition
from ..common.rendermethod import build_rendermethod_string


def encode_materialdefinition(parser, mat) -> str:

    if mat.get("quaildef") != "materialdefinition":
        return ""

    props = mat.quail_materialdefinition

    # ------------------------------------------------
    # Create WCE object
    # ------------------------------------------------
    wce = materialdefinition()

    # -------------------------
    # Tag
    # -------------------------
    wce.tag = mat.name

    # -------------------------
    # Variation
    # -------------------------
    wce.variation = int(props.variation)

    # -------------------------
    # RenderMethod (rebuild string)
    # -------------------------
    wce.rendermethod = build_rendermethod_string(props)

    # -------------------------
    # RGBPEN (float 0–1 → int 0–255)
    # -------------------------
    r, g, b = props.rgbpen
    wce.rgbpen = (
        int(r * 255),
        int(g * 255),
        int(b * 255),
        0  # alpha channel always 0 in your format
    )

    # -------------------------
    # Brightness / Ambient
    # -------------------------
    wce.brightness = float(props.brightness)
    wce.scaledambient = float(props.scaledambient)

    # -------------------------
    # SimpleSpriteInst
    # -------------------------
    inst = wce.simplespriteinst

    if props.simplespritetag and props.simplespritetag != "NONE":
        inst.simplespritetag = props.simplespritetag
    else:
        inst.simplespritetag = ""

    inst.simplespritehaveskipframes = 1 if props.simplespritehaveskipframes else 0
    inst.simplespriteskipframes = 1 if props.simplespriteskipframes else 0

    # -------------------------
    # UV Shift
    # -------------------------
    if not props.has_uvshiftperms:
        wce.uvshiftperms = None
    else:
        u, v = props.uvshiftperms
        wce.uvshiftperms = (float(u), float(v))

    # -------------------------
    # Two-sided
    # -------------------------
    wce.twosided = 1 if props.twosided else 0

    # ------------------------------------------------
    # Store in parser
    # ------------------------------------------------
    parser.materialdefinitions[wce.tag] = wce

    return ""