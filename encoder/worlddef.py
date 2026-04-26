from ..wce.worlddef import worlddef

def encode_worlddef(parser, collection) -> str:

    if not collection or collection.get("quaildef") != "worlddef":
        return ""

    props = collection.quail_worlddef

    # ------------------------------------------------
    # Create WCE object
    # ------------------------------------------------
    wce = worlddef()

    # ----------------------------------------
    # NewWorld (bool → int)
    # ----------------------------------------
    wce.newworld = 1 if props.newworld else 0

    # ----------------------------------------
    # Zone (bool → int)
    # ----------------------------------------
    wce.zone = 1 if props.zone else 0

    # ----------------------------------------
    # Optional EQG
    # ----------------------------------------
    if props.use_eqg:
        wce.eqgversion = props.eqgversion
    else:
        wce.eqgversion = None

    # ------------------------------------------------
    # Store on parser (single, not dict)
    # ------------------------------------------------
    parser.worlddef = wce

    return ""