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
    sphere.hide_viewport = True
    sphere.hide_render = True

    return sphere

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