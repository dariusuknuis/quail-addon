# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false

import bpy
from bpy.props import BoolProperty, FloatProperty, FloatVectorProperty, PointerProperty
from ...common import state
from ...common.s3dobject import apply_bounding_radius_geo

def update_centeroffset(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "sprite3ddef":
        return

    if self.hascenteroffset:
        obj.lock_location = (False, False, False)
    else:
        obj.location = (0.0, 0.0, 0.0)
        obj.lock_location = (True, True, True)


def update_bounding_radius(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "sprite3ddef":
        return

    mod = obj.modifiers.get("BoundingSphere")
    if not mod or mod.type != 'NODES':
        mod = apply_bounding_radius_geo(obj, self.boundingradius, enabled=True)

    if not mod:
        return

    try:
        mod["Socket_1"] = self.boundingradius if self.hasboundingradius else 1.0
    except Exception as e:
        print("Sprite3D bounding radius update failed:", e)


# =========================================================
# PROPERTY GROUP
# =========================================================

class QuailSprite3DDefProperties(bpy.types.PropertyGroup):

    enablegouraud2: BoolProperty(
        name="Enable Gouraud2",
        default=False
    )

    # ----------------------------------------
    # Center offset
    # ----------------------------------------

    hascenteroffset: BoolProperty(
        name="Has Center Offset (Location)",
        default=False,
        update=update_centeroffset
    )

    # ----------------------------------------
    # Bounding radius
    # ----------------------------------------

    hasboundingradius: BoolProperty(
        name="Bounding Radius",
        default=False,
        update=update_bounding_radius
    )

    boundingradius: FloatProperty(
        name="Radius",
        default=1.0,
        update=update_bounding_radius
    )


# =========================================================
# PANEL
# =========================================================

def draw_sprite3ddef_in_transform(self, context):

    obj = context.object
    if not obj or obj.get("quaildef") != "sprite3ddef":
        return

    props = obj.quail_sprite3ddef
    layout = self.layout

    box = layout.box()
    box.label(text="SPRITE3DDEF")

    box.prop(props, "enablegouraud2")

    box.prop(props, "hascenteroffset")

    box.prop(props, "hasboundingradius")
    if props.hasboundingradius:
        box.prop(props, "boundingradius")


# =========================================================
# REGISTER
# =========================================================

def register():

    bpy.types.Object.quail_sprite3ddef = PointerProperty(
        type=QuailSprite3DDefProperties
    )

    bpy.types.OBJECT_PT_transform.prepend(draw_sprite3ddef_in_transform)


def unregister():

    del bpy.types.Object.quail_sprite3ddef

    bpy.types.OBJECT_PT_transform.remove(draw_sprite3ddef_in_transform)