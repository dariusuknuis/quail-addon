import bpy
import math
import mathutils
from .context import Context
from ..common.bsp import create_bsp_plane_mesh, create_leaf_mesh, rotation_from_normal
from ..wce.worldtree import worldtree

def decode_worldtree(ctx: Context, wt: worldtree) -> str:

    if not wt or not wt.worldnodes:
        return ""

    # ----------------------------------------
    # Root object
    # ----------------------------------------
    root = bpy.data.objects.new(wt.tag, None)
    root["quaildef"] = "worldtree"
    ctx.collection.objects.link(root)

    props = root.quail_worldtree

    # clear existing
    while len(props.nodes) > 0:
        props.nodes.remove(0)

    # ----------------------------------------
    # Shared meshes (IMPORTANT)
    # ----------------------------------------
    plane_mesh = create_bsp_plane_mesh()
    leaf_mesh = create_leaf_mesh()

    # ----------------------------------------
    # Create nodes
    # ----------------------------------------
    for i, node in enumerate(wt.worldnodes):

        node_index = i + 1
        node_name = f"WorldNode_{node_index}"

        normal = node.normalabcd[:3]
        d = node.normalabcd[3]

        # position from plane
        n = mathutils.Vector(normal).normalized()
        position = -d * n

        is_leaf = (node.fronttree == 0 and node.backtree == 0)

        mesh = leaf_mesh if is_leaf else plane_mesh

        obj = bpy.data.objects.new(node_name, mesh)
        obj["quaildef"] = "worldnode"

        obj.location = position
        obj.rotation_euler = rotation_from_normal(normal)

        obj.parent = ctx.parent

        # ----------------------------------------
        # Prefer WORLDTREE collection if it exists
        # ----------------------------------------
        target_collection = None

        if hasattr(ctx, "worldtree_collection") and ctx.worldtree_collection:
            target_collection = ctx.worldtree_collection
        else:
            target_collection = ctx.collection

        target_collection.objects.link(obj)

        # ----------------------------------------
        # Store in PropertyGroup
        # ----------------------------------------
        item = props.nodes.add()

        item.normal_x = normal[0]
        item.normal_y = normal[1]
        item.normal_z = normal[2]
        item.normal_w = d

        item.region_tag = node.worldregiontag
        item.front_tree = node.fronttree
        item.back_tree = node.backtree

        item.object = obj

        obj.hide_set(True)

    print(f"Decoded WorldTree: {len(wt.worldnodes)} nodes")

    return ""