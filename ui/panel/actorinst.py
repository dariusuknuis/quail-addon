import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty

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
    has_currentaction: BoolProperty(name="Has Current Action", default=False)
    currentaction: StringProperty(name="Current Action", default="")

    # -------------------------
    # Location
    # -------------------------
    has_location: BoolProperty(name="Has Location", default=False)

    loc_x: FloatProperty(name="X", default=0.0)
    loc_y: FloatProperty(name="Y", default=0.0)
    loc_z: FloatProperty(name="Z", default=0.0)

    rot_x: FloatProperty(name="Rot X", default=0.0)
    rot_y: FloatProperty(name="Rot Y", default=0.0)
    rot_z: FloatProperty(name="Rot Z", default=0.0)

    # -------------------------
    # Optional fields
    # -------------------------
    has_boundingradius: BoolProperty(name="Has Bounding Radius", default=False)
    boundingradius: FloatProperty(name="Bounding Radius", default=0.0)

    has_scalefactor: BoolProperty(name="Has Scale Factor", default=False)
    scalefactor: FloatProperty(name="Scale Factor", default=1.0)

    sound: StringProperty(name="Sound", default="")

    has_active: BoolProperty(name="Has Active", default=False)
    active: IntProperty(name="Active", default=1)

    # -------------------------
    # Required
    # -------------------------
    spritevolumeonly: BoolProperty(name="Sprite Volume Only", default=False)

    dmrgbtrack: StringProperty(name="DMRGB Track", default="")

    sphere: StringProperty(name="Sphere", default="")
    sphereradius: FloatProperty(name="Sphere Radius", default=0.0)

    useboundingbox: BoolProperty(name="Use Bounding Box", default=False)

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
    if props.has_location:
        col = box.column(align=True)

        col.label(text="Position")
        row = col.row(align=True)
        row.prop(props, "loc_x")
        row.prop(props, "loc_y")
        row.prop(props, "loc_z")

        col.label(text="Rotation")
        row = col.row(align=True)
        row.prop(props, "rot_x")
        row.prop(props, "rot_y")
        row.prop(props, "rot_z")

    # -------------------------
    # Optional
    # -------------------------
    box.prop(props, "has_boundingradius")
    if props.has_boundingradius:
        box.prop(props, "boundingradius")

    box.prop(props, "has_scalefactor")
    if props.has_scalefactor:
        box.prop(props, "scalefactor")

    box.prop(props, "sound")

    box.prop(props, "has_active")
    if props.has_active:
        box.prop(props, "active")

    # -------------------------
    # Required
    # -------------------------
    box.prop(props, "spritevolumeonly")
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