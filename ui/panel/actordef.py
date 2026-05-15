# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty
from ...common.s3dobject import collect_sprite_graph


# ------------------------------------------------
# Update: LOD Sprite (collection-based)
# ------------------------------------------------
def update_lod_sprite(self, context):

    col = context.collection
    if not col or col.get("quaildef") != "actordef":
        return

    props = col.quail_actordef

    # ----------------------------------------
    # First: remove ALL existing sprite graph objects from this collection
    # ----------------------------------------
    to_remove = set()

    for obj in list(col.objects):
        if obj.get("quaildef") in {
            "hierarchicalspritedef",
            "dmspritedef2",
            "dmspritedefinition",
            "sprite3ddef"
        }:
            to_remove.update(collect_sprite_graph(obj))

    for obj in to_remove:
        if col in obj.users_collection:
            col.objects.unlink(obj)

    # ----------------------------------------
    # Then: add all graphs from current LOD selection
    # ----------------------------------------
    for action in props.actions:
        for lod in action.lods:
            sprite = lod.sprite

            if not sprite:
                continue

            graph = collect_sprite_graph(sprite)

            for obj in graph:

                # Remove from non-actordef collections
                for c in list(obj.users_collection):
                    if c.get("quaildef") != "actordef":
                        c.objects.unlink(obj)

                # Ensure in THIS collection
                if col not in obj.users_collection:
                    col.objects.link(obj)

# ------------------------------------------------
# Update counts
# ------------------------------------------------
def update_numactions(self, context):
    actions = self.actions

    if len(actions) < self.numactions:
        for _ in range(self.numactions - len(actions)):
            act = actions.add()
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


# ------------------------------------------------
# Properties
# ------------------------------------------------
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

    unk1: BoolProperty(name="Unknown 1", default=False)

    numlods: IntProperty(
        name="Num Levels of Detail",
        default=1,
        min=1,
        update=update_numlods
    )

    lods: bpy.props.CollectionProperty(type=QuailLODProperties)


class QuailActorDefProperties(bpy.types.PropertyGroup):

    callback: StringProperty(name="Callback", default="")
    boundsref: IntProperty(name="BoundsRef", default=0)

    # -------------------------
    # Current Action
    # -------------------------
    has_currentaction: BoolProperty(name="Has Current Action", default=False)
    currentaction: IntProperty(name="Current Action", default=0)

    # -------------------------
    # Location (stored only)
    # -------------------------
    has_location: BoolProperty(name="Has Location", default=False)

    loc_x: FloatProperty(name="X", default=0.0)
    loc_y: FloatProperty(name="Y", default=0.0)
    loc_z: FloatProperty(name="Z", default=0.0)

    rot_x: FloatProperty(name="Rot X", default=0.0)
    rot_y: FloatProperty(name="Rot Y", default=0.0)
    rot_z: FloatProperty(name="Rot Z", default=0.0)

    # -------------------------
    activegeometry: BoolProperty(name="Active Geometry", default=False)

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
    collider: BoolProperty(name="Sprite Volume Only", default=False)
    userdata: StringProperty(name="User Data", default="")


# ------------------------------------------------
# Operator: Create ActorDef (Collection)
# ------------------------------------------------
class OBJECT_OT_add_quail_actordef(bpy.types.Operator):
    bl_idname = "object.add_quail_actordef"
    bl_label = "ActorDef"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        col = bpy.data.collections.new("ActorDef")
        col["quaildef"] = "actordef"

        context.collection.children.link(col)

        return {'FINISHED'}


# ------------------------------------------------
# UI Panel (Collection context)
# ------------------------------------------------
class PROPERTIES_PT_quail_actordef(bpy.types.Panel):
    bl_label = "ACTORDEF"
    bl_idname = "PROPERTIES_PT_quail_actordef"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "collection"

    def draw(self, context):

        col = context.collection

        if not col or col.get("quaildef") != "actordef":
            return

        props = col.quail_actordef
        layout = self.layout

        box = layout.box()

        # Basic
        box.prop(props, "callback")
        box.prop(props, "boundsref")

        # Current Action
        box.prop(props, "has_currentaction")
        if props.has_currentaction:
            box.prop(props, "currentaction")

        # Location (data only)
        box.prop(props, "has_location")
        if props.has_location:
            col_ui = box.column(align=True)

            col_ui.label(text="Position")
            row = col_ui.row(align=True)
            row.prop(props, "loc_x")
            row.prop(props, "loc_y")
            row.prop(props, "loc_z")

            col_ui.label(text="Rotation")
            row = col_ui.row(align=True)
            row.prop(props, "rot_x")
            row.prop(props, "rot_y")
            row.prop(props, "rot_z")

        # Active Geometry
        box.prop(props, "activegeometry")

        # Actions
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

        # Misc
        box.prop(props, "collider")
        box.prop(props, "userdata")


def register():

    bpy.types.Collection.quail_actordef = PointerProperty(type=QuailActorDefProperties)


def unregister():

    del bpy.types.Collection.quail_actordef