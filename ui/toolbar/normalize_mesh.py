import bpy
import bmesh
from bpy.types import Operator
from mathutils import Vector
from ...common.mesh import merge_verts_by_attrs, split_vertices_by_uv


class VIEW3D_PT_quail_mesh_cleanup(bpy.types.Panel):

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Quail"
    bl_label = "Normalize Mesh"

    @classmethod
    def poll(cls, context):

        obj = context.object

        if not obj:
            return False

        if obj.type != 'MESH':
            return False

        return obj.get("quaildef") in {
            "dmspritedef2",
            "dmspritedefinition",
            "eqterdef",
            "eqmodeldef",
        }

    def draw(self, context):

        layout = self.layout

        layout.operator(
            "quail.normalize_mesh",
            icon='MOD_TRIANGULATE',
        )

class QUAIL_OT_normalize_game_vertices(Operator):
    bl_idname = "quail.normalize_mesh"
    bl_label = "Normalize Mesh"
    bl_description = (
        "Split vertices with mismatched UVs, "
        "merge compatible verts, and triangulate"
    )

    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        obj = context.object

        if not obj:
            return False

        if obj.type != 'MESH':
            return False

        return obj.get("quaildef") in {
            "dmspritedef2",
            "dmspritedefinition",
            "eqterdef",
            "eqmodeldef",
        }

    def execute(self, context):

        obj = context.object
        me = obj.data

        split_vertices_by_uv(obj)

        bm = bmesh.new()
        bm.from_mesh(me)

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        merge_verts_by_attrs(
            bm,
            float_vec_name="vertex_normals"
        )

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        bmesh.ops.triangulate(
            bm,
            faces=list(bm.faces)
        )

        bm.to_mesh(me)
        bm.free()

        me.update()

        self.report(
            {'INFO'},
            "Mesh normalized for game export"
        )

        return {'FINISHED'}