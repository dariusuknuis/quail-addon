# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy, bmesh
from mathutils import Vector
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty, CollectionProperty
from ...common import state
from ...common.mesh import get_vertex_normal_nodegroup
from ...common.s3dobject import apply_bounding_box_geo, apply_bounding_radius_geo

def update_fpscale(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "dmspritedef2":
        return

    mesh = obj.data
    if not mesh:
        return

    old_scale = self.fpscale_prev
    new_scale = self.fpscale

    if old_scale == new_scale:
        return

    # ----------------------------------------
    # Compute scale factor
    # ----------------------------------------
    scale_factor = 2 ** (old_scale - new_scale)

    # ----------------------------------------
    # Apply to vertices
    # ----------------------------------------
    for v in mesh.vertices:
        v.co *= scale_factor

    mesh.update()

    # ----------------------------------------
    # Store new as previous
    # ----------------------------------------
    self.fpscale_prev = new_scale

def update_bounding_radius(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "dmspritedef2":
        return

    mod = obj.modifiers.get("BoundingSphere")
    if not mod or mod.type != 'NODES':
        return

    # ----------------------------------------
    # Compute effective radius
    # ----------------------------------------
    radius = self.boundingradius if self.useboundingradius else 1.0

    # ----------------------------------------
    # Apply to geo nodes
    # ----------------------------------------
    try:
        mod["Socket_1"] = radius
    except Exception as e:
        print("Failed to set radius:", e)

def update_bounding_box(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "dmspritedef2":
        return

    bounds = (
        (self.b_box_min_x, self.b_box_min_y, self.b_box_min_z),
        (self.b_box_max_x, self.b_box_max_y, self.b_box_max_z),
    )

    mod = obj.modifiers.get("BoundingBox")
    if not mod or mod.type != 'NODES':
        mod = apply_bounding_box_geo(obj, bounds)

    if not mod:
        return

    try:
        # Min / Max
        mod["Socket_1"] = bounds[0]
        mod["Socket_2"] = bounds[1]

        # Use custom vs AABB
        mod["Socket_3"] = self.useboundingbox

    except Exception as e:
        print("BoundingBox update failed:", e)

def update_polyhedron(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "dmspritedef2":
        return

    dmsprite = obj

    # ----------------------------------------
    # Remove ALL polyhedrondefinition children
    # ----------------------------------------
    for child in list(dmsprite.children):
        if child.get("quaildef") == "polyhedrondefinition":
            child.parent = None

    # ----------------------------------------
    # Assign new polyhedron (if any)
    # ----------------------------------------
    new_obj = self.polyhedron

    if not new_obj:
        return

    new_obj.parent = dmsprite

def update_materialpalette(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "dmspritedef2":
        return

    palette_obj = self.materialpalette

    mesh = obj.data
    mesh.materials.clear()

    if not palette_obj:
        return

    palette_props = palette_obj.quail_materialpalette

    for item in palette_props.materials:
        if item.material:
            mesh.materials.append(item.material)

def update_centeroffset(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "dmspritedef2":
        return

    if self.usecenteroffset:
        obj.lock_location = (False, False, False)
    else:
        obj.location = (0.0, 0.0, 0.0)
        obj.lock_location = (True, True, True)

# =========================================================
# PROPERTY GROUPS
# =========================================================
class QuailDMSpriteDef2Properties(bpy.types.PropertyGroup):

    usecenteroffset: BoolProperty(name="Use Center Offset (Location)", default=False, update=update_centeroffset)

    materialpalette: PointerProperty(
        name="Material Palette",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.get("quaildef") == "materialpalette",
        update=update_materialpalette
    )

    dmtrack: StringProperty()

    dmrgbtrack: StringProperty()

    polyhedron: PointerProperty(
        name="Polyhedron",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.get("quaildef") == "polyhedrondefinition",
        update=update_polyhedron
    )

    useparams2: BoolProperty(name="Params2", default=False)
    params2_x: FloatProperty(name="X", default=0.0)
    params2_y: FloatProperty(name="Y", default=0.0)
    params2_z: FloatProperty(name="Z", default=0.0)

    useboundingbox: BoolProperty(name="Bounding Box", default=False, update=update_bounding_box)
    b_box_min_x: FloatProperty(name="Min X", default=0.0, update=update_bounding_box)
    b_box_min_y: FloatProperty(name="Min Y", default=0.0, update=update_bounding_box)
    b_box_min_z: FloatProperty(name="Min Z", default=0.0, update=update_bounding_box)
    b_box_max_x: FloatProperty(name="Max X", default=0.0, update=update_bounding_box)
    b_box_max_y: FloatProperty(name="Max Y", default=0.0, update=update_bounding_box)
    b_box_max_z: FloatProperty(name="Max Z", default=0.0, update=update_bounding_box)

    useboundingradius: BoolProperty(
        name="Bounding Radius",
        default=False,
        update=update_bounding_radius
    )
    boundingradius: FloatProperty(
        name="Radius",
        default=1.0,
        update=update_bounding_radius
    )

    fpscale: IntProperty(update=lambda self, context: update_fpscale(self, context))
    fpscale_prev: IntProperty(default=1)

    # Flags
    usevertexcoloralpha: BoolProperty(name="Vertex Color Alpha", default=False)
    spritedefpolyhedron: BoolProperty(name="Sprite Def Polyhedron", default=False)

class OBJECT_OT_add_default_dmspritedef2(bpy.types.Operator):

    bl_idname = "object.add_default_dmspritedef2"
    bl_label = "Set DMSPRITEDEF2"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        obj = context.object

        return (
            obj and
            obj.type == 'MESH'
        )

    def execute(self, context):

        obj = context.object
        mesh = obj.data

        # Tag object
        obj["quaildef"] = "dmspritedef2"
        props = obj.quail_dmspritedef2

        # Default panel values
        props.usecenteroffset = True
        props.dmtrack = ""
        props.dmrgbtrack = ""
        props.useparams2 = False
        props.params2_x = 0.0
        props.params2_y = 0.0
        props.params2_z = 0.0
        props.useboundingbox = False
        props.useboundingradius = True
        props.usevertexcoloralpha = False
        props.spritedefpolyhedron = False

        # Normalize mesh
        bpy.context.view_layer.objects.active = obj

        if obj.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        # Triangulate
        bmesh.ops.triangulate(bm, faces=list(bm.faces))

        # Create vertex_normals layer
        normal_layer = (
            bm.verts.layers.float_vector.get("vertex_normals")
        )

        # Only generate normals if missing
        if not normal_layer:

            normal_layer = (
                bm.verts.layers.float_vector.new(
                    "vertex_normals"
                )
            )

            bm.normal_update()
            for vert in bm.verts:
                normal = vert.normal.normalized()
                vert[normal_layer] = (
                    normal.x,
                    normal.y,
                    normal.z,
                )

        # Convert vertex colors
        color_attr = None

        # POINT domain existing layer
        if "vertex_colors" in mesh.color_attributes:
            attr = mesh.color_attributes["vertex_colors"]
            if attr.domain == 'POINT':
                color_attr = attr

        # Convert CORNER -> POINT
        if color_attr is None:
            source_attr = None
            for attr in mesh.color_attributes:
                if attr.domain == 'CORNER':
                    source_attr = attr
                    break

            if source_attr:
                point_attr = mesh.color_attributes.new(
                    name="vertex_colors",
                    type='FLOAT_COLOR',
                    domain='POINT',
                )

                accum = {}
                counts = {}

                for poly in mesh.polygons:
                    for loop_index in poly.loop_indices:
                        loop = mesh.loops[loop_index]
                        vidx = loop.vertex_index
                        color = source_attr.data[loop_index].color
                        if vidx not in accum:
                            accum[vidx] = [0.0, 0.0, 0.0, 0.0]
                            counts[vidx] = 0

                        for i in range(4):
                            accum[vidx][i] += color[i]

                        counts[vidx] += 1

                for vidx, col in accum.items():
                    count = counts[vidx]
                    point_attr.data[vidx].color = (
                        col[0] / count,
                        col[1] / count,
                        col[2] / count,
                        col[3] / count,
                    )

                mesh.color_attributes.remove(source_attr)
                color_attr = point_attr

        if color_attr:
            props.usevertexcoloralpha = True

        # Write BMesh back
        bm.to_mesh(mesh)
        bm.free()
        mesh.update()

        # Add vertex normal geo node
        nodegroup = get_vertex_normal_nodegroup()

        if not obj.modifiers.get("VertexNormals"):

            mod = obj.modifiers.new(
                "VertexNormals",
                'NODES'
            )

            mod.node_group = nodegroup

        # ------------------------------------------------
        # Compute bounds
        # ------------------------------------------------

        coords = [v.co.copy() for v in mesh.vertices]

        if coords:
            min_v = Vector((
                min(v.x for v in coords),
                min(v.y for v in coords),
                min(v.z for v in coords),
            ))

            max_v = Vector((
                max(v.x for v in coords),
                max(v.y for v in coords),
                max(v.z for v in coords),
            ))

            props.b_box_min_x = 0.0
            props.b_box_min_y = 0.0
            props.b_box_min_z = 0.0

            props.b_box_max_x = 0.0
            props.b_box_max_y = 0.0
            props.b_box_max_z = 0.0

            # Bounding sphere
            center = (min_v + max_v) * 0.5
            radius = max(
                (v.co - center).length
                for v in mesh.vertices
            )

            extent = (max_v - min_v).length

        props.boundingradius = radius
        apply_bounding_radius_geo(
            parent_obj=obj,
            radius=radius,
            enabled=False,
        )

        apply_bounding_box_geo(
            obj,
            (
                (min_v.x, min_v.y, min_v.z),
                (max_v.x, max_v.y, max_v.z),
            ),
            use_custom=False,
            visible=False,
        )

        # FPSCALE heuristic
        vert_count = max(len(mesh.vertices), 1)
        density = vert_count / max(extent, 0.0001)
        fpscale = int(round(max(5,min(13, 5 + ((density ** 0.75) * 0.25)))))
        props.fpscale_prev = fpscale
        props.fpscale = fpscale

        self.report(
            {'INFO'},
            f"Initialized DMSPRITEDEF2 (fpscale={fpscale})"
        )

        return {'FINISHED'}


# =========================================================
# PANEL
# =========================================================

def draw_dmspritedef2_in_transform(self, context):

    obj = context.object

    if not obj:
        return

    layout = self.layout

    # Show initialize button for normal meshes
    if (
        obj.type == 'MESH' and
        obj.get("quaildef") != "dmspritedef2"
    ):

        box = layout.box()

        box.operator(
            "object.add_default_dmspritedef2",
            text="Set DMSPRITEDEF2",
        )

        return

    # Existing DMSPRITEDEF2 panel
    if obj.get('quaildef') != 'dmspritedef2':
        return

    props = obj.quail_dmspritedef2

    box = layout.box()
    box.label(text="DMSPRITEDEF2")

    box.prop(props, "usecenteroffset")

    box.prop(props, "materialpalette")

    box.prop(props, "dmtrack")

    box.prop(props, "dmrgbtrack")

    box.prop(props, "polyhedron")

    box.prop(props, "useparams2")

    row = box.row(align=True)
    row.prop(props, "params2_x")
    row.prop(props, "params2_y")
    row.prop(props, "params2_z")

    box.prop(props, "useboundingbox")

    row = box.row(align=True)
    row.prop(props, "b_box_min_x")
    row.prop(props, "b_box_min_y")
    row.prop(props, "b_box_min_z")

    row = box.row(align=True)
    row.prop(props, "b_box_max_x")
    row.prop(props, "b_box_max_y")
    row.prop(props, "b_box_max_z")

    box.prop(props, "useboundingradius")

    row = box.row(align=True)
    row.prop(props, "boundingradius")

    box.prop(props, "fpscale")

    box.prop(props, "usevertexcoloralpha")

    box.prop(props, "spritedefpolyhedron")

# =========================================================
# REGISTER
# =========================================================

def register():

    bpy.types.Object.quail_dmspritedef2 = PointerProperty(type=QuailDMSpriteDef2Properties)
    bpy.types.OBJECT_PT_transform.prepend(draw_dmspritedef2_in_transform)

def unregister():
    del bpy.types.Object.quail_dmspritedef2
    bpy.types.OBJECT_PT_transform.remove(draw_dmspritedef2_in_transform)