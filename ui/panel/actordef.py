# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
import os
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty

def update_lod_sprite(self, context):
    obj = context.object
    if not obj or obj.get("quaildef") != "actordef":
        return

    props = obj.quail_actordef

    for child in list(obj.children):
        child.parent = None

    for action in props.actions:
        for lod in action.lods:
            if lod.sprite:
                lod.sprite.parent = obj

def update_numactions(self, context):
    actions = self.actions

    if len(actions) < self.numactions:
        for _ in range(self.numactions - len(actions)):
            act = actions.add()

            act.numlods = 0
            act.numlods = 1

    elif len(actions) > self.numactions:
        for _ in range(len(actions) - self.numactions):
            actions.remove(len(actions) - 1)


def update_numlods(self, context):
    lods = self.lods

    if len(lods) < self.numlods:
        for _ in range(self.numlods - len(lods)):
            lods.add()
    elif len(lods) > self.numlods:
        for _ in range(len(lods) - self.numlods):
            lods.remove(len(lods) - 1)

class QuailLODProperties(bpy.types.PropertyGroup):
    sprite: PointerProperty(
        name="Sprite",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.get("quaildef") in {
            "hierarchicalspritedef",
            "dmspritedef2",
            "dmspritedefinition",
            "sprite3ddef"
        },
        update=update_lod_sprite
    )

    mindistance: FloatProperty(
        name="Min Distance",
        default=1.0e30
    )

class QuailActionProperties(bpy.types.PropertyGroup):
    unk1: BoolProperty(
        name="Unknown 1",
        default=False
    )

    numlods: IntProperty(
        name="Num Levels of Detail",
        default=1,
        min=1,
        update=update_numlods
    )

    lods: bpy.props.CollectionProperty(type=QuailLODProperties)

# Define Actor properties
class QuailActorDefProperties(bpy.types.PropertyGroup):

    callback: StringProperty(name="Callback", default="")
    boundsref: IntProperty(name="BoundsRef", default=0)

    # -------------------------
    # Current Action (optional)
    # -------------------------
    has_currentaction: BoolProperty(name="Has Current Action", default=False)

    currentaction: IntProperty(
        name="Current Action",
        default=0
    )

    # -------------------------
    # Location (optional)
    # -------------------------
    has_location: BoolProperty(name="Has Location", default=False)

    loc_x: FloatProperty(name="X", default=0.0)
    loc_y: FloatProperty(name="Y", default=0.0)
    loc_z: FloatProperty(name="Z", default=0.0)

    rot_x: FloatProperty(name="Rot X", default=0.0)
    rot_y: FloatProperty(name="Rot Y", default=0.0)
    rot_z: FloatProperty(name="Rot Z", default=0.0)

    # -------------------------
    # Active Geometry (flag)
    # -------------------------
    activegeometry: BoolProperty(
        name="Active Geometry",
        default=False
    )

    # -------------------------
    # Actions
    # -------------------------
    numactions: IntProperty(
        name="Num Actions",
        default=1,
        min=1,
        update=update_numactions
    )

    actions: bpy.props.CollectionProperty(type=QuailActionProperties)

    # -------------------------
    collider: BoolProperty(
        name="Sprite Volume Only",
        default=False
    )

    userdata: StringProperty(name="User Data", default="")

class OBJECT_OT_add_quail_actordef(bpy.types.Operator):
    """Create a new ActorDef"""
    bl_idname = "object.add_custom_actor"
    bl_label = "ActorDef"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Create an Empty
        obj = bpy.data.objects.new("Actor", None)

        # Set transformation
        obj.location = context.scene.cursor.location

        obj.empty_display_type = 'SINGLE_ARROW'

        # Add custom property to identify this as an actor
        obj['quaildef'] = 'actordef'


        # Link to collection
        context.collection.objects.link(obj)

        # Set active object
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        return {'FINISHED'}

# Panel to display actor properties
class PROPERTIES_PT_quail_actordef(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"  # This puts it in the Object Properties panel
    bl_label = "ACTORDEF"
    # bl_options = {'DEFAULT_CLOSED'}
    bl_order = -100

    @classmethod
    def poll(cls, context):
        # Only show this panel when an actor is selected
        return context.object and context.object.get('quaildef') == 'actordef'

    def draw(self, context):
        pass

def draw_actordef_in_transform(self, context):
    obj = context.object
    if not obj or obj.get('quaildef') != 'actordef':
        return

    props = obj.quail_actordef
    layout = self.layout

    box = layout.box()
    box.label(text="ACTORDEF")

    # Basic
    box.prop(props, "callback")
    box.prop(props, "boundsref")

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
    # Active Geometry
    # -------------------------
    box.prop(props, "activegeometry")

    # -------------------------
    # Actions
    # -------------------------
    box.prop(props, "numactions")

    for i, action in enumerate(props.actions):
        action_box = box.box()
        action_box.label(text=f"Action {i+1}")

        action_box.prop(action, "unk1")
        action_box.prop(action, "numlods")

        for j, lod in enumerate(action.lods):
            lod_box = action_box.box()
            lod_box.label(text=f"LOD {j+1}")

            lod_box.prop(lod, "sprite")
            lod_box.prop(lod, "mindistance")

    # -------------------------
    box.prop(props, "collider")
    box.prop(props, "userdata")

# Register classes
def register():
    # ignored, auto_load bpy.utils.register_class(QuailActorDefProperties)
    # ignored, auto_load bpy.utils.register_class(OBJECT_OT_add_custom_empty)
    # ignored, auto_load bpy.utils.register_class(VIEW3D_MT_quail_add)
    # ignored, auto_load bpy.utils.register_class(PROPERTIES_PT_quail_actor)
    bpy.types.Object.quail_actordef = PointerProperty(type=QuailActorDefProperties)
    bpy.types.OBJECT_PT_transform.prepend(draw_actordef_in_transform)

def unregister():
    del bpy.types.Object.quail_actordef
    bpy.types.OBJECT_PT_transform.remove(draw_actordef_in_transform)
    # ignored, auto_load bpy.utils.unregister_class(PROPERTIES_PT_quail_actor)
    # ignored, auto_load bpy.utils.unregister_class(VIEW3D_MT_quail_add)
    # ignored, auto_load bpy.utils.unregister_class(OBJECT_OT_add_custom_empty)
    # ignored, auto_load bpy.utils.unregister_class(QuailActorDefProperties)