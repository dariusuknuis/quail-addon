# pyright: basic, reportGeneralTypeIssues=false

import bpy
import mathutils


def apply_particlecloud_settings(obj):

    if not obj:
        return

    props = obj.quail_particleclouddef

    modifier = None

    for mod in obj.modifiers:
        if mod.type == 'PARTICLE_SYSTEM':
            modifier = mod
            break

    if not modifier:
        return

    psys = modifier.particle_system

    if not psys:
        return

    settings = psys.settings

    if not settings:
        return

    # ------------------------------------------------
    # FPS conversion
    # ------------------------------------------------

    fps = bpy.context.scene.render.fps

    lifespan_seconds = max(
        props.lifespan / 1000.0,
        0.001
    )

    lifetime_frames = max(
        lifespan_seconds * fps,
        1.0
    )

    spawn_interval_frames = max(
        (props.spawnrate / 1000.0) * fps,
        1.0
    )

    # ------------------------------------------------
    # Core
    # ------------------------------------------------

    settings.count = max(props.size, 1)

    settings.frame_start = 1

    settings.frame_end = (
        settings.frame_start +
        (spawn_interval_frames * max(props.size - 1, 0))
    )

    settings.lifetime = lifetime_frames

    settings.physics_type = 'NEWTON'

    settings.use_modifier_stack = True

    settings.use_emit_random = False

    settings.distribution = 'RAND'

    settings.particle_size = max(
        props.spawnscale,
        0.001
    )

    # ------------------------------------------------
    # Particle Types
    # ------------------------------------------------

    if props.particletype in (1, 2):

        settings.render_type = 'HALO'

        settings.halo.size = max(
            props.spawnscale,
            0.01
        )

    elif props.particletype in (3, 4):

        settings.render_type = 'OBJECT'

        helper = find_particleblit(obj)

        if helper:
            settings.instance_object = helper

        settings.use_rotation_instance = True

        if props.particletype == 4:
            settings.rotation_mode = 'GLOB_Z'

    # ------------------------------------------------
    # Spawn Type
    # ------------------------------------------------

    if props.movement == "BOX":

        settings.emit_from = 'VOLUME'

    elif props.movement == "SPHERE":

        settings.emit_from = 'VOLUME'

    elif props.movement == "PLANE":

        settings.emit_from = 'FACE'

    elif props.movement == "STREAM":

        settings.emit_from = 'VERT'

    elif props.movement == "DISK":

        settings.emit_from = 'FACE'

    else:

        settings.emit_from = 'VERT'

    # ------------------------------------------------
    # Spawn Normal
    # ------------------------------------------------

    spawn_normal = mathutils.Vector(
        props.spawnnormal
    )

    settings.object_align_factor[0] = spawn_normal.x
    settings.object_align_factor[1] = spawn_normal.y
    settings.object_align_factor[2] = spawn_normal.z

    # ------------------------------------------------
    # Velocity
    # ------------------------------------------------

    vel = mathutils.Vector(
        props.spawnvelocity
    )

    # ------------------------------------------------
    # BOX
    # ------------------------------------------------

    if props.movement == "BOX":

        velocity = (
            vel *
            props.spawnvelocitymultiplier
        )

        settings.normal_factor = velocity.length

        settings.object_align_factor[0] = velocity.x
        settings.object_align_factor[1] = velocity.y
        settings.object_align_factor[2] = velocity.z

        settings.factor_random = 0.0

    # ------------------------------------------------
    # SPHERE
    # ------------------------------------------------

    elif props.movement == "SPHERE":

        settings.normal_factor = 0.0

        settings.object_align_factor[0] = 0.0
        settings.object_align_factor[1] = 0.0
        settings.object_align_factor[2] = 0.0

        settings.factor_random = (
            props.spawnvelocitymultiplier
        )

    # ------------------------------------------------
    # PLANE
    # ------------------------------------------------

    elif props.movement == "PLANE":

        settings.normal_factor = vel.length

        settings.object_align_factor[0] = vel.x
        settings.object_align_factor[1] = vel.y
        settings.object_align_factor[2] = vel.z

        settings.factor_random = 1.0

    # ------------------------------------------------
    # STREAM
    # ------------------------------------------------

    elif props.movement == "STREAM":

        velocity = (
            vel *
            props.spawnvelocitymultiplier
        )

        settings.normal_factor = velocity.length

        settings.object_align_factor[0] = velocity.x
        settings.object_align_factor[1] = velocity.y
        settings.object_align_factor[2] = velocity.z

        settings.factor_random = max(
            min(props.spawnangle / 90.0, 1.0),
            0.0
        )

    # ------------------------------------------------
    # DISK
    # ------------------------------------------------

    elif props.movement == "DISK":

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

    if props.movement in {
        "BOX",
        "SPHERE",
        "PLANE",
        "STREAM",
        "DISK",
    }:

        settings.effector_weights.gravity = (
            props.gravity / 9.81
        )

    else:

        settings.effector_weights.gravity = 0.0

    # ------------------------------------------------
    # Brownian
    # ------------------------------------------------

    if props.brownian:

        settings.brownian_factor = 1.0

    else:

        settings.brownian_factor = 0.0

    # ------------------------------------------------
    # Fade
    # ------------------------------------------------

    if props.fade:

        settings.use_rotations = False

    # ------------------------------------------------
    # Object Relative
    # ------------------------------------------------

    if props.objectrelative:

        settings.use_rotations = True

def find_particleblit(obj):

    for child in obj.children:

        if child.get("quaildef") == "particleblit":
            return child

    return None

def apply_particlecloud_blit(obj):

    if not obj:
        return

    props = obj.quail_particleclouddef

    source_blit = props.blittag

    if not source_blit:
        return

    helper = find_particleblit(obj)

    # ------------------------------------------------
    # Recreate helper if source changed
    # ------------------------------------------------

    if helper:

        helper_props = helper.quail_particleblit

        if helper_props.sourceblit != source_blit:

            bpy.data.objects.remove(
                helper,
                do_unlink=True
            )

            helper = None

    # ------------------------------------------------
    # Create helper if missing
    # ------------------------------------------------

    if not helper:

        helper = source_blit.copy()

        helper.data = source_blit.data.copy()

        for i, mat in enumerate(helper.data.materials):
            if not mat:
                continue

            helper.data.materials[i] = mat.copy()

        helper.name = f"{obj.name}_BLIT"

        helper["quaildef"] = "particleblit"

        helper.parent = obj

        pblitprops = helper.quail_particleblit

        pblitprops.sourceblit = source_blit

        obj.users_collection[0].objects.link(helper)

    # ------------------------------------------------
    # Material tint
    # ------------------------------------------------

    tint = (
        props.tint[0],
        props.tint[1],
        props.tint[2],
        props.tint[3],
    )

    for i, mat in enumerate(helper.data.materials):

        if not mat:
            continue

        if not mat.use_nodes:
            continue

        if not mat.node_tree:
            continue

        for node in mat.node_tree.nodes:

            if (
                node.type == 'GROUP' and
                node.node_tree and
                node.node_tree.name == "RENDERMETHOD"
            ):

                if "Particle Tint" in node.inputs:

                    node.inputs["Particle Tint"].default_value = tint

    helper.hide_set(True)

def apply_particlecloud_visuals(obj):

    if not obj:
        return

    props = obj.quail_particleclouddef

    # ------------------------------------------------
    # Spawn Radius
    # ------------------------------------------------

    if props.spawnradius > 0.0:

        obj.empty_display_size = (
            props.spawnradius
        )

    # ------------------------------------------------
    # BOX
    # ------------------------------------------------

    if props.movement == "BOX":

        if (
            props.has_spawnbox and
            props.spawnboxmin and
            props.spawnboxmax
        ):

            minv = mathutils.Vector(
                props.spawnboxmin
            )

            maxv = mathutils.Vector(
                props.spawnboxmax
            )

            center = (minv + maxv) * 0.5
            scale = (maxv - minv) * 0.5

            obj.location = center
            obj.scale = scale

    # ------------------------------------------------
    # SPHERE
    # ------------------------------------------------

    elif props.spawnradius > 0.0:

        obj.scale = (
            props.spawnradius,
            props.spawnradius,
            props.spawnradius
        )