import bpy, bmesh, re
from mathutils import Vector, Matrix
from ...common.mesh import merge_verts_by_attrs, rearrange_uvs


class OBJECT_OT_format_world(bpy.types.Operator):
    bl_idname = "object.format_world"
    bl_label = "Format World"
    bl_description = "Align UVs of region meshes and join into a single terrain mesh"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        result = run_format_world()
        if result == {'FINISHED'}:
            self.report({'INFO'}, "World formatted successfully")
        else:
            self.report({'WARNING'}, "World formatting was cancelled or failed")
        return result

def run_format_world():

    context = bpy.context

    # --------------------------------------------------------
    # REGION_MESHES collection
    # --------------------------------------------------------

    region_collection = bpy.data.collections.get("REGION_MESHES")

    if not region_collection:
        print("[Format World] REGION_MESHES collection not found")
        return {'CANCELLED'}

    # --------------------------------------------------------
    # Active WORLDDEF collection
    # --------------------------------------------------------

    layer_col = context.view_layer.active_layer_collection

    world_collection = layer_col.collection

    if world_collection.get("quaildef") != "worlddef":

        print(
            "[Format World] Active collection must "
            "have quaildef='worlddef'"
        )

        return {'CANCELLED'}

    # --------------------------------------------------------
    # Collect region meshes
    # --------------------------------------------------------
    meshes = [
        obj for obj in region_collection.objects
        if obj.type == 'MESH'
    ]

    if not meshes:
        print("[Format World] No meshes found in REGION_MESHES")
        return {'CANCELLED'}

    # --------------------------------------------------------
    # Join meshes
    # --------------------------------------------------------

    bpy.ops.object.select_all(action='DESELECT')

    for obj in meshes:
        obj.select_set(True)

    context.view_layer.objects.active = meshes[0]

    print(f"[Format World] Joining {len(meshes)} meshes...")

    bpy.ops.object.join()

    joined = context.view_layer.objects.active

    # --------------------------------------------------------
    # Terrain naming
    # --------------------------------------------------------

    base_name = (world_collection.name.replace("_WORLDDEF", "").upper())

    terrain_name = f"{base_name}_TERRAIN"

    joined.name = terrain_name
    joined.data.name = terrain_name

    # --------------------------------------------------------
    # Apply location to mesh
    # --------------------------------------------------------

    translation = joined.location.copy()

    if translation.length_squared != 0.0:

        joined.data.transform(
            Matrix.Translation(translation)
        )

        joined.location = Vector((0.0, 0.0, 0.0))

    # --------------------------------------------------------
    # BMesh processing
    # --------------------------------------------------------

    bm = bmesh.new()
    bm.from_mesh(joined.data)

    rearrange_uvs(bm)

    merge_verts_by_attrs(bm)

    bm.to_mesh(joined.data)
    joined.data.update()

    bm.free()

    # Tag as formatted terrain
    joined["Formatted Terrain"] = True

    # --------------------------------------------------------
    # Smooth shading
    # --------------------------------------------------------

    for poly in joined.data.polygons:
        poly.use_smooth = True

    # --------------------------------------------------------
    # Delete WORLD_BOUNDS
    # --------------------------------------------------------

    wb = bpy.data.objects.get("WORLD_BOUNDS")

    if wb:
        bpy.data.objects.remove(wb, do_unlink=True)

    # --------------------------------------------------------
    # Remove REGION collection
    # --------------------------------------------------------

    region_col = bpy.data.collections.get("REGIONS")

    if region_col:
        for obj in list(region_col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(region_col)

    # --------------------------------------------------------
    # Remove WorldTree_Root collection
    # --------------------------------------------------------

    worldtree_col = bpy.data.collections.get("WORLDTREE")

    if worldtree_col:
        for obj in list(worldtree_col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(worldtree_col)


    print(f"[Format World] Created '{terrain_name}'")

    return {'FINISHED'}