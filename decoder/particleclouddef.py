# pyright: basic, reportGeneralTypeIssues=false

import bpy
import mathutils
from ..wce.particleclouddef import particleclouddef
from .context import Context

def decode_particleclouddef(ctx: Context, cloud: particleclouddef) -> str:

    # ------------------------------------------------
    # Create emitter mesh
    # ------------------------------------------------

    mesh = bpy.data.meshes.new(cloud.tag + "_EMITTER")

    # Tiny triangle so Blender can emit particles
    verts = [
        (0.0, 0.0, 0.0),
        (0.001, 0.0, 0.0),
        (0.0, 0.001, 0.0),
    ]

    faces = [(0, 1, 2)]

    mesh.from_pydata(verts, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(cloud.tag, mesh)

    ctx.collection.objects.link(obj)

    obj.parent = ctx.parent

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

    # ------------------------------------------------
    # Create particle render object
    # ------------------------------------------------

    particle_mesh = bpy.data.meshes.new(cloud.tag + "_PARTICLE")

    pverts = [
        (-0.5, -0.5, 0.0),
        ( 0.5, -0.5, 0.0),
        ( 0.5,  0.5, 0.0),
        (-0.5,  0.5, 0.0),
    ]

    pfaces = [(0, 1, 2, 3)]

    particle_mesh.from_pydata(pverts, [], pfaces)
    particle_mesh.update()

    particle_obj = bpy.data.objects.new(
        cloud.tag + "_PARTICLE",
        particle_mesh
    )

    ctx.collection.objects.link(particle_obj)

    particle_obj.hide_render = True
    particle_obj.hide_viewport = True

    # ------------------------------------------------
    # Resolve blittag -> sprite
    # ------------------------------------------------

    image = None

    blit = ctx.parser.blitspritedefs.get(cloud.blittag)

    if blit:

        sprite = ctx.parser.simplespritedefs.get(blit.sprite)

        if sprite and len(sprite.frames) > 0:

            frame = sprite.frames[0]

            if len(frame.files) > 0:

                filename = frame.files[0].file

                image = bpy.data.images.get(filename)

    # ------------------------------------------------
    # Material
    # ------------------------------------------------

    mat = bpy.data.materials.new(cloud.tag + "_MAT")

    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    # mat.shadow_method = 'NONE'

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (500, 0)

    transparent = nodes.new("ShaderNodeBsdfTransparent")
    transparent.location = (200, -100)

    emission = nodes.new("ShaderNodeEmission")
    emission.location = (200, 100)

    mix = nodes.new("ShaderNodeMixShader")
    mix.location = (350, 0)

    tex = nodes.new("ShaderNodeTexImage")
    tex.location = (-300, 100)

    if image:
        tex.image = image

    tint = cloud.tint

    emission.inputs["Color"].default_value = (
        tint[0] / 255.0,
        tint[1] / 255.0,
        tint[2] / 255.0,
        tint[3] / 255.0,
    )

    emission.inputs["Strength"].default_value = 1.0

    links.new(tex.outputs["Color"], emission.inputs["Color"])
    links.new(tex.outputs["Alpha"], mix.inputs["Fac"])

    links.new(transparent.outputs["BSDF"], mix.inputs[1])
    links.new(emission.outputs["Emission"], mix.inputs[2])

    links.new(mix.outputs["Shader"], output.inputs["Surface"])

    particle_obj.data.materials.append(mat)

    # ------------------------------------------------
    # Particle system
    # ------------------------------------------------

    modifier = obj.modifiers.new(
        name="ParticleCloud",
        type='PARTICLE_SYSTEM'
    )

    psys = modifier.particle_system
    settings = bpy.data.particles.new(cloud.tag + "_SETTINGS")

    psys.settings = settings

    settings.count = max(cloud.size, 1)

    settings.frame_start = 1
    settings.frame_end = max(cloud.duration, 1)

    settings.lifetime = max(cloud.lifespan / 100.0, 1.0)

    settings.emit_from = 'FACE'

    settings.render_type = 'OBJECT'
    settings.instance_object = particle_obj

    settings.physics_type = 'NEWTON'

    settings.normal_factor = cloud.spawnvelocitymultiplier

    vel = mathutils.Vector(cloud.spawnvelocity)

    settings.factor_random = vel.length

    settings.particle_size = max(cloud.spawnscale, 0.001)

    settings.use_rotations = False

    settings.effector_weights.all = 1.0
    settings.effector_weights.gravity = cloud.gravity

    settings.use_emit_random = True

    settings.distribution = 'RAND'

    settings.use_modifier_stack = True

    # ------------------------------------------------
    # Spawn shape approximation
    # ------------------------------------------------

    if cloud.movement == "SPHERE":
        settings.emit_from = 'VOLUME'

    elif cloud.movement == "PLANE":
        settings.emit_from = 'FACE'

    elif cloud.movement == "DISK":
        settings.emit_from = 'FACE'

    elif cloud.movement == "STREAM":
        settings.emit_from = 'VERT'

    # ------------------------------------------------
    # Brownian motion
    # ------------------------------------------------

    if cloud.brownian:
        settings.brownian_factor = 1.0

    # ------------------------------------------------
    # Fade
    # ------------------------------------------------

    if cloud.fade:
        settings.use_die_on_collision = False

    # ------------------------------------------------
    # Spawn radius visualization
    # ------------------------------------------------

    if cloud.spawnradius > 0.0:
        obj.empty_display_size = cloud.spawnradius

    # ------------------------------------------------
    # Bounding box helpers
    # ------------------------------------------------

    if cloud.spawnboxmin and cloud.spawnboxmax:

        obj["spawnboxmin"] = cloud.spawnboxmin
        obj["spawnboxmax"] = cloud.spawnboxmax

    if cloud.boxmin and cloud.boxmax:

        obj["boxmin"] = cloud.boxmin
        obj["boxmax"] = cloud.boxmax

    return ""