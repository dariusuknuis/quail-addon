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

def create_bounding_box(mesh_obj, bounding_box_data):

    if not mesh_obj or mesh_obj.type != 'MESH':
        return None

    # Skip if all zeros
    if not any(v != 0 for pair in bounding_box_data for v in pair):
        return None

    min_x, min_y, min_z = bounding_box_data[0]
    max_x, max_y, max_z = bounding_box_data[1]

    # Remove existing box
    bb_name = f"{mesh_obj.name}_BOUNDINGBOX"
    existing = bpy.data.objects.get(bb_name)
    if existing:
        bpy.data.objects.remove(existing, do_unlink=True)

    # Geometry
    vertices = [
        (min_x, min_y, min_z), (max_x, min_y, min_z),
        (max_x, max_y, min_z), (min_x, max_y, min_z),
        (min_x, min_y, max_z), (max_x, min_y, max_z),
        (max_x, max_y, max_z), (min_x, max_y, max_z)
    ]

    faces = [
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7)
    ]

    mesh = bpy.data.meshes.new(f"{mesh_obj.name}_BOUNDINGBOX")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    bbox_obj = bpy.data.objects.new(bb_name, mesh)

    # Your material
    mat = get_collision_volume_material()
    if mat:
        bbox_obj.data.materials.append(mat)

    # Link to same collection
    mesh_obj.users_collection[0].objects.link(bbox_obj)

    # Parent
    bbox_obj.parent = mesh_obj

    bbox_obj.hide_set(True)

    return bbox_obj

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