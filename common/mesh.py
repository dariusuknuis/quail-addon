import bpy
from .s3dobject import get_collision_volume_material

def get_vertex_normal_nodegroup():

    name="VERTEX_NORMALS"

    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]

    mat = get_collision_volume_material()

    group = bpy.data.node_groups.new(name, "GeometryNodeTree")
    nodes = group.nodes
    links = group.links
    nodes.clear()

    # ------------------------------------------------
    # INTERFACE
    # ------------------------------------------------
    group.interface.new_socket(
        name="Geometry",
        in_out='INPUT',
        socket_type='NodeSocketGeometry'
    )

    group.interface.new_socket(
        name="Show Normals",
        in_out='INPUT',
        socket_type='NodeSocketBool'
    )

    group.interface.new_socket(
        name="Geometry",
        in_out='OUTPUT',
        socket_type='NodeSocketGeometry'
    )

    # ------------------------------------------------
    # INPUT / OUTPUT
    # ------------------------------------------------
    group_in = nodes.new("NodeGroupInput")
    group_in.location = (-1200, 0)

    group_out = nodes.new("NodeGroupOutput")
    group_out.location = (600, 0)

    # ------------------------------------------------
    # Named Attribute (vertex_normals)
    # ------------------------------------------------
    n_attr = nodes.new("GeometryNodeInputNamedAttribute")
    n_attr.location = (-1000, -200)
    n_attr.data_type = 'FLOAT_VECTOR'
    n_attr.inputs["Name"].default_value = "vertex_normals"

    # ------------------------------------------------
    # Set Mesh Normal (ALWAYS ACTIVE)
    # ------------------------------------------------
    n_set_normal = nodes.new("GeometryNodeSetMeshNormal")
    n_set_normal.location = (-700, 0)
    n_set_normal.mode = 'FREE'
    n_set_normal.domain = 'POINT'

    links.new(group_in.outputs["Geometry"], n_set_normal.inputs["Mesh"])
    links.new(n_attr.outputs["Attribute"], n_set_normal.inputs["Custom Normal"])

    # ------------------------------------------------
    # MESH → POINTS (for rods)
    # ------------------------------------------------
    n_mesh2pts = nodes.new("GeometryNodeMeshToPoints")
    n_mesh2pts.location = (-700, 200)
    n_mesh2pts.mode = 'VERTICES'

    links.new(n_set_normal.outputs["Mesh"], n_mesh2pts.inputs["Mesh"])

    # ------------------------------------------------
    # ALIGN ROTATION TO NORMAL
    # ------------------------------------------------
    n_align = nodes.new("FunctionNodeAlignRotationToVector")
    n_align.location = (-500, 0)
    n_align.axis = 'Z'

    links.new(n_attr.outputs["Attribute"], n_align.inputs["Vector"])

    # ------------------------------------------------
    # LINE (normal rod)
    # ------------------------------------------------
    n_line = nodes.new("GeometryNodeCurvePrimitiveLine")
    n_line.location = (-500, 300)
    n_line.mode = 'POINTS'

    # ------------------------------------------------
    # INSTANCE ON POINTS
    # ------------------------------------------------
    n_inst = nodes.new("GeometryNodeInstanceOnPoints")
    n_inst.location = (-200, 200)

    links.new(n_mesh2pts.outputs["Points"], n_inst.inputs["Points"])
    links.new(n_line.outputs["Curve"], n_inst.inputs["Instance"])
    links.new(n_align.outputs["Rotation"], n_inst.inputs["Rotation"])

    # scale of rods
    n_inst.inputs["Scale"].default_value = (0.25, 0.25, 0.25)

    # ------------------------------------------------
    # PROFILE (make rods visible)
    # ------------------------------------------------
    n_circle = nodes.new("GeometryNodeCurvePrimitiveCircle")
    n_circle.location = (-200, 0)
    n_circle.inputs["Radius"].default_value = 0.003
    n_circle.inputs["Resolution"].default_value = 4

    # ------------------------------------------------
    # CURVE → MESH
    # ------------------------------------------------
    n_curve2mesh = nodes.new("GeometryNodeCurveToMesh")
    n_curve2mesh.location = (0, 150)

    links.new(n_inst.outputs["Instances"], n_curve2mesh.inputs["Curve"])
    links.new(n_circle.outputs["Curve"], n_curve2mesh.inputs["Profile Curve"])

    # ------------------------------------------------
    # SET MATERIAL (reuse collider material)
    # ------------------------------------------------
    n_setmat = nodes.new("GeometryNodeSetMaterial")
    n_setmat.location = (200, 150)

    if mat:
        n_setmat.inputs["Material"].default_value = mat

    links.new(n_curve2mesh.outputs["Mesh"], n_setmat.inputs["Geometry"])

    # ------------------------------------------------
    # JOIN (base mesh + rods)
    # ------------------------------------------------
    n_join = nodes.new("GeometryNodeJoinGeometry")
    n_join.location = (350, 50)

    links.new(n_set_normal.outputs["Mesh"], n_join.inputs["Geometry"])
    links.new(n_setmat.outputs["Geometry"], n_join.inputs["Geometry"])

    # ------------------------------------------------
    # SWITCH (toggle rods)
    # ------------------------------------------------
    n_switch = nodes.new("GeometryNodeSwitch")
    n_switch.location = (500, 50)
    n_switch.input_type = 'GEOMETRY'

    # FALSE → base mesh only
    links.new(n_set_normal.outputs["Mesh"], n_switch.inputs[1])

    # TRUE → mesh + rods
    links.new(n_join.outputs["Geometry"], n_switch.inputs[2])

    links.new(group_in.outputs["Show Normals"], n_switch.inputs["Switch"])

    # ------------------------------------------------
    # OUTPUT
    # ------------------------------------------------
    links.new(n_switch.outputs["Output"], group_out.inputs["Geometry"])

    return group