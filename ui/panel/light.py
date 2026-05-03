# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import FloatProperty, BoolProperty, IntProperty, StringProperty, CollectionProperty, PointerProperty

def update_light(self, context):
    obj = context.object
    if not obj or obj.type != 'LIGHT':
        return

    light = obj.data

    light.energy = self.lightlevel * 1000.0
    light.color = (self.color_r, self.color_g, self.color_b)
    light.shadow_soft_size = self.radiusofinfluence

class QuailLightProperties(bpy.types.PropertyGroup):

    # -------------------------
    # LIGHTDEFINITION
    # -------------------------
    lightlevel: FloatProperty(name="Light Level", default=1.0)

    has_sleep: BoolProperty(name="Sleep", default=False)
    sleep: IntProperty(default=0)

    haveskipframes: BoolProperty(name="Have Skip Frames", default=False)
    skipframes: IntProperty(name="Skip Frames", default=0)

    # -------------------------
    # COLOR
    # -------------------------
    color_r: FloatProperty(name="R", default=1.0, min=0.0, max=1.0)
    color_g: FloatProperty(name="G", default=1.0, min=0.0, max=1.0)
    color_b: FloatProperty(name="B", default=1.0, min=0.0, max=1.0)

    # -------------------------
    # POINTLIGHT
    # -------------------------
    radiusofinfluence: FloatProperty(name="Radius", default=100.0)

    static: BoolProperty(name="Static", default=False)
    staticinfluence: BoolProperty(name="Static Influence", default=False)
    dynamicinfluence: BoolProperty(name="Dynamic Influence", default=True)

    regions: StringProperty(name="Regions", default="")  # simple for now

def draw_light_in_transform(self, context):
    obj = context.object

    if not obj or obj.get("quaildef") != "light":
        return

    props = obj.quail_light
    layout = self.layout

    box = layout.box()
    box.label(text="LIGHT")

    # -------------------------
    # Light Level
    # -------------------------
    box.prop(props, "lightlevel")

    # -------------------------
    # Color
    # -------------------------
    col = box.column(align=True)
    col.label(text="Color")
    col.prop(props, "color_r")
    col.prop(props, "color_g")
    col.prop(props, "color_b")

    # -------------------------
    # Sleep
    # -------------------------
    box.prop(props, "has_sleep")
    if props.has_sleep:
        box.prop(props, "sleep")

    # -------------------------
    # Skip Frames
    # -------------------------
    box.prop(props, "haveskipframes")
    if props.haveskipframes:
        box.prop(props, "skipframes")

    # -------------------------
    # Radius
    # -------------------------
    box.prop(props, "radiusofinfluence")

    # -------------------------
    # Flags
    # -------------------------
    col = box.column(align=True)
    col.label(text="Flags")
    col.prop(props, "static")
    col.prop(props, "staticinfluence")
    col.prop(props, "dynamicinfluence")

    # -------------------------
    # Regions
    # -------------------------
    box.prop(props, "regions")

def register():
    bpy.types.Object.quail_light = PointerProperty(type=QuailLightProperties)
    bpy.types.OBJECT_PT_transform.prepend(draw_light_in_transform)


def unregister():
    del bpy.types.Object.quail_light
    bpy.types.OBJECT_PT_transform.remove(draw_light_in_transform)