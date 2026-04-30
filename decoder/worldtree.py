import bpy
import math
import mathutils
from .context import Context
from ..common.bsp import create_bsp_plane_mesh, create_leaf_mesh, rotation_from_normal, create_zone_bounds_intersect_geometry_node
from ..wce.worldtree import worldtree

def decode_worldtree(ctx: Context, wt: worldtree) -> str:

    if not wt or not wt.worldnodes:
        return ""

    # ----------------------------------------
    # Shared meshes (IMPORTANT)
    # ----------------------------------------
    plane_mesh = bpy.data.meshes.get("BSPPlaneMesh") or create_bsp_plane_mesh()
    leaf_mesh  = bpy.data.meshes.get("LeafMesh") or create_leaf_mesh()

    # ----------------------------------------
    # Create / get material
    # ----------------------------------------
    mat = bpy.data.materials.get("WorldTreePlaneMaterial")
    if not mat:
        mat = bpy.data.materials.new("WorldTreePlaneMaterial")
        mat.use_nodes = True

        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (1.0, 1.0, 0.0, 1.0)
            bsdf.inputs["Alpha"].default_value = 0.25

        mat.blend_method = 'BLEND'
        mat.use_backface_culling = False

    # assign material to shared plane mesh
    if plane_mesh.materials:
        plane_mesh.materials[0] = mat
    else:
        plane_mesh.materials.append(mat)

    # ----------------------------------------
    # Target collection
    # ----------------------------------------
    if hasattr(ctx, "worldtree_collection") and ctx.worldtree_collection:
        target_collection = ctx.worldtree_collection
    else:
        target_collection = ctx.collection

    # ----------------------------------------
    # Create nodes
    # ----------------------------------------
    for i, node in enumerate(wt.worldnodes):

        node_index = i + 1
        node_name = f"WorldNode_{node_index}"

        normal = node.normalabcd[:3]
        d = node.normalabcd[3]

        n = mathutils.Vector(normal).normalized()
        position = -d * n

        is_leaf = (node.fronttree == 0 and node.backtree == 0)
        mesh = leaf_mesh if is_leaf else plane_mesh

        obj = bpy.data.objects.new(node_name, mesh)
        obj["quaildef"] = "worldnode"

        obj.location = position
        obj.rotation_euler = rotation_from_normal(normal)

        # optional parenting (safe, but not required)
        obj.parent = ctx.parent

        # ----------------------------------------
        # Geometry node (only for planes)
        # ----------------------------------------
        if not is_leaf:
            gn = create_zone_bounds_intersect_geometry_node()

            mod = obj.modifiers.new(name="BoundsIntersect", type='NODES')
            mod.node_group = gn

        # ----------------------------------------
        # Link object
        # ----------------------------------------
        target_collection.objects.link(obj)

        # ----------------------------------------
        # Store data ON THE OBJECT (correct way)
        # ----------------------------------------
        props = obj.quail_worldnode

        props.normal_x = normal[0]
        props.normal_y = normal[1]
        props.normal_z = normal[2]
        props.normal_w = d

        props.region_tag = node.worldregiontag
        props.front_tree = node.fronttree
        props.back_tree = node.backtree

        obj.hide_set(True)

    print(f"Decoded WorldTree: {len(wt.worldnodes)} nodes")

    return ""