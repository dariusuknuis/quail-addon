import bpy

def create_bounding_radius_empty(parent_obj: bpy.types.Object, radius: float, collection: bpy.types.Collection) -> bpy.types.Object:

    if radius is None or radius <= 0:
        return None

    name = f"{parent_obj.name}_BOUNDINGRADIUS"
    sphere = bpy.data.objects.new(name, None)
    sphere.empty_display_type = 'SPHERE'
    sphere.empty_display_size = radius
    collection.objects.link(sphere)
    sphere.parent = parent_obj
    # sphere.hide_viewport = True
    # sphere.hide_render = True
    sphere.hide_set(True)

    return sphere

def apply_bounding_radius_geo(parent_obj: bpy.types.Object, radius: float, enabled: bool = False):

    if radius is None or radius <= 0:
        return None

    name = "QUAIL_BoundingSphere"

    # ------------------------------------------------
    # Get or create node group
    # ------------------------------------------------
    if name in bpy.data.node_groups:
        ng = bpy.data.node_groups[name]
    else:
        ng = bpy.data.node_groups.new(name, 'GeometryNodeTree')

        # sockets
        ng.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
        ng.interface.new_socket(name="Radius", in_out='INPUT', socket_type='NodeSocketFloat')
        ng.interface.new_socket(name="Enabled", in_out='INPUT', socket_type='NodeSocketBool')

        ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

        nodes = ng.nodes
        links = ng.links
        nodes.clear()

        input_node = nodes.new("NodeGroupInput")
        output_node = nodes.new("NodeGroupOutput")
        bbox = nodes.new("GeometryNodeBoundBox")
        add = nodes.new("ShaderNodeVectorMath")
        add.operation = 'ADD'
        mult = nodes.new("ShaderNodeVectorMath")
        mult.operation = 'MULTIPLY'
        mult.inputs[1].default_value = (0.5, 0.5, 0.5)

        sphere = nodes.new("GeometryNodeMeshUVSphere")
        transform = nodes.new("GeometryNodeTransform")
        mesh_to_curve = nodes.new("GeometryNodeMeshToCurve")
        switch = nodes.new("GeometryNodeSwitch")
        join = nodes.new("GeometryNodeJoinGeometry")

        input_node.location = (-800, 0)
        bbox.location = (-600, -200)
        add.location = (-400, -200)
        mult.location = (-200, -200)

        sphere.location = (-200, 100)
        transform.location = (0, 100)

        mesh_to_curve.location = (200, 100)
        switch.location = (400, 100)
        join.location = (600, 100)
        output_node.location = (800, 100)

        # ------------------------------------------------
        # wiring
        # ------------------------------------------------
        links.new(input_node.outputs["Geometry"], bbox.inputs["Geometry"])

        links.new(bbox.outputs["Min"], add.inputs[0])
        links.new(bbox.outputs["Max"], add.inputs[1])

        links.new(add.outputs["Vector"], mult.inputs[0])
        links.new(mult.outputs["Vector"], transform.inputs["Translation"])

        links.new(input_node.outputs["Radius"], transform.inputs["Scale"])
        links.new(sphere.outputs["Mesh"], transform.inputs["Geometry"])

        links.new(input_node.outputs["Enabled"], switch.inputs["Switch"])
        links.new(transform.outputs["Geometry"], mesh_to_curve.inputs[0])
        links.new(mesh_to_curve.outputs[0], switch.inputs[2])

        links.new(input_node.outputs["Geometry"], join.inputs[0])
        links.new(switch.outputs["Output"], join.inputs[0])

        links.new(join.outputs["Geometry"], output_node.inputs["Geometry"])

    # ------------------------------------------------
    # Apply modifier
    # ------------------------------------------------
    mod = parent_obj.modifiers.get("BoundingSphere")
    if not mod:
        mod = parent_obj.modifiers.new("BoundingSphere", 'NODES')

    mod.node_group = ng

    # ------------------------------------------------
    # Set inputs
    # ------------------------------------------------
    # Input order: Geometry, Radius, Enabled
    mod["Socket_1"] = radius
    mod["Socket_2"] = enabled

    return mod

def get_collision_volume_material() -> bpy.types.Material:
    name = "CollisionVolumeMaterial"

    # Reuse if already exists
    mat = bpy.data.materials.get(name)
    if mat:
        return mat

    # Create new
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    nodes.clear()

    # Nodes
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (300, 0)

    # Magenta color + transparency
    bsdf.inputs["Base Color"].default_value = (1.0, 0.0, 1.0, 1.0)  # magenta
    bsdf.inputs["Alpha"].default_value = 0.25  # translucent

    # Link
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    # Enable transparency
    mat.blend_method = 'BLEND'

    return mat

def attach_collision_volume(parent_obj: bpy.types.Object, poly_tag: str) -> bpy.types.Object | None:

    if not poly_tag:
        return None

    poly_obj = bpy.data.objects.get(poly_tag)

    if poly_obj is None:
        return None

    if poly_obj.get("quaildef") != "polyhedrondefinition":
        return None

    # Just parent it, nothing else
    poly_obj.parent = parent_obj

    return poly_obj

def apply_bounding_box_geo(parent_obj, bounds, use_custom=False, visible=False):

    if not bounds:
        return None

    (min_x, min_y, min_z), (max_x, max_y, max_z) = bounds

    name = "QUAIL_BoundingBox"

    # ------------------------------------------------
    # Create node group (once)
    # ------------------------------------------------
    if name in bpy.data.node_groups:
        ng = bpy.data.node_groups[name]
    else:
        ng = bpy.data.node_groups.new(name, 'GeometryNodeTree')

        # Interface
        ng.interface.new_socket(name="Geometry", in_out='INPUT', socket_type='NodeSocketGeometry')
        ng.interface.new_socket(name="Min", in_out='INPUT', socket_type='NodeSocketVector')
        ng.interface.new_socket(name="Max", in_out='INPUT', socket_type='NodeSocketVector')
        ng.interface.new_socket(name="UseCustom", in_out='INPUT', socket_type='NodeSocketBool')
        ng.interface.new_socket(name="Visible", in_out='INPUT', socket_type='NodeSocketBool')

        ng.interface.new_socket(name="Geometry", in_out='OUTPUT', socket_type='NodeSocketGeometry')

        nodes = ng.nodes
        links = ng.links
        nodes.clear()

        # ------------------------------------------------
        # Nodes
        # ------------------------------------------------
        input_node = nodes.new("NodeGroupInput")
        output_node = nodes.new("NodeGroupOutput")

        bbox = nodes.new("GeometryNodeBoundBox")

        # Switch Custom
        switch_custom = nodes.new("GeometryNodeSwitch")
        switch_custom.input_type = 'GEOMETRY'

        # Math
        add = nodes.new("ShaderNodeVectorMath")
        add.operation = 'ADD'

        mul = nodes.new("ShaderNodeVectorMath")
        mul.operation = 'MULTIPLY'
        mul.inputs[1].default_value = (0.5, 0.5, 0.5)

        sub = nodes.new("ShaderNodeVectorMath")
        sub.operation = 'SUBTRACT'

        # Geometry
        cube = nodes.new("GeometryNodeMeshCube")
        transform = nodes.new("GeometryNodeTransform")
        mesh_to_curve = nodes.new("GeometryNodeMeshToCurve")

        # Visibility switch
        switch_vis = nodes.new("GeometryNodeSwitch")
        switch_vis.input_type = 'GEOMETRY'

        join = nodes.new("GeometryNodeJoinGeometry")

        # ------------------------------------------------
        # Layout
        # ------------------------------------------------
        input_node.location = (-1000, 0)
        bbox.location = (-800, -200)

        switch_custom.location = (-600, 0)

        add.location = (-400, 0)
        mul.location = (-200, 0)
        sub.location = (-400, -200)

        cube.location = (0, -200)
        transform.location = (200, -200)
        mesh_to_curve.location = (400, -200)

        switch_vis.location = (600, -200)
        join.location = (800, 0)
        output_node.location = (1000, 0)

        # ------------------------------------------------
        # Wiring
        # ------------------------------------------------

        # Geometry to BoundingBox
        links.new(input_node.outputs["Geometry"], bbox.inputs[0])

        # UseCustom switch for Min
        links.new(input_node.outputs["UseCustom"], switch_custom.inputs["Switch"])
        links.new(bbox.outputs[0], switch_custom.inputs[1])  # False
        links.new(transform.outputs["Geometry"], switch_custom.inputs[2])  # True

        # center = (min + max) * 0.5
        links.new(input_node.outputs["Min"], add.inputs[0])
        links.new(input_node.outputs["Max"], add.inputs[1])
        links.new(add.outputs[0], mul.inputs[0])

        # size = max - min
        links.new(input_node.outputs["Max"], sub.inputs[0])
        links.new(input_node.outputs["Min"], sub.inputs[1])

        # cube
        links.new(cube.outputs["Mesh"], transform.inputs["Geometry"])
        links.new(sub.outputs[0], transform.inputs["Scale"])
        links.new(mul.outputs[0], transform.inputs["Translation"])

        # wireframe
        links.new(switch_custom.outputs[0], mesh_to_curve.inputs["Mesh"])

        # visibility
        links.new(input_node.outputs["Visible"], switch_vis.inputs["Switch"])
        links.new(mesh_to_curve.outputs["Curve"], switch_vis.inputs[2])

        # join
        links.new(input_node.outputs["Geometry"], join.inputs[0])
        links.new(switch_vis.outputs[0], join.inputs[0])

        links.new(join.outputs["Geometry"], output_node.inputs["Geometry"])

    # ------------------------------------------------
    # Apply modifier
    # ------------------------------------------------
    mod = parent_obj.modifiers.get("BoundingBox")
    if not mod:
        mod = parent_obj.modifiers.new("BoundingBox", 'NODES')

    mod.node_group = ng

    # ------------------------------------------------
    # Set inputs
    # ------------------------------------------------
    try:
        mod["Socket_1"][0] = min_x
        mod["Socket_1"][1] = min_y
        mod["Socket_1"][2] = min_z
        mod["Socket_2"][0] = max_x
        mod["Socket_2"][1] = max_y
        mod["Socket_2"][2] = max_z
        mod["Socket_3"] = use_custom              # UseCustom
        mod["Socket_4"] = visible                 # Visible
    except Exception as e:
        print("BoundingBox input error:", e)

    return mod

def collect_sprite_graph(root_obj):
    visited = set()
    stack = [root_obj]

    while stack:
        obj = stack.pop()

        if obj in visited:
            continue

        visited.add(obj)

        # ----------------------------------------
        # Children
        # ----------------------------------------
        for child in obj.children:
            stack.append(child)

        # ----------------------------------------
        # CHILD_OF constraints (very important)
        # ----------------------------------------
        for other in bpy.data.objects:
            for c in other.constraints:
                if c.type == 'CHILD_OF' and c.target == obj:
                    stack.append(other)

    return visited