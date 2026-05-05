import bpy
import math
import mathutils
from mathutils import Vector

class BSPNode:
    def __init__(self):
        self.normal = None
        self.d = None

        self.front = None
        self.back = None
        self.parent = None

        self.region_tag = None


def build_bsp(parser):

    if getattr(parser, "bsp_root", None):
        return

    tree = next(iter(parser.worldtrees.values()), None)
    if not tree:
        return

    nodes = {}

    # create nodes (1-based)
    for i, raw in enumerate(tree.worldnodes, start=1):

        n = BSPNode()

        nx, ny, nz, d = raw.normalabcd
        n.normal = Vector((nx, ny, nz))
        n.d = d

        if raw.worldregiontag and raw.worldregiontag != "NULL":
            n.region_tag = raw.worldregiontag

        nodes[i] = n

    # link
    for i, raw in enumerate(tree.worldnodes, start=1):

        node = nodes[i]

        ft = raw.fronttree
        bt = raw.backtree

        if ft > 0:
            node.front = nodes[ft]
            node.front.parent = node

        if bt > 0:
            node.back = nodes[bt]
            node.back.parent = node

    # map leaves
    parser.region_to_leaf = {}

    for node in nodes.values():
        if node.region_tag and node.front is None and node.back is None:
            parser.region_to_leaf[node.region_tag] = node

    parser.bsp_root = nodes[1]

def create_zone_bounds_intersect_geometry_node():

    if "ZoneBoundsIntersect" in bpy.data.node_groups:
        return bpy.data.node_groups["ZoneBoundsIntersect"]

    gn_tree = bpy.data.node_groups.new("ZoneBoundsIntersect", 'GeometryNodeTree')

    nodes = gn_tree.nodes
    links = gn_tree.links

    # ----------------------------------------
    # Group I/O
    # ----------------------------------------
    group_input = nodes.new("NodeGroupInput")
    group_input.location = (-1000, 0)

    group_output = nodes.new("NodeGroupOutput")
    group_output.location = (600, 0)

    gn_tree.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
    gn_tree.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

    # ----------------------------------------
    # Camera + Self distance
    # ----------------------------------------

    act_cam_node = nodes.new("GeometryNodeInputActiveCamera")
    act_cam_node.location = (-1100, 300)

    cam_node = nodes.new("GeometryNodeObjectInfo")
    cam_node.location = (-1000, 300)
    links.new(act_cam_node.outputs[0], cam_node.inputs["Object"])

    self_node = nodes.new("GeometryNodeSelfObject")
    self_node.location = (-1100, 100)

    obj_info_node = nodes.new("GeometryNodeObjectInfo")
    obj_info_node.location = (-1000, 100)
    links.new(self_node.outputs[0], obj_info_node.inputs["Object"])

    distance = nodes.new("ShaderNodeVectorMath")
    distance.operation = 'DISTANCE'
    distance.location = (-800, 200)

    links.new(cam_node.outputs["Location"], distance.inputs[0])
    links.new(obj_info_node.outputs["Location"], distance.inputs[1])

    # ----------------------------------------
    # Extrude + / -
    # ----------------------------------------
    extrude1 = nodes.new("GeometryNodeExtrudeMesh")
    extrude1.mode = 'FACES'
    extrude1.location = (-200, 300)
    extrude1.inputs["Offset Scale"].default_value = 0.005


    extrude2 = nodes.new("GeometryNodeExtrudeMesh")
    extrude2.mode = 'FACES'
    extrude2.location = (-200, 100)
    extrude2.inputs["Offset Scale"].default_value = -0.005

    links.new(group_input.outputs[0], extrude1.inputs["Mesh"])
    links.new(distance.outputs["Value"], extrude1.inputs[2])

    links.new(group_input.outputs[0], extrude2.inputs["Mesh"])
    links.new(distance.outputs["Value"], extrude2.inputs[2])

    join_node = nodes.new("GeometryNodeJoinGeometry")
    join_node.location = (0, 200)
    links.new(extrude1.outputs[0], join_node.inputs[0])
    links.new(extrude2.outputs[0], join_node.inputs[0])

    # ----------------------------------------
    # WORLD_BOUNDS cube
    # ----------------------------------------
    obj_info = nodes.new("GeometryNodeObjectInfo")
    obj_info.location = (-800, -200)
    obj_info.transform_space = 'RELATIVE'

    bounds_obj = bpy.data.objects.get("WORLD_BOUNDS")
    if bounds_obj:
        obj_info.inputs["Object"].default_value = bounds_obj

    cube = nodes.new("GeometryNodeMeshCube")
    cube.location = (-600, -200)
    cube.inputs["Size"].default_value = (2.0, 2.0, 2.0)

    transform = nodes.new("GeometryNodeTransform")
    transform.location = (-400, -200)

    links.new(cube.outputs["Mesh"], transform.inputs["Geometry"])
    links.new(obj_info.outputs["Location"], transform.inputs["Translation"])
    links.new(obj_info.outputs["Rotation"], transform.inputs["Rotation"])
    links.new(obj_info.outputs["Scale"], transform.inputs["Scale"])

    # ----------------------------------------
    # Boolean INTERSECT
    # ----------------------------------------
    boolean = nodes.new("GeometryNodeMeshBoolean")
    boolean.operation = 'INTERSECT'
    boolean.location = (200, 0)

    links.new(join_node.outputs[0], boolean.inputs[1])  # plane slab
    links.new(transform.outputs["Geometry"], boolean.inputs[1])  # bounds

    # ----------------------------------------
    # Output
    # ----------------------------------------
    links.new(boolean.outputs["Mesh"], group_output.inputs[0])

    return gn_tree

def create_bsp_plane_mesh(name="BSPPlaneMesh", size=10000.0):
    half = size / 2.0

    verts = [
        (-half, -half, 0),
        ( half, -half, 0),
        ( half,  half, 0),
        (-half,  half, 0)
    ]
    faces = [(0, 1, 2, 3)]

    rot = mathutils.Euler((-math.pi/2, 0, 0), 'XYZ').to_matrix().to_4x4()
    verts_rot = [rot @ mathutils.Vector(v) for v in verts]

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts_rot, [], faces)
    mesh.update()
    return mesh


def create_leaf_mesh(name="LeafMesh"):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(0, 0, 0)], [], [])
    mesh.update()
    return mesh


def rotation_from_normal(normal):
    default_dir = mathutils.Vector((0, 1, 0))
    target_dir = mathutils.Vector(normal).normalized()
    quat = default_dir.rotation_difference(target_dir)
    return quat.to_euler()


def calculate_point_on_plane(normal, d):
    n = mathutils.Vector(normal).normalized()
    return -d * n