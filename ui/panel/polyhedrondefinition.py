# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty, CollectionProperty
from ...common import state

def update_bounding_radius(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "polyhedrondefinition":
        return

    empty_name = f"{obj.name}_BOUNDINGRADIUS"
    empty = bpy.data.objects.get(empty_name)

    if not empty:
        return

    empty.empty_display_size = self.boundingradius

def update_scale(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "polyhedrondefinition":
        return

    if self.has_scalefactor:
        obj.scale[0] = self.scalefactor
        obj.scale[1] = self.scalefactor
        obj.scale[2] = self.scalefactor
    else:
        obj.scale[0] = 1.0
        obj.scale[1] = 1.0
        obj.scale[2] = 1.0

# =========================================================
# PROPERTY GROUPS
# =========================================================
class QuailPolyhedronDefinitionProperties(bpy.types.PropertyGroup):

    boundingradius: FloatProperty(
        name="Bounding Radius",
        default=1.0,
        update=update_bounding_radius
    )

    has_scalefactor: BoolProperty(name="Scale Factor", default=False, update=update_scale)
    scalefactor: FloatProperty(default=0.0, update=update_scale)

# =========================================================
# PANEL
# =========================================================

def draw_polyhedrondefinition_in_transform(self, context):
    obj = context.object
    if not obj or obj.get('quaildef') != 'polyhedrondefinition':
        return

    props = obj.quail_polyhedrondefinition
    layout = self.layout

    box = layout.box()
    box.label(text="POLYHEDRONDEFINITION")

    box.prop(props, "boundingradius")

    box.prop(props, "has_scalefactor")
    if props.has_scalefactor:
        row = box.row(align=True)
        row.prop(props, "scalefactor")

# =========================================================
# REGISTER
# =========================================================

def register():

    bpy.types.Object.quail_polyhedrondefinition = PointerProperty(type=QuailPolyhedronDefinitionProperties)
    bpy.types.OBJECT_PT_transform.prepend(draw_polyhedrondefinition_in_transform)

def unregister():
    del bpy.types.Object.quail_polyhedrondefinition
    bpy.types.OBJECT_PT_transform.remove(draw_polyhedrondefinition_in_transform)