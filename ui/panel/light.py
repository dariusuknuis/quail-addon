# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import FloatProperty, FloatVectorProperty, BoolProperty, IntProperty, StringProperty, CollectionProperty, PointerProperty
from ...common import state

def apply_light(self, context):
    obj = context.object
    if not obj or obj.type != 'LIGHT':
        return

    light = obj.data
    light.energy = self.lightlevel * 100.0
    light.color = self.color
    light.shadow_soft_size = self.radiusofinfluence

def update_color_vector(self, context):
    if state.QUAIL_UPDATING:
        return

    state.QUAIL_UPDATING = True
    try:
        self.color_r, self.color_g, self.color_b = self.color
        apply_light(self, context)
    finally:
        state.QUAIL_UPDATING = False

def update_color_floats(self, context):
    if state.QUAIL_UPDATING:
        return

    state.QUAIL_UPDATING = True
    try:
        self.color = (self.color_r, self.color_g, self.color_b)
        apply_light(self, context)
    finally:
        state.QUAIL_UPDATING = False

class QuailLightProperties(bpy.types.PropertyGroup):

    # -------------------------
    # LIGHTDEFINITION
    # -------------------------
    has_currentframe: BoolProperty(name="Current Frame", default=False)
    currentframe: IntProperty(default=1)
    numframes: IntProperty(default=1)
    lightlevel: FloatProperty(name="Light Level", default=1.0, update=apply_light)

    has_sleep: BoolProperty(name="Sleep", default=False)
    sleep: IntProperty(default=0)

    haveskipframes: BoolProperty(name="Have Skip Frames", default=False)
    skipframes: BoolProperty(name="Skip Frames", default=False)

    # -------------------------
    # COLOR
    # -------------------------
    color: FloatVectorProperty(
        name="Color",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=update_color_vector
    )

    color_r: FloatProperty(name="R", default=1.0, min=0.0, max=1.0, update=update_color_floats)
    color_g: FloatProperty(name="G", default=1.0, min=0.0, max=1.0, update=update_color_floats)
    color_b: FloatProperty(name="B", default=1.0, min=0.0, max=1.0, update=update_color_floats)

    # -------------------------
    # POINTLIGHT
    # -------------------------
    light: StringProperty(name="Light Def", default="")
    radiusofinfluence: FloatProperty(name="Radius", default=100.0, update=apply_light)

    static: BoolProperty(name="Static", default=False)
    staticinfluence: BoolProperty(name="Static Influence", default=False)
    dynamicinfluence: BoolProperty(name="Dynamic Influence", default=True)

    has_regions: BoolProperty(name="Regions", default=False)
    regions: StringProperty(name="Regions", default="")  # simple for now

def draw_light_in_transform(self, context):
    obj = context.object

    if not obj or obj.get("quaildef") != "light":
        return

    props = obj.quail_light
    layout = self.layout

    box = layout.box()

    # -------------------------
    # Light Definition
    # -------------------------

    box.label(text="LIGHTDEFINITION")

    box.prop(props, "has_currentframe")
    if props.has_currentframe:
        box.prop(props, "currentframe")

    box.prop(props, "numframes")

    box.prop(props, "lightlevel")

    col = box.column(align=True)
    col.label(text="Color")

    row = col.row(align=True)
    row.prop(props, "color_r", text="R")
    row.prop(props, "color_g", text="G")
    row.prop(props, "color_b", text="B")

    col.prop(props, "color", text="")

    box.prop(props, "has_sleep")
    if props.has_sleep:
        box.prop(props, "sleep")

    box.prop(props, "haveskipframes")
    if props.haveskipframes:
        box.prop(props, "skipframes")

    # -------------------------
    # Point Light
    # -------------------------

    box.label(text="POINTLIGHT")

    box.prop(props, "light")

    box.prop(props, "static")
    box.prop(props, "staticinfluence")
    box.prop(props, "dynamicinfluence")

    box.prop(props, "radiusofinfluence")

    # -------------------------
    # Regions
    # -------------------------
    box.prop(props, "has_regions")
    if props.has_regions:
        box.prop(props, "regions")

def register():
    bpy.types.Object.quail_light = PointerProperty(type=QuailLightProperties)
    bpy.types.OBJECT_PT_transform.prepend(draw_light_in_transform)


def unregister():
    del bpy.types.Object.quail_light
    bpy.types.OBJECT_PT_transform.remove(draw_light_in_transform)