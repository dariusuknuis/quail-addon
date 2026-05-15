import bpy
import bmesh
from bpy.types import Operator
from mathutils import Vector
from ...common.mesh import merge_verts_by_attrs


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
        in_edit_mode = (
            obj.mode == 'EDIT'
        )

        if in_edit_mode:
            bm = bmesh.from_edit_mesh(me)
        else:
            bm = bmesh.new()
            bm.from_mesh(me)

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        luv = bm.loops.layers.uv.active

        if not luv:
            self.report(
                {'ERROR'},
                "Mesh has no active UV layer"
            )

            if not in_edit_mode:
                bm.free()

            return {'CANCELLED'}

        # Find verts whose linked loops have different UVs
        verts_to_split = []
        for v in bm.verts:
            if len(v.link_loops) < 2:
                continue

            uv_set = set()
            for loop in v.link_loops:
                uv = loop[luv].uv
                uv_set.add((
                    round(uv.x, 6),
                    round(uv.y, 6),
                ))

            if len(uv_set) > 1:
                verts_to_split.append(v)

        print(
            f"Splitting {len(verts_to_split)} "
            f"vertices with mismatched UVs"
        )

        for v in verts_to_split:
            if not v.is_valid:
                continue

            try:
                bmesh.utils.vert_separate(v, list(v.link_edges))
            except Exception as ex:
                print(f"Failed splitting vert: {ex}")

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        merge_verts_by_attrs(bm, float_vec_name="vertex_normals")

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        bmesh.ops.triangulate(bm, faces=list(bm.faces))

        if in_edit_mode:

            bmesh.update_edit_mesh(
                me,
                loop_triangles=True,
                destructive=True,
            )

        else:
            bm.to_mesh(me)
            bm.free()

        me.update()
        self.report(
            {'INFO'},
            "Mesh normalized for game export"
        )

        return {'FINISHED'}