# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import bmesh
from ..wce.blitspritedef import blitspritedef
from .context import Context
from ..common.rendermethod import apply_userdefined, apply_transparent, parse_rendermethod_string, create_rendermethod_nodegroup


def create_blitsprite_billboard_geo():

    geo_name = "BLITSPRITE_BILLBOARD"

    geo_group = bpy.data.node_groups.get(geo_name)

    if geo_group:
        return geo_group

    geo_group = bpy.data.node_groups.new(
        geo_name,
        'GeometryNodeTree'
    )

    nodes = geo_group.nodes
    links = geo_group.links

    nodes.clear()

    # ------------------------------------------------
    # Interface
    # ------------------------------------------------

    geo_group.interface.new_socket(
        name="Geometry",
        in_out='INPUT',
        socket_type='NodeSocketGeometry'
    )

    geo_group.interface.new_socket(
        name="Geometry",
        in_out='OUTPUT',
        socket_type='NodeSocketGeometry'
    )

    # ------------------------------------------------
    # Nodes
    # ------------------------------------------------

    group_input = nodes.new("NodeGroupInput")
    group_input.location = (-1200, 0)

    group_output = nodes.new("NodeGroupOutput")
    group_output.location = (800, 0)

    active_cam = nodes.new("GeometryNodeInputActiveCamera")
    active_cam.location = (-1200, -300)

    cam_info = nodes.new("GeometryNodeObjectInfo")
    cam_info.location = (-1000, -300)

    self_obj = nodes.new("GeometryNodeSelfObject")
    self_obj.location = (-1200, -600)

    self_info = nodes.new("GeometryNodeObjectInfo")
    self_info.location = (-1000, -600)

    subtract = nodes.new("ShaderNodeVectorMath")
    subtract.operation = 'SUBTRACT'
    subtract.location = (-700, -400)

    align = nodes.new("FunctionNodeAlignRotationToVector")
    align.location = (-400, -400)

    # Plane faces Y axis
    align.axis = 'Y'
    align.pivot_axis = 'Z'

    transform = nodes.new("GeometryNodeTransform")
    transform.location = (200, 0)

    # ------------------------------------------------
    # Links
    # ------------------------------------------------

    links.new(
        active_cam.outputs["Active Camera"],
        cam_info.inputs["Object"]
    )

    links.new(
        self_obj.outputs["Self Object"],
        self_info.inputs["Object"]
    )

    links.new(
        cam_info.outputs["Location"],
        subtract.inputs[0]
    )

    links.new(
        self_info.outputs["Location"],
        subtract.inputs[1]
    )

    links.new(
        subtract.outputs["Vector"],
        align.inputs["Vector"]
    )

    links.new(
        group_input.outputs["Geometry"],
        transform.inputs["Geometry"]
    )

    links.new(
        align.outputs["Rotation"],
        transform.inputs["Rotation"]
    )

    links.new(
        transform.outputs["Geometry"],
        group_output.inputs["Geometry"]
    )

    return geo_group

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

    uv_layer.data[0].uv = (1.0, 0.0)
    uv_layer.data[1].uv = (0.0, 0.0)
    uv_layer.data[2].uv = (0.0, 1.0)
    uv_layer.data[3].uv = (1.0, 1.0)

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
        "Transparent Blit",
        "Particle Tint",
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
    group_node.inputs["Transparent Blit"].default_value = float(sprite.transparent)
    group_node.inputs["Particle Tint"].default_value = (1.0, 1.0, 1.0, 1.0)
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
        props.simplespritetag = tag

    if props.simplespritetag:
        sprite_group = bpy.data.node_groups.get(props.simplespritetag)
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
    # Billboard Geometry Nodes
    # --------------------------------------------------

    geo_group = create_blitsprite_billboard_geo()

    mod = obj.modifiers.new(
        name="Billboard",
        type='NODES'
    )

    mod.node_group = geo_group

    obj.hide_set(True)

    return ""