# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false


import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty

class QuailRGBDeformationTrackDefProperties(bpy.types.PropertyGroup):

    tag: bpy.props.StringProperty(name="Tag")

    sleep: bpy.props.IntProperty(name="Sleep")
    data4: bpy.props.IntProperty(name="Data4")
    usealpha: bpy.props.BoolProperty(name="Use Alpha")

    numframes: bpy.props.IntProperty(name="Num Frames")

    # future use (animation / preview)
    active_frame: bpy.props.IntProperty(name="Frame", default=0, min=0)

def draw_rgbdeformationtrackdef_in_transform(self, context):

    obj = context.object
    if not obj or obj.get("quaildef") != "rgbdeformationtrackdef":
        return

    props = obj.quail_rgbdeformationtrackdef
    layout = self.layout

    box = layout.box()
    box.label(text="RGBDEFORMATIONTRACKDEF")

    box.prop(props, "tag")

    box.prop(props, "sleep")
    box.prop(props, "data4")
    box.prop(props, "usealpha")

    box.label(text=f"Frames: {props.numframes}")

    # optional (future animation control)
    box.prop(props, "active_frame")

def register():

    bpy.types.Object.quail_rgbdeformationtrackdef = bpy.props.PointerProperty(
        type=QuailRGBDeformationTrackDefProperties
    )

    bpy.types.OBJECT_PT_transform.prepend(draw_rgbdeformationtrackdef_in_transform)


def unregister():

    del bpy.types.Object.quail_rgbdeformationtrackdef

    bpy.types.OBJECT_PT_transform.remove(draw_rgbdeformationtrackdef_in_transform)