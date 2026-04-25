import bpy
from ..wce.actordef import actordef

def encode_actordef(parser, obj) -> str:

    if obj.get("quaildef") != "actordef":
        return ""

    props = obj.quail_actordef

    # ------------------------------------------------
    # Create WCE object
    # ------------------------------------------------
    wce_actor = actordef()

    # -------------------------
    # Tag
    # -------------------------
    wce_actor.tag = obj.name

    # -------------------------
    # Basic fields
    # -------------------------
    wce_actor.callback = props.callback
    wce_actor.boundsref = props.boundsref

    # -------------------------
    # Current Action
    # -------------------------
    if props.has_currentaction:
        wce_actor.currentaction = int(props.currentaction)
    else:
        wce_actor.currentaction = None

    # -------------------------
    # Location (tuple[float, float, float, int, int, int] | None)
    # -------------------------
    if props.has_location:
        wce_actor.location = (
            float(props.loc_x),
            float(props.loc_y),
            float(props.loc_z),
            int(props.rot_x),
            int(props.rot_y),
            int(props.rot_z),
        )
    else:
        wce_actor.location = None

    # -------------------------
    # Active Geometry
    # NOTE:
    # Your panel stores this as BOOL
    # WCE expects STRING or NULL
    # -------------------------
    if props.activegeometry:
        # You may want to store a real tag later
        # For now match decoder behavior (flag-only)
        wce_actor.activegeometry = obj.name
    else:
        wce_actor.activegeometry = None

    # -------------------------
    # Sprite Volume Only
    # -------------------------
    wce_actor.spritevolumeonly = 1 if props.collider else 0

    # -------------------------
    # Userdata
    # -------------------------
    wce_actor.userdata = props.userdata

    # ------------------------------------------------
    # Actions
    # ------------------------------------------------
    wce_actor.actions = []

    for action in props.actions:

        act = actordef.action()
        a = act.action

        # unk1 (bool → int)
        a.unk1 = 1 if action.unk1 else 0

        a.levelsofdetails = []

        for lod in action.lods:

            lod_obj = actordef.action.action.levelofdetail()
            ld = lod_obj.levelofdetail

            # -------------------------
            # Sprite (object → tag)
            # -------------------------
            if lod.sprite:
                ld.sprite = lod.sprite.name
            else:
                ld.sprite = ""

            # -------------------------
            # Mindistance
            # -------------------------
            ld.mindistance = float(lod.mindistance)

            a.levelsofdetails.append(lod_obj)

        wce_actor.actions.append(act)

    # ------------------------------------------------
    # Store in parser
    # ------------------------------------------------
    parser.actordefs[wce_actor.tag] = wce_actor

    return ""