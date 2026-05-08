# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import bmesh
from ..wce.blitspritedef import blitspritedef
from .context import Context
from ..common.rendermethod import apply_userdefined, apply_transparent, parse_rendermethod_string, create_rendermethod_nodegroup


def decode_blitspritedef(ctx: Context, sprite: blitspritedef) -> str:

    # --------------------------------------------------
    # Already exists
    # --------------------------------------------------

    if sprite.tag in bpy.data.objects:
        return ""

    # Image size

    width = 64
    height = 64

    aspect = width / height

    # --------------------------------------------------
    # Create mesh plane
    # --------------------------------------------------

    mesh = bpy.data.meshes.new(sprite.tag)

    bm = bmesh.new()

    sx = aspect * 0.5
    sy = 0.5

    verts = [
        bm.verts.new((-sx, 0.0, -sy)),
        bm.verts.new(( sx, 0.0, -sy)),
        bm.verts.new(( sx, 0.0,  sy)),
        bm.verts.new((-sx, 0.0,  sy)),
    ]

    bm.faces.new(verts)

    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(sprite.tag, mesh)

    obj["quaildef"] = "blitspritedef"

    ctx.collection.objects.link(obj)

    props = obj.quail_blitspritedef

    # --------------------------------------------------
    # UVs
    # --------------------------------------------------

    mesh.uv_layers.new(name="UVMap")

    uv_layer = mesh.uv_layers.active

    uv_layer.data[0].uv = (0.0, 0.0)
    uv_layer.data[1].uv = (1.0, 0.0)
    uv_layer.data[2].uv = (1.0, 1.0)
    uv_layer.data[3].uv = (0.0, 1.0)

    # --------------------------------------------------
    # Material
    # --------------------------------------------------

    mat = bpy.data.materials.new(sprite.tag)

    mat["quaildef"] = "blitspritematerial"

    mesh.materials.append(mat)

    parsed = parse_rendermethod_string(sprite.rendermethod)

    if parsed["use_userdefined"]:
        props.use_userdefined = True
        props.userdefined_index = parsed["userdefined_index"]

        apply_userdefined(props, props.userdefined_index)

    elif parsed.get("transparent"):
        props.use_userdefined = False
        props.transparent_override = True

        apply_transparent(props)

    else:
        props.use_userdefined = False

        props.drawstyle = parsed["drawstyle"]
        props.lighting = parsed["lighting"]
        props.shading = parsed["shading"]
        props.texture_index = parsed["texture_index"]

        props.masked = parsed["masked"]
        props.alphablend = parsed["alphablend"]
        props.opacity = parsed["opacity"]
        props.additive = parsed["additive"]
        props.dynamic = parsed["dynamic"]
        props.prelit = parsed["prelit"]

    mat.use_nodes = True

    if mat.node_tree is None:
        return f"material {sprite.tag} has no node tree"

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    for n in nodes:
        nodes.remove(n)

    # --------------------------------------------------
    # RenderMethod nodegroup
    # --------------------------------------------------

    group_tree = create_rendermethod_nodegroup()

    group_node = nodes.new("ShaderNodeGroup")
    group_node.node_tree = group_tree
    group_node.location = (0, 0)

    hide_inputs = {
        "PassableDisplay",
        "Masked",
        "AlphaBlend",
        "Additive",
        "Opacity",
        "Drawstyle",
        "TextureIndex",
    }

    for socket in group_node.inputs:
        if socket.name in hide_inputs:
            socket.hide = True

    group_node.inputs["sRGB Texture"].default_value = (1.0, 1.0, 1.0, 1.0)
    group_node.inputs["Masked"].default_value = float(props.masked)
    group_node.inputs["AlphaBlend"].default_value = float(props.alphablend)
    group_node.inputs["Opacity"].default_value = props.opacity
    group_node.inputs["Additive"].default_value = float(props.additive)
    group_node.inputs["TextureIndex"].default_value = float(props.texture_index)
    drawstyle_map = {
        "DRAW0": 0.0,
        "DRAW1": 1.0,
        "WIREFRAME": 2.0,
        "SOLIDFILL": 3.0,
    }

    group_node.inputs["Drawstyle"].default_value = drawstyle_map.get(
        props.drawstyle, 0.0
    )

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (300, 0)

    links.new(
        group_node.outputs["Shader"],
        output.inputs["Surface"]
    )

    # --------------------------------------------------
    # SIMPLESPRITE nodegroup
    # --------------------------------------------------

    tag = sprite.sprite
    if tag:
        props.spritetag = tag

    if props.spritetag:
        sprite_group = bpy.data.node_groups.get(props.spritetag)
        if sprite_group:
            sprite_node = nodes.new("ShaderNodeGroup")
            sprite_node.node_tree = sprite_group
            sprite_node.location = (-400, 0)

            links.new(sprite_node.outputs["sRGB Texture"], group_node.inputs["sRGB Texture"])
            links.new(sprite_node.outputs["Alpha"], group_node.inputs["Alpha"])

    # --------------------------------------------------
    # Transparency
    # --------------------------------------------------

    mat.blend_method = 'BLEND'
    mat.use_backface_culling = False
    props.transparent = bool(sprite.transparent)

    # --------------------------------------------------
    # Billboard constraint
    # --------------------------------------------------

    cam = bpy.context.scene.camera

    if cam:

        c = obj.constraints.new('TRACK_TO')

        c.target = cam
        c.track_axis = 'TRACK_NEGATIVE_Y'
        c.up_axis = 'UP_Z'

    return ""