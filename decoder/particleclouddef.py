# pyright: basic, reportGeneralTypeIssues=false

import bpy

from ..wce.particleclouddef import particleclouddef
from .context import Context
from ..common.s3dparticle import apply_particlecloud_settings, apply_particlecloud_blit, apply_particlecloud_visuals


def decode_particleclouddef(ctx: Context, cloud: particleclouddef) -> str:

    # ------------------------------------------------
    # Already exists
    # ------------------------------------------------

    if cloud.tag in bpy.data.objects:
        return ""

    # ------------------------------------------------
    # Create emitter object
    # ------------------------------------------------

    emitter_mesh = bpy.data.meshes.new(cloud.tag)
    emitter_mesh.from_pydata(
        [(0.0, 0.0, 0.0)],
        [],
        []
    )

    emitter_mesh.update()

    obj = bpy.data.objects.new(
        cloud.tag,
        emitter_mesh
    )

    ctx.collection.objects.link(obj)

    obj["quaildef"] = "particleclouddef"

    # ------------------------------------------------
    # Property group
    # ------------------------------------------------

    props = obj.quail_particleclouddef
    props.particletype = cloud.particletype
    props.movement = cloud.movement
    props.size = cloud.size
    props.gravity = cloud.gravity
    props.spawnnormal = cloud.spawnnormal
    props.duration = cloud.duration
    props.spawnradius = cloud.spawnradius
    props.spawnangle = cloud.spawnangle
    props.lifespan = cloud.lifespan
    props.spawnvelocitymultiplier = (cloud.spawnvelocitymultiplier)
    props.spawnvelocity = cloud.spawnvelocity
    props.spawnrate = cloud.spawnrate
    props.spawnscale = cloud.spawnscale
    props.tint = (
        cloud.tint[0] / 255.0,
        cloud.tint[1] / 255.0,
        cloud.tint[2] / 255.0,
        cloud.tint[3] / 255.0,
    )

    # ------------------------------------------------
    # Nullable spawn box
    # ------------------------------------------------

    if cloud.spawnboxmin and cloud.spawnboxmax:

        props.has_spawnbox = True
        props.spawnboxmin = cloud.spawnboxmin
        props.spawnboxmax = cloud.spawnboxmax

    else:

        props.has_spawnbox = False

    # ------------------------------------------------
    # Nullable box
    # ------------------------------------------------

    if cloud.boxmin and cloud.boxmax:

        props.has_box = True
        props.boxmin = cloud.boxmin
        props.boxmax = cloud.boxmax

    else:

        props.has_box = False

    # ------------------------------------------------
    # Flags
    # ------------------------------------------------

    props.usesprite = bool(cloud.usesprite)
    props.free = bool(cloud.free)
    props.collision = bool(cloud.collision)
    props.respawn = bool(cloud.respawn)
    props.viewrelx = bool(cloud.viewrelx)
    props.viewrely = bool(cloud.viewrely)
    props.viewrelz = bool(cloud.viewrelz)
    props.viewwarp = bool(cloud.viewwarp)
    props.brownian = bool(cloud.brownian)
    props.fade = bool(cloud.fade)
    props.boundingbox = bool(cloud.boundingbox)
    props.updatebbox = bool(cloud.updatebbox)
    props.pointgravity = bool(cloud.pointgravity)
    props.gravityflag = bool(cloud.gravityflag)
    props.freedef = bool(cloud.freedef)
    props.objectrelative = bool(cloud.objectrelative)
    props.parentobjrelative = bool(cloud.parentobjrelative)
    props.spawnscalerelative = bool(cloud.spawnscalerelative)
    props.hidewithspawnobject = bool(cloud.hidewithspawnobject)

    # ------------------------------------------------
    # Resolve blittag
    # ------------------------------------------------

    if cloud.blittag:
        source_blit = bpy.data.objects.get(cloud.blittag)

        if source_blit:
            props.blittag = source_blit

    # ------------------------------------------------
    # Particle System
    # ------------------------------------------------

    modifier = obj.modifiers.new(
        name=cloud.tag,
        type='PARTICLE_SYSTEM'
    )

    psys = modifier.particle_system

    settings = bpy.data.particles.new(
        cloud.tag
    )

    psys.settings = settings

    # ------------------------------------------------
    # Apply helpers
    # ------------------------------------------------

    apply_particlecloud_blit(obj)

    apply_particlecloud_settings(obj)

    apply_particlecloud_visuals(obj)

    # ------------------------------------------------
    # Hide helper object
    # ------------------------------------------------

    obj.hide_set(True)

    return ""