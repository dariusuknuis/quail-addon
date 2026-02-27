# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false, reportAttributeAccessIssue=false

import bpy
from ..wce.wce import wce
from ..wce.simplespritedef import simplespritedef
from .context import Context

def decode_simplespritedef(ctx:Context, simplesprite:simplespritedef) -> str:
    if simplesprite.tag in bpy.data.node_groups:
        return ""
    simplesprite_node = bpy.data.node_groups.new(simplesprite.tag, 'ShaderNodeTree')
    simplesprite_node['quaildef'] = 'simplespritedef'

    nodes = simplesprite_node.nodes
    links = simplesprite_node.links

    group_output = nodes.new("NodeGroupOutput")
    group_output.location = (1428, 12)

    def add_output(name, socket_type):
        simplesprite_node.interface.new_socket(
            name=name,
            in_out='OUTPUT',
            socket_type=socket_type
        )

    add_output("sRGB Texture", "NodeSocketColor")
    add_output("Alpha", "NodeSocketFloat")

    out = group_output.inputs



    return ""