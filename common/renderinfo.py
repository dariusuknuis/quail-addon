import bpy
from .rendermethod import parse_rendermethod_string, create_rendermethod_nodegroup, apply_userdefined, apply_transparent

def build_renderinfo_material(sprite_tag: str, node_index: int, node) -> bpy.types.Material:

    mat_name = f"{sprite_tag}_NODE{node_index}_RENDERINFO"

    mat = bpy.data.materials.get(mat_name)
    if not mat:
        mat = bpy.data.materials.new(mat_name)

    mat['quaildef'] = 'renderinfo'

    ri = node.bspnode.renderinfo
    parsed = parse_rendermethod_string(node.bspnode.rendermethod)

    props = mat.quail_renderinfo

    # --------------------------------------------
    # RenderMethod logic
    # --------------------------------------------

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
    # --------------------------------------------
    # RenderInfo-specific values
    # --------------------------------------------

    if ri.pen is not None:
        props.has_pen = True
        props.pen = ri.pen
    else:
        props.has_pen = False
        props.pen = 0

    if ri.brightness is not None:
        props.has_brightness = True
        props.brightness = ri.brightness
    else:
        props.has_brightness = False
        props.brightness = 0.0

    if ri.scaledambient is not None:
        props.has_scaledambient = True
        props.scaledambient = ri.scaledambient
    else:
        props.has_scaledambient = False
        props.scaledambient = 0.0

    tag = ri.simplespriteinst.simplespritetag
    if tag:
        props.simplespritetag = tag
        props.has_simplesprite = True
    else:
        props.has_simplesprite = False

    props.simplespritehaveskipframes = bool(ri.simplespriteinst.simplespritehaveskipframes)
    props.simplespriteskipframes = bool(ri.simplespriteinst.simplespriteskipframes == 1)

    props.twosided = bool(ri.twosided)

    # --------------------------------------------
    # Build node tree
    # --------------------------------------------

    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    for n in nodes:
        nodes.remove(n)

    group_tree = create_rendermethod_nodegroup()

    group_node = nodes.new("ShaderNodeGroup")
    group_node.node_tree = group_tree
    group_node.location = (0, 0)

    hide_inputs = {
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

    links.new(group_node.outputs["Shader"], output.inputs["Surface"])

    mat.use_backface_culling = not props.twosided

    if props.simplespritetag:
        sprite_group = bpy.data.node_groups.get(props.simplespritetag)
        if sprite_group:
            sprite_node = nodes.new("ShaderNodeGroup")
            sprite_node.node_tree = sprite_group
            sprite_node.location = (-400, 0)

            links.new(sprite_node.outputs["sRGB Texture"], group_node.inputs["sRGB Texture"])
            links.new(sprite_node.outputs["Alpha"], group_node.inputs["Alpha"])

    return mat