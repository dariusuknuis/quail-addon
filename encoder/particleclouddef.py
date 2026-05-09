# pyright: basic, reportGeneralTypeIssues=false

import bpy

from ..wce.particleclouddef import particleclouddef


def encode_particleclouddef(parser, obj) -> str:

    if obj.get("quaildef") != "particleclouddef":
        return ""

    props = obj.quail_particleclouddef

    wce_cloud = particleclouddef()

    # ------------------------------------------------
    # Tag
    # ------------------------------------------------

    wce_cloud.tag = obj.name

    # ------------------------------------------------
    # Blit
    # ------------------------------------------------

    wce_cloud.blittag = (
        props.blittag.name
        if props.blittag
        else ""
    )

    # ------------------------------------------------
    # Core
    # ------------------------------------------------

    wce_cloud.particletype = int(
        props.particletype
    )

    wce_cloud.movement = str(
        props.movement
    )

    wce_cloud.size = int(
        props.size
    )

    wce_cloud.gravity = float(
        props.gravity
    )

    wce_cloud.spawnnormal = (
        float(props.spawnnormal[0]),
        float(props.spawnnormal[1]),
        float(props.spawnnormal[2]),
    )

    wce_cloud.duration = int(
        props.duration
    )

    wce_cloud.spawnradius = float(
        props.spawnradius
    )

    wce_cloud.spawnangle = float(
        props.spawnangle
    )

    wce_cloud.lifespan = int(
        props.lifespan
    )

    wce_cloud.spawnvelocitymultiplier = float(
        props.spawnvelocitymultiplier
    )

    wce_cloud.spawnvelocity = (
        float(props.spawnvelocity[0]),
        float(props.spawnvelocity[1]),
        float(props.spawnvelocity[2]),
    )

    wce_cloud.spawnrate = int(
        props.spawnrate
    )

    wce_cloud.spawnscale = float(
        props.spawnscale
    )

    # ------------------------------------------------
    # Tint
    # ------------------------------------------------

    wce_cloud.tint = (
        int(props.tint[0] * 255),
        int(props.tint[1] * 255),
        int(props.tint[2] * 255),
        int(props.tint[3] * 255),
    )

    # ------------------------------------------------
    # Nullable Spawn Box
    # ------------------------------------------------

    if props.has_spawnbox:

        wce_cloud.spawnboxmin = (
            float(props.spawnboxmin[0]),
            float(props.spawnboxmin[1]),
            float(props.spawnboxmin[2]),
        )

        wce_cloud.spawnboxmax = (
            float(props.spawnboxmax[0]),
            float(props.spawnboxmax[1]),
            float(props.spawnboxmax[2]),
        )

    else:

        wce_cloud.spawnboxmin = None
        wce_cloud.spawnboxmax = None

    # ------------------------------------------------
    # Nullable Box
    # ------------------------------------------------

    if props.has_box:

        wce_cloud.boxmin = (
            float(props.boxmin[0]),
            float(props.boxmin[1]),
            float(props.boxmin[2]),
        )

        wce_cloud.boxmax = (
            float(props.boxmax[0]),
            float(props.boxmax[1]),
            float(props.boxmax[2]),
        )

    else:

        wce_cloud.boxmin = None
        wce_cloud.boxmax = None

    # ------------------------------------------------
    # Flags
    # ------------------------------------------------

    wce_cloud.usesprite = (
        1 if props.usesprite else 0
    )

    wce_cloud.free = (
        1 if props.free else 0
    )

    wce_cloud.collision = (
        1 if props.collision else 0
    )

    wce_cloud.respawn = (
        1 if props.respawn else 0
    )

    wce_cloud.viewrelx = (
        1 if props.viewrelx else 0
    )

    wce_cloud.viewrely = (
        1 if props.viewrely else 0
    )

    wce_cloud.viewrelz = (
        1 if props.viewrelz else 0
    )

    wce_cloud.viewwarp = (
        1 if props.viewwarp else 0
    )

    wce_cloud.brownian = (
        1 if props.brownian else 0
    )

    wce_cloud.fade = (
        1 if props.fade else 0
    )

    wce_cloud.boundingbox = (
        1 if props.boundingbox else 0
    )

    wce_cloud.updatebbox = (
        1 if props.updatebbox else 0
    )

    wce_cloud.pointgravity = (
        1 if props.pointgravity else 0
    )

    wce_cloud.gravityflag = (
        1 if props.gravityflag else 0
    )

    wce_cloud.freedef = (
        1 if props.freedef else 0
    )

    wce_cloud.objectrelative = (
        1 if props.objectrelative else 0
    )

    wce_cloud.parentobjrelative = (
        1 if props.parentobjrelative else 0
    )

    wce_cloud.spawnscalerelative = (
        1 if props.spawnscalerelative else 0
    )

    wce_cloud.hidewithspawnobject = (
        1 if props.hidewithspawnobject else 0
    )

    # ------------------------------------------------
    # Store
    # ------------------------------------------------

    parser.particleclouddefs[
        wce_cloud.tag
    ] = wce_cloud

    return ""