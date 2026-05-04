# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty, CollectionProperty
from ...common import state
from ...common.s3dobject import apply_bounding_box_geo

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