# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty
from ...common import state

def update_has_scalefactor(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "actorinst":
        return

    if not self.has_scalefactor:
        # Reset scale to 1
        obj.scale = (1.0, 1.0, 1.0)

        # Lock scale
        obj.lock_scale = (True, True, True)
    else:
        # Unlock scale
        obj.lock_scale = (False, False, False)

def update_has_location(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "actorinst":
        return

    if not self.has_location:
        # Zero transforms
        obj.location = (0.0, 0.0, 0.0)
        obj.rotation_euler = (0.0, 0.0, 0.0)

        # Lock transforms
        obj.lock_location = (True, True, True)
        obj.lock_rotation = (True, True, True)
    else:
        # Unlock transforms
        obj.lock_location = (False, False, False)
        obj.lock_rotation = (False, False, False)

class OBJECT_OT_add_quail_actorinst(bpy.types.Operator):
    bl_idname = "object.add_quail_actorinst"
    bl_label = "ActorInst"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        obj = bpy.data.objects.new("ActorInst", None)
        obj["quaildef"] = "actorinst"

        context.collection.objects.link(obj)

        return {'FINISHED'}

class QuailActorInstProperties(bpy.types.PropertyGroup):

    # -------------------------
    # Sprite
    # -------------------------
    sprite: PointerProperty(
        name="Sprite",
        type=bpy.types.Collection,
        poll=lambda self, col: col.get("quaildef") == "actordef"
    )

    # -------------------------
    # Current Action
    # -------------------------
    has_currentaction: BoolProperty(name="Current Action", default=False)
    currentaction: StringProperty(name="Action", default="")

    # -------------------------
    # Location
    # -------------------------
    has_location: BoolProperty(name="Location", default=True, update=update_has_location)

    # -------------------------
    # Optional fields
    # -------------------------
    has_boundingradius: BoolProperty(name="Bounding Radius", default=True)
    boundingradius: FloatProperty(name="Radius", default=1.0)

    has_scalefactor: BoolProperty(name="Scale Factor", default=True)

    has_sound: BoolProperty(name="Sound", default=False)
    sound: StringProperty(name="Sound Ref", default="")

    has_active: BoolProperty(name="Active", default=False)
    active: IntProperty(name="Active", default=1)

    has_dmrgbtrack: BoolProperty(name="DMRGB Track", default=False)
    dmrgbtrack: StringProperty(name="Track Ref", default="")

    # -------------------------
    # Required
    # -------------------------
    spritevolumeonly: BoolProperty(name="Sprite Volume Only", default=False)

    sphere: StringProperty(name="Sphere", default="")
    sphereradius: FloatProperty(name="Sphere Radius", default=0.0)

    useboundingbox: BoolProperty(name="Use Bounding Box", default=True)

    userdata: StringProperty(name="User Data", default="")

def draw_actorinst_in_transform(self, context):
    obj = context.object

    if not obj or obj.get("quaildef") != "actorinst":
        return

    props = obj.quail_actorinst
    layout = self.layout

    box = layout.box()
    box.label(text="ACTORINST")

    # -------------------------
    # Sprite
    # -------------------------
    box.prop(props, "sprite")

    # -------------------------
    # Current Action
    # -------------------------
    box.prop(props, "has_currentaction")
    if props.has_currentaction:
        box.prop(props, "currentaction")

    # -------------------------
    # Location
    # -------------------------

    box.prop(props, "has_location")

    # -------------------------
    # Optional
    # -------------------------
    box.prop(props, "has_boundingradius")
    if props.has_boundingradius:
        box.prop(props, "boundingradius")

    box.prop(props, "has_scalefactor")

    box.prop(props, "has_sound")
    if props.has_sound:
        box.prop(props, "sound")

    box.prop(props, "has_active")
    if props.has_active:
        box.prop(props, "active")

    box.prop(props, "spritevolumeonly")

    box.prop(props, "has_dmrgbtrack")
    if props.has_dmrgbtrack:
        box.prop(props, "dmrgbtrack")

    box.prop(props, "sphere")
    box.prop(props, "sphereradius")

    box.prop(props, "useboundingbox")

    box.prop(props, "userdata")

def register():
    bpy.types.Object.quail_actorinst = PointerProperty(type=QuailActorInstProperties)
    bpy.types.OBJECT_PT_transform.prepend(draw_actorinst_in_transform)


def unregister():
    del bpy.types.Object.quail_actorinst
    bpy.types.OBJECT_PT_transform.remove(draw_actorinst_in_transform)