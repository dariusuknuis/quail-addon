# pyright: basic, reportGeneralTypeIssues=false

import bpy
import mathutils
from ..wce.particleclouddef import particleclouddef
from .context import Context


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
    # Store raw properties
    # ------------------------------------------------

    obj["blittag"] = cloud.blittag
    obj["particletype"] = cloud.particletype
    obj["movement"] = cloud.movement
    obj["size"] = cloud.size
    obj["gravity"] = cloud.gravity
    obj["duration"] = cloud.duration
    obj["spawnradius"] = cloud.spawnradius
    obj["spawnangle"] = cloud.spawnangle
    obj["lifespan"] = cloud.lifespan
    obj["spawnvelocitymultiplier"] = cloud.spawnvelocitymultiplier
    obj["spawnrate"] = cloud.spawnrate
    obj["spawnscale"] = cloud.spawnscale
    obj["spawnvelocity"] = cloud.spawnvelocity
    obj["spawnnormal"] = cloud.spawnnormal

    # ------------------------------------------------
    # Resolve blittag
    # ------------------------------------------------

    blit_obj = None

    if cloud.blittag:
        blit_obj = bpy.data.objects.get(cloud.blittag)

    # ------------------------------------------------
    # Particle Settings
    # ------------------------------------------------

    modifier = obj.modifiers.new(
        name=cloud.tag,
        type='PARTICLE_SYSTEM'
    )

    psys = modifier.particle_system

    settings = bpy.data.particles.new(cloud.tag)

    psys.settings = settings

    # ------------------------------------------------
    # FPS conversion
    # ------------------------------------------------

    fps = bpy.context.scene.render.fps

    lifespan_seconds = max(
        cloud.lifespan / 1000.0,
        0.001
    )

    lifetime_frames = max(
        lifespan_seconds * fps,
        1.0
    )

    spawn_interval_frames = max(
        (cloud.spawnrate / 1000.0) * fps,
        1.0
    )

    # ------------------------------------------------
    # Core
    # ------------------------------------------------

    settings.count = max(cloud.size, 1)

    settings.frame_start = 1

    # Emit particles gradually based on EQ SpawnRate
    settings.frame_end = (
        settings.frame_start +
        (spawn_interval_frames * max(cloud.size - 1, 0))
    )

    # EQ lifespan -> Blender frames
    settings.lifetime = lifetime_frames

    settings.physics_type = 'NEWTON'

    settings.use_modifier_stack = True

    # EQ behaves more deterministic
    settings.use_emit_random = False

    settings.distribution = 'RAND'

    settings.particle_size = max(
        cloud.spawnscale,
        0.001
    )

    # ------------------------------------------------
    # Particle Types
    # ------------------------------------------------

    # ------------------------------------------------
    # Type 1 / 2
    # Point / trail particles
    # ------------------------------------------------

    if cloud.particletype in (1, 2):

        settings.render_type = 'HALO'

        settings.halo.size = max(
            cloud.spawnscale,
            0.01
        )

    # ------------------------------------------------
    # Type 3 / 4
    # Billboard blitsprites
    # ------------------------------------------------

    elif cloud.particletype in (3, 4):

        settings.render_type = 'OBJECT'

        if blit_obj:
            settings.instance_object = blit_obj

        settings.use_rotation_instance = True

        # Type 4 is XY aligned in EQ
        if cloud.particletype == 4:
            settings.rotation_mode = 'GLOB_Z'

    # ------------------------------------------------
    # Spawn Type
    # ------------------------------------------------

    # BOX
    if cloud.movement == "BOX":

        settings.emit_from = 'VOLUME'

    # SPHERE
    elif cloud.movement == "SPHERE":

        settings.emit_from = 'VOLUME'

    # PLANE
    elif cloud.movement == "PLANE":

        settings.emit_from = 'FACE'

    # STREAM
    elif cloud.movement == "STREAM":

        settings.emit_from = 'VERT'

    # DISK
    elif cloud.movement == "DISK":

        settings.emit_from = 'FACE'

    else:

        settings.emit_from = 'VERT'

    # ------------------------------------------------
    # Spawn Normal (EQ "up direction")
    # ------------------------------------------------

    spawn_normal = mathutils.Vector(cloud.spawnnormal)

    settings.object_align_factor[0] = spawn_normal.x
    settings.object_align_factor[1] = spawn_normal.y
    settings.object_align_factor[2] = spawn_normal.z

    # ------------------------------------------------
    # Velocity
    # ------------------------------------------------

    vel = mathutils.Vector(cloud.spawnvelocity)

    # ------------------------------------------------
    # BOX
    # Random spawn position in volume
    # Directional movement from SpawnVelocity
    # ------------------------------------------------

    if cloud.movement == "BOX":

        velocity = vel * cloud.spawnvelocitymultiplier

        settings.normal_factor = velocity.length

        if velocity.length > 0.0:

            velocity.normalize()

            settings.object_align_factor[0] = velocity.x
            settings.object_align_factor[1] = velocity.y
            settings.object_align_factor[2] = velocity.z

        settings.factor_random = 0.0

    # ------------------------------------------------
    # SPHERE
    # Random direction
    # Speed ONLY from SpawnVelocityMultiplier
    # Ignore XYZ SpawnVelocity
    # ------------------------------------------------

    elif cloud.movement == "SPHERE":

        settings.normal_factor = 0.0

        settings.object_align_factor[0] = 0.0
        settings.object_align_factor[1] = 0.0
        settings.object_align_factor[2] = 0.0

        settings.factor_random = (
            cloud.spawnvelocitymultiplier
        )

    # ------------------------------------------------
    # PLANE
    # Random planar movement from SpawnVelocity
    # SpawnVelocityMultiplier alone does nothing
    # ------------------------------------------------

    elif cloud.movement == "PLANE":

        settings.normal_factor = vel.length

        if vel.length > 0.0:

            velocity = vel.normalized()

            settings.object_align_factor[0] = velocity.x
            settings.object_align_factor[1] = velocity.y
            settings.object_align_factor[2] = velocity.z

        settings.factor_random = 1.0

    # ------------------------------------------------
    # STREAM
    # Directional movement from SpawnVelocity
    # SpawnVelocityMultiplier scales velocity
    # SpawnAngle controls spread
    # ------------------------------------------------

    elif cloud.movement == "STREAM":

        velocity = vel * cloud.spawnvelocitymultiplier

        settings.normal_factor = velocity.length

        if velocity.length > 0.0:

            velocity.normalize()

            settings.object_align_factor[0] = velocity.x
            settings.object_align_factor[1] = velocity.y
            settings.object_align_factor[2] = velocity.z

        settings.factor_random = max(
            min(cloud.spawnangle / 90.0, 1.0),
            0.0
        )

    # ------------------------------------------------
    # DISK
    # Spawn randomly on disk surface
    # Directional movement from SpawnVelocity
    # SpawnVelocityMultiplier alone does nothing
    # ------------------------------------------------

    elif cloud.movement == "DISK":

        settings.normal_factor = vel.length

        if vel.length > 0.0:

            velocity = vel.normalized()

            settings.object_align_factor[0] = velocity.x
            settings.object_align_factor[1] = velocity.y
            settings.object_align_factor[2] = velocity.z

        settings.factor_random = 0.0

    # ------------------------------------------------
    # Fallback
    # ------------------------------------------------

    else:

        settings.normal_factor = 0.0
        settings.factor_random = 0.0

    # ------------------------------------------------
    # Gravity
    # ------------------------------------------------

    # EQ uses actual acceleration values
    # Blender uses Earth gravity scale multiplier

    if cloud.movement in {
        "BOX",
        "SPHERE",
        "PLANE",
        "STREAM",
        "DISK",
    }:

        settings.effector_weights.gravity = (
            cloud.gravity / 9.81
        )

    else:

        settings.effector_weights.gravity = 0.0

    # ------------------------------------------------
    # Spawn Radius
    # ------------------------------------------------

    if cloud.spawnradius > 0.0:

        obj.empty_display_size = cloud.spawnradius

    # ------------------------------------------------
    # Brownian
    # ------------------------------------------------

    if cloud.brownian:

        settings.brownian_factor = 1.0

    # ------------------------------------------------
    # Fade
    # ------------------------------------------------

    if cloud.fade:

        # Fade over lifetime
        settings.use_rotations = False

    # ------------------------------------------------
    # Object Relative
    # ------------------------------------------------

    if cloud.objectrelative:

        settings.use_rotations = True

    # ------------------------------------------------
    # Spawn boxes
    # ------------------------------------------------

    if cloud.spawnboxmin and cloud.spawnboxmax:

        obj["spawnboxmin"] = cloud.spawnboxmin
        obj["spawnboxmax"] = cloud.spawnboxmax

    if cloud.boxmin and cloud.boxmax:

        obj["boxmin"] = cloud.boxmin
        obj["boxmax"] = cloud.boxmax

    # ------------------------------------------------
    # Visual helper mesh scaling
    # ------------------------------------------------

    if cloud.movement == "BOX":

        if cloud.spawnboxmin and cloud.spawnboxmax:

            minv = mathutils.Vector(cloud.spawnboxmin)
            maxv = mathutils.Vector(cloud.spawnboxmax)

            center = (minv + maxv) * 0.5
            scale = (maxv - minv) * 0.5

            obj.location = center
            obj.scale = scale

    elif cloud.spawnradius > 0.0:

        obj.scale = (
            cloud.spawnradius,
            cloud.spawnradius,
            cloud.spawnradius
        )

    return ""