import bpy

def get_vertex_normal_nodegroup():

    name = "VERTEX_NORMALS"

    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]

    group = bpy.data.node_groups.new(name, "GeometryNodeTree")

    nodes = group.nodes
    links = group.links

    nodes.clear()

    # -----------------------------
    # Group Input
    # -----------------------------
    group_in = nodes.new("NodeGroupInput")
    group_in.location = (-300, 0)

    group.interface.new_socket(
        name="Geometry",
        in_out='INPUT',
        socket_type='NodeSocketGeometry'
    )

    # -----------------------------
    # Named Attribute
    # -----------------------------
    named_attr = nodes.new("GeometryNodeInputNamedAttribute")
    named_attr.location = (-100, -100)
    named_attr.data_type = 'FLOAT_VECTOR'
    named_attr.inputs["Name"].default_value = "vertex_normals"

    # -----------------------------
    # Set Mesh Normal
    # -----------------------------
    set_normal = nodes.new("GeometryNodeSetMeshNormal")
    set_normal.location = (100, 0)
    set_normal.mode = 'FREE'
    set_normal.domain = 'POINT'

    # -----------------------------
    # Group Output
    # -----------------------------
    group_out = nodes.new("NodeGroupOutput")
    group_out.location = (300, 0)

    group.interface.new_socket(
        name="Geometry",
        in_out='OUTPUT',
        socket_type='NodeSocketGeometry'
    )

    # -----------------------------
    # Links
    # -----------------------------
    links.new(group_in.outputs["Geometry"], set_normal.inputs["Mesh"])
    links.new(named_attr.outputs["Attribute"], set_normal.inputs["Custom Normal"])
    links.new(set_normal.outputs["Mesh"], group_out.inputs["Geometry"])

    return group