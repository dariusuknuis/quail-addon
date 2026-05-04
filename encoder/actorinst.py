import math
import bpy
from ..wce.actorinst import actorinst


def encode_actorinst(parser, obj) -> str:

    if obj.get("quaildef") != "actorinst":
        return ""

    props = obj.quail_actorinst

    # ------------------------------------------------
    # Create WCE object
    # ------------------------------------------------
    wce_inst = actorinst()

    # -------------------------
    # Tag
    # -------------------------
    wce_inst.tag = ""
    key = f"__actorinst_{len(parser.actorinsts)}"

    # -------------------------
    # Sprite (collection reference)
    # -------------------------
    if props.sprite:
        wce_inst.sprite = props.sprite.name
    else:
        name = obj.name.upper().split(".")[0]

        if name.endswith("_ACTORINST"):
            base = name[:-len("_ACTORINST")]
            wce_inst.sprite = f"{base}_ACTORDEF"
        else:
            wce_inst.sprite = ""

    # -------------------------
    # Current Action
    # -------------------------
    if props.has_currentaction:
        wce_inst.currentaction = str(props.currentaction)
    else:
        wce_inst.currentaction = None

    # -------------------------
    # Location (object → WCE)
    # -------------------------
    if props.has_location:

        loc = obj.location
        rot = obj.rotation_euler

        # convert radians → EQ units
        scale = 512.0 / (2 * math.pi)

        wce_inst.location = (
            float(loc.x),
            float(loc.y),
            float(loc.z),
            int(round(rot.z * scale)),
            int(round(rot.x * scale)),
            int(round(rot.y * scale)),
        )

    else:
        wce_inst.location = None

    # -------------------------
    # Bounding Radius
    # -------------------------
    if props.has_boundingradius:
        wce_inst.boundingradius = float(props.boundingradius)
    else:
        wce_inst.boundingradius = None

    # -------------------------
    # Scale Factor (object → WCE)
    # -------------------------
    if props.has_scalefactor:
        # uniform scale assumed
        wce_inst.scalefactor = float(obj.scale[0])
    else:
        wce_inst.scalefactor = None

    # -------------------------
    # Sound
    # -------------------------
    if props.has_sound:
        wce_inst.sound = props.sound
    else:
        wce_inst.sound = None

    # -------------------------
    # Active
    # -------------------------
    if props.has_active:
        wce_inst.active = int(props.active)
    else:
        wce_inst.active = None

    # -------------------------
    # RGB Track
    # -------------------------
    index = len(parser.actorinsts)

    if props.has_dmrgbtrack:

        new_name = f"ENT{index}_DMT"
        wce_inst.dmrgbtrack = new_name

        if not hasattr(parser, "_dmrgbtrack_map"):
            parser._dmrgbtrack_map = {}

        rgb_obj = next(
            (c for c in obj.children if c.get("quaildef") == "rgbdeformationtrackdef"),
            None
        )

        if rgb_obj:
            parser._dmrgbtrack_map[rgb_obj.name] = new_name

    else:
        wce_inst.dmrgbtrack = None

    # -------------------------
    # Required fields
    # -------------------------
    wce_inst.spritevolumeonly = 1 if props.spritevolumeonly else 0

    wce_inst.sphere = props.sphere or ""
    wce_inst.sphereradius = float(props.sphereradius)

    wce_inst.useboundingbox = 1 if props.useboundingbox else 0

    wce_inst.userdata = props.userdata or ""

    # ------------------------------------------------
    # Store in parser
    # ------------------------------------------------
    parser.actorinsts[key] = wce_inst

    return ""