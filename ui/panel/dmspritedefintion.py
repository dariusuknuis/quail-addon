# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty, CollectionProperty
from ...common import state

def update_materialpalette(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "dmspritedefinition":
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
    if not obj or obj.get("quaildef") != "dmspritedefinition":
        return

    if self.hascenter:
        obj.lock_location = (False, False, False)
    else:
        obj.location = (0.0, 0.0, 0.0)
        obj.lock_location = (True, True, True)

# =========================================================
# PROPERTY GROUPS
# =========================================================
class QuailDMSpriteDefinitionProperties(bpy.types.PropertyGroup):

    fragment1: IntProperty(name="Fragment1")

    materialpalette: PointerProperty(
        name="Material Palette",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.get("quaildef") == "materialpalette",
        update=update_materialpalette
    )

    fragment3: IntProperty(name="Fragment3")

    hascenter: BoolProperty(name="Has Center (Location)", default=False, update=update_centeroffset)

    hasparams1: BoolProperty(name="Params1", default=False)
    params1_x: FloatProperty(name="X", default=0.0)
    params1_y: FloatProperty(name="Y", default=0.0)
    params1_z: FloatProperty(name="Z", default=0.0)

    data8: IntProperty(name="Data8")

    hasparams2: BoolProperty(name="Params2", default=False)
    params2_x: FloatProperty(name="X", default=0.0)
    params2_y: FloatProperty(name="Y", default=0.0)
    params2_z: FloatProperty(name="Z", default=0.0)

# =========================================================
# PANEL
# =========================================================

def draw_dmspritedefinition_in_transform(self, context):
    obj = context.object
    if not obj or obj.get('quaildef') != 'dmspritedefinition':
        return

    props = obj.quail_dmspritedefinition
    layout = self.layout

    box = layout.box()
    box.label(text="DMSPRITEDEFINITION")

    box.prop(props, "fragment1")

    box.prop(props, "materialpalette")

    box.prop(props, "fragment3")

    box.prop(props, "hascenter")

    box.prop(props, "hasparams1")
    if props.hasparams1:
        row = box.row(align=True)
        row.prop(props, "params1_x")
        row.prop(props, "params1_y")
        row.prop(props, "params1_z")

    box.prop(props, "data8")

    box.prop(props, "hasparams2")
    if props.hasparams2:
        row = box.row(align=True)
        row.prop(props, "params2_x")
        row.prop(props, "params2_y")
        row.prop(props, "params2_z")

# =========================================================
# REGISTER
# =========================================================

def register():

    bpy.types.Object.quail_dmspritedefinition = PointerProperty(type=QuailDMSpriteDefinitionProperties)
    bpy.types.OBJECT_PT_transform.prepend(draw_dmspritedefinition_in_transform)

def unregister():
    del bpy.types.Object.quail_dmspritedefinition
    bpy.types.OBJECT_PT_transform.remove(draw_dmspritedefinition_in_transform)