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

        source_blit = bpy.data.objects.get(cloud.blittag)

        if source_blit:

            # ----------------------------------------
            # Duplicate object
            # ----------------------------------------

            blit_obj = source_blit.copy()

            blit_obj.data = source_blit.data.copy()

            blit_obj.name = f"{cloud.tag}_BLIT"

            ctx.collection.objects.link(blit_obj)

            # ----------------------------------------
            # Tint color
            # ----------------------------------------

            tint = (
                cloud.tint[0] / 255.0,
                cloud.tint[1] / 255.0,
                cloud.tint[2] / 255.0,
                cloud.tint[3] / 255.0,
            )

            # ----------------------------------------
            # Copy materials
            # ----------------------------------------

            for i, mat in enumerate(blit_obj.data.materials):

                if not mat:
                    continue

                new_mat = mat.copy()

                new_mat.name = f"{cloud.tag}_{mat.name}"

                blit_obj.data.materials[i] = new_mat

                if not new_mat.use_nodes:
                    continue

                if not new_mat.node_tree:
                    continue

                # ------------------------------------
                # Find RENDERMETHOD node
                # ------------------------------------

                for node in new_mat.node_tree.nodes:

                    if (
                        node.type == 'GROUP' and
                        node.node_tree and
                        node.node_tree.name == "RENDERMETHOD"
                    ):

                        if "Particle Tint" in node.inputs:

                            node.inputs["Particle Tint"].default_value = tint

            # ----------------------------------------
            # Hide helper object
            # ----------------------------------------

            # blit_obj.hide_viewport = True
            # blit_obj.hide_render = True

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

    settings.frame_end = (
        settings.frame_start +
        (spawn_interval_frames * max(cloud.size - 1, 0))
    )

    settings.lifetime = lifetime_frames

    settings.physics_type = 'NEWTON'

    settings.use_modifier_stack = True

    settings.use_emit_random = False

    settings.distribution = 'RAND'

    settings.particle_size = max(
        cloud.spawnscale,
        0.001
    )

    # ------------------------------------------------
    # Particle Types
    # ------------------------------------------------

    if cloud.particletype in (1, 2):

        settings.render_type = 'HALO'

        settings.halo.size = max(
            cloud.spawnscale,
            0.01
        )

    elif cloud.particletype in (3, 4):

        settings.render_type = 'OBJECT'

        if blit_obj:
            settings.instance_object = blit_obj

        settings.use_rotation_instance = True

        if cloud.particletype == 4:
            settings.rotation_mode = 'GLOB_Z'

    # ------------------------------------------------
    # Spawn Type
    # ------------------------------------------------

    if cloud.movement == "BOX":

        settings.emit_from = 'VOLUME'

    elif cloud.movement == "SPHERE":

        settings.emit_from = 'VOLUME'

    elif cloud.movement == "PLANE":

        settings.emit_from = 'FACE'

    elif cloud.movement == "STREAM":

        settings.emit_from = 'VERT'

    elif cloud.movement == "DISK":

        settings.emit_from = 'FACE'

    else:

        settings.emit_from = 'VERT'

    # ------------------------------------------------
    # Spawn Normal
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
    # ------------------------------------------------

    if cloud.movement == "BOX":

        velocity = vel * cloud.spawnvelocitymultiplier

        settings.normal_factor = velocity.length

        settings.object_align_factor[0] = velocity.x
        settings.object_align_factor[1] = velocity.y
        settings.object_align_factor[2] = velocity.z

        settings.factor_random = 0.0

    # ------------------------------------------------
    # SPHERE
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
    # ------------------------------------------------

    elif cloud.movement == "PLANE":

        settings.normal_factor = vel.length

        settings.object_align_factor[0] = vel.x
        settings.object_align_factor[1] = vel.y
        settings.object_align_factor[2] = vel.z

        settings.factor_random = 1.0

    # ------------------------------------------------
    # STREAM
    # ------------------------------------------------

    elif cloud.movement == "STREAM":

        velocity = vel * cloud.spawnvelocitymultiplier

        settings.normal_factor = velocity.length

        settings.object_align_factor[0] = velocity.x
        settings.object_align_factor[1] = velocity.y
        settings.object_align_factor[2] = velocity.z

        settings.factor_random = max(
            min(cloud.spawnangle / 90.0, 1.0),
            0.0
        )

    # ------------------------------------------------
    # DISK
    # ------------------------------------------------

    elif cloud.movement == "DISK":

        settings.normal_factor = vel.length

        settings.object_align_factor[0] = vel.x
        settings.object_align_factor[1] = vel.y
        settings.object_align_factor[2] = vel.z

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