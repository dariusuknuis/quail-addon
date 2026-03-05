import bpy
from mathutils import Vector, Quaternion


def is_dev() -> bool:
    return False  # RAWR


def version() -> str:
    return "v1.5.8"


def string_to_vector(line: str) -> Vector:
    lines = line.split(",")
    return Vector((float(lines[0]), float(lines[1]), float(lines[2])))


def string_to_quaternion(line: str) -> Quaternion:
    lines = line.split(",")
    return Quaternion((float(lines[0]), float(lines[1]), float(lines[2]), float(lines[3]))).normalized()


def _add_group_socket(nt: bpy.types.NodeTree, name: str, socket_type: str, is_input: bool):
    """
    Create a group interface socket in a way that works on both 3.6 and 4/5.
    Returns the created interface item (4/5) or the socket (3.6).
    """
    # Blender 4/5 API: use node_group.interface
    if hasattr(nt, "interface"):
        return nt.interface.new_socket(
            name=name,
            in_out='INPUT' if is_input else 'OUTPUT',
            socket_type=socket_type,
        )
    # Blender 3.6 fallback
    return (nt.inputs if is_input else nt.outputs).new(socket_type, name)

def _get_group_io_sockets(node_group):
    """
    Blender 5.0 compatible:
    Return two dicts mapping socket name -> NodeSocket
    for the Group Input (outputs) and Group Output (inputs) nodes.

    Usage:
        gi, go = _get_group_io_sockets(my_group)
        links.new(gi["Color"], some_node.inputs["Base Color"])
        links.new(some_node.outputs["BSDF"], go["Shader"])
    """
    gi_node = None
    go_node = None
    for n in node_group.nodes:
        # bl_idname is stable across versions
        if n.bl_idname == 'NodeGroupInput':
            gi_node = n
        elif n.bl_idname == 'NodeGroupOutput':
            go_node = n

    # Create them if they don't exist yet (fresh group)
    if gi_node is None:
        gi_node = node_group.nodes.new('NodeGroupInput')
        gi_node.location = (-400, 0)
    if go_node is None:
        go_node = node_group.nodes.new('NodeGroupOutput')
        go_node.location = (400, 0)

    # Build name->socket maps from the real, linkable sockets
    gi = {sock.name: sock for sock in gi_node.outputs}  # inputs of the group appear as outputs on Group Input
    go = {sock.name: sock for sock in go_node.inputs}   # outputs of the group appear as inputs on Group Output
    return gi, go
