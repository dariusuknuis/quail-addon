import bpy
from ..wce.hierarchicalspritedef import hierarchicalspritedef


def encode_hierarchicalspritedef(parser, obj) -> str:

    if obj.get("quaildef") != "hierarchicalspritedef":
        return ""

    props = obj.quail_hierarchicalspritedef

    # ------------------------------------------------
    # Create WCE object
    # ------------------------------------------------
    wce = hierarchicalspritedef()

    # -------------------------
    # Tag
    # -------------------------
    wce.tag = obj.name

    # -------------------------
    # DAGs
    # -------------------------
    wce.dags = []

    for dag in props.dags:

        d = hierarchicalspritedef.dag()

        # TAG
        d.tag = dag.tag

        # SPRITETAG (object → tag)
        if dag.spritetag:
            d.spritetag = dag.spritetag.name
        else:
            d.spritetag = ""

        # TRACK
        d.track = dag.track or ""

        # SUBDAGLIST
        if len(dag.subdags) > 0:
            indices = [str(sub.dag_index) for sub in dag.subdags]
            d.subdaglist = [str(len(indices))] + indices
        else:
            d.subdaglist = ["0"]

        wce.dags.append(d)

    # -------------------------
    # Attached Skins
    # -------------------------
    wce.attachedskins = []

    if props.haveattachedskins:
        for skin in props.attachedskins:

            s = hierarchicalspritedef.attachedskin()

            if skin.dmsprite:
                s.dmsprite = skin.dmsprite.name
            else:
                s.dmsprite = ""

            s.linkskinupdatestodagindex = int(skin.linkdagindex)

            wce.attachedskins.append(s)

        wce.haveattachedskins = 1
    else:
        wce.haveattachedskins = 0

    # -------------------------
    # Polyhedron (SPRITE field)
    # -------------------------
    if props.polyhedron:
        wce.sprite = props.polyhedron.name
    else:
        wce.sprite = ""

    # -------------------------
    # Center Offset
    # -------------------------
    if props.has_centeroffset:
        wce.centeroffset = (
            float(props.center_x),
            float(props.center_y),
            float(props.center_z),
        )
    else:
        wce.centeroffset = None

    # -------------------------
    # Bounding Radius
    # -------------------------
    if props.has_boundingradius:
        wce.boundingradius = float(props.boundingradius)
    else:
        wce.boundingradius = None

    # -------------------------
    # DAG Collisions
    # -------------------------
    wce.dagcollisions = 1 if props.dagcollisions else 0

    # ------------------------------------------------
    # Store in parser
    # ------------------------------------------------
    parser.hierarchicalspritedefs[wce.tag] = wce

    return ""