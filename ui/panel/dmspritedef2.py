# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty, CollectionProperty
from ...common import state
from ...common.s3dobject import create_bounding_box

def update_bounding_radius(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "dmspritedef2":
        return

    empty_name = f"{obj.name}_BOUNDINGRADIUS"
    empty = bpy.data.objects.get(empty_name)

    if not empty:
        return

    if self.useboundingradius:
        empty.empty_display_size = self.boundingradius
    else:
        # Default fallback
        empty.empty_display_size = 1.0

def update_bounding_box(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "dmspritedef2":
        return

    bb_name = f"{obj.name}_BOUNDINGBOX"
    existing = bpy.data.objects.get(bb_name)

    if not self.useboundingbox:
        if existing:
            bpy.data.objects.remove(existing, do_unlink=True)
        return

    bounds = (
        (self.b_box_min_x, self.b_box_min_y, self.b_box_min_z),
        (self.b_box_max_x, self.b_box_max_y, self.b_box_max_z),
    )

    # Remove old
    if existing:
        bpy.data.objects.remove(existing, do_unlink=True)

    create_bounding_box(obj, bounds)

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

    arm = obj

    if self.usecenteroffset:
        arm.location[0] = self.center_x
        arm.location[1] = self.center_y
        arm.location[2] = self.center_z
    else:
        arm.location[0] = 0.0
        arm.location[1] = 0.0
        arm.location[2] = 0.0

# =========================================================
# PROPERTY GROUPS
# =========================================================
class QuailDMSpriteDef2Properties(bpy.types.PropertyGroup):

    usecenteroffset: BoolProperty(name="Center Offset", default=False, update=update_centeroffset)
    center_x: FloatProperty(name="X", default=0.0, update=update_centeroffset)
    center_y: FloatProperty(name="Y", default=0.0, update=update_centeroffset)
    center_z: FloatProperty(name="Z", default=0.0, update=update_centeroffset)

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
        poll=lambda self, obj: obj.get("quaildef") == "polyhedrondefinition"
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

    fpscale: IntProperty()

    # Flags
    usevertexcoloralpha: BoolProperty(name="Vertex Color Alpha", default=False)
    spritedefpolyhedron: BoolProperty(name="Sprite Def Polyhedron", default=False)


# =========================================================
# PANEL
# =========================================================

def draw_dmspritedef2_in_transform(self, context):
    obj = context.object
    if not obj or obj.get('quaildef') != 'dmspritedef2':
        return

    props = obj.quail_dmspritedef2
    layout = self.layout

    box = layout.box()
    box.label(text="DMSPRITEDEF2")

    box.prop(props, "usecenteroffset")
    row = box.row(align=True)
    row.prop(props, "center_x")
    row.prop(props, "center_y")
    row.prop(props, "center_z")

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