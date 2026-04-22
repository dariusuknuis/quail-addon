# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty, CollectionProperty
from ...common import state
from ...common.armature import attach_object_to_dag

# =========================================================
# UPDATE HELPERS
# =========================================================

def update_dag_sprite(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "hierarchicalspritedef":
        return

    arm = obj
    props = obj.quail_hierarchicalspritedef

    dag_tag = self.tag

    # ----------------------------------------
    # Remove previous object from THIS DAG only
    # ----------------------------------------
    prev_name = self.get("_prev_sprite_name")

    if prev_name:
        prev_obj = bpy.data.objects.get(prev_name)

        if prev_obj:
            for c in prev_obj.constraints:
                if (
                    c.type == 'CHILD_OF' and
                    c.target == arm and
                    c.subtarget == dag_tag
                ):
                    prev_obj.constraints.remove(c)

    # ----------------------------------------
    # Assign new object
    # ----------------------------------------
    new_obj = self.spritetag

    if not new_obj:
        self["_prev_sprite_name"] = ""
        return

    attach_object_to_dag(new_obj, arm, dag_tag)

    # Prevent snapping (keep this)
    bpy.context.view_layer.update()

    bpy.context.view_layer.objects.active = new_obj
    bpy.ops.object.select_all(action='DESELECT')
    new_obj.select_set(True)

    # Store for cleanup next time
    self["_prev_sprite_name"] = new_obj.name

def update_dag_parenting(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "hierarchicalspritedef":
        return

    props = obj.quail_hierarchicalspritedef

    bpy.ops.object.mode_set(mode='EDIT')

    arm = obj.data

    # Clear all parenting first
    for bone in arm.edit_bones:
        bone.parent = None

    for i, dag in enumerate(props.dags):
        parent_bone = arm.edit_bones.get(dag.tag)
        if not parent_bone:
            continue

        for sub in dag.subdags:
            if sub.dag_index >= len(props.dags):
                continue

            child_dag = props.dags[sub.dag_index]
            child_bone = arm.edit_bones.get(child_dag.tag)

            if child_bone:
                child_bone.parent = parent_bone
                child_bone.use_connect = False

    bpy.ops.object.mode_set(mode='OBJECT')

def update_numattachedskins(self, context):
    skins = self.attachedskins

    if len(skins) < self.numattachedskins:
        for _ in range(self.numattachedskins - len(skins)):
            skins.add()
    elif len(skins) > self.numattachedskins:
        for _ in range(len(skins) - self.numattachedskins):
            skins.remove(len(skins) - 1)


def update_attachedskin_sprite(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "hierarchicalspritedef":
        return

    tag = obj.name

    prev_name = self.get("_prev_dmsprite_name")
    if prev_name:
        prev_obj = bpy.data.objects.get(prev_name)
        if prev_obj and prev_obj.get("hsprite") == tag:
            del prev_obj["hsprite"]
            if prev_obj.parent == obj:
                prev_obj.parent = None

    new_obj = self.dmsprite
    if new_obj:
        new_obj["hsprite"] = tag
        new_obj.parent = obj

        # store for next update
        self["_prev_dmsprite_name"] = new_obj.name
    else:
        self["_prev_dmsprite_name"] = ""


# =========================================================
# PROPERTY GROUPS
# =========================================================
class QuailSubDAGItem(bpy.types.PropertyGroup):
    dag_index: IntProperty(
        name="DAG Index",
        update=lambda self, context: update_dag_parenting(self, context)
    )
class QuailDAGProperties(bpy.types.PropertyGroup):
    tag: StringProperty(name="Tag")
    def sprite_poll(self, obj):
        return obj.get("quaildef") in {
            "dmspritedef2",
            "dmspritedefinition"
        }

    spritetag: PointerProperty(
        name="Sprite",
        type=bpy.types.Object,
        poll=sprite_poll,
        update=lambda self, context: update_dag_sprite(self, context)
    )
    track: StringProperty(name="Track")
    subdags: CollectionProperty(type=QuailSubDAGItem)


class QuailAttachedSkinProperties(bpy.types.PropertyGroup):
    dmsprite: PointerProperty(
        name="DMSprite",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.get("quaildef") in {
            "dmspritedef2",
            "dmspritedefinition"
        },
        update=update_attachedskin_sprite
    )

    linkdagindex: IntProperty(name="Link DAG Index", default=2)


class QuailHierarchicalSpriteProperties(bpy.types.PropertyGroup):

    # DAGs
    dags: CollectionProperty(type=QuailDAGProperties)
    selected_dag_index: IntProperty(name="DAG Index", default=0, min=0)

    # Attached skins
    haveattachedskins: BoolProperty(name="Attached Skins", default=False)

    numattachedskins: IntProperty(
        name="Num Attached Skins",
        default=0,
        min=0,
        update=update_numattachedskins
    )

    attachedskins: CollectionProperty(type=QuailAttachedSkinProperties)

    # Polyhedron
    polyhedron: PointerProperty(
        name="Polyhedron",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.get("quaildef") == "polyhedrondef"
    )

    # Center offset
    has_centeroffset: BoolProperty(name="Center Offset", default=False)
    center_x: FloatProperty(name="X", default=0.0)
    center_y: FloatProperty(name="Y", default=0.0)
    center_z: FloatProperty(name="Z", default=0.0)

    # Flags
    boundingradius: FloatProperty(name="Bounding Radius", default=0.0)
    dagcollisions: BoolProperty(name="DAG Collisions", default=False)


# =========================================================
# PANEL
# =========================================================

def draw_hierarchicalspritedef_in_transform(self, context):
    obj = context.object
    if not obj or obj.get('quaildef') != 'hierarchicalspritedef':
        return

    props = obj.quail_hierarchicalspritedef
    layout = self.layout

    box = layout.box()
    box.label(text="HIERARCHICALSPRITEDEF")

    # -------------------------
    # DAG SECTION
    # -------------------------
    box.label(text=f"Num DAGs: {len(props.dags)}")
    box.prop(props, "selected_dag_index")

    if props.dags and props.selected_dag_index < len(props.dags):
        dag = props.dags[props.selected_dag_index]

        dag_box = box.box()
        dag_box.label(text=f"DAG {props.selected_dag_index + 1}")

        dag_box.prop(dag, "tag")
        dag_box.prop(dag, "spritetag")
        dag_box.prop(dag, "track")

        dag_box.label(text="SubDAGs:")

        for sub in dag.subdags:
            row = dag_box.row(align=True)

            row.prop(sub, "dag_index", text="")

            if sub.dag_index < len(props.dags):
                row.label(text=props.dags[sub.dag_index].tag)
    # -------------------------
    # ATTACHED SKINS
    # -------------------------
    box.prop(props, "haveattachedskins")

    if props.haveattachedskins:
        box.prop(props, "numattachedskins")

        for i, skin in enumerate(props.attachedskins):
            skin_box = box.box()
            skin_box.label(text=f"Skin {i+1}")

            skin_box.prop(skin, "dmsprite")
            skin_box.prop(skin, "linkdagindex")

    # -------------------------
    # POLYHEDRON
    # -------------------------
    box.prop(props, "polyhedron")

    # -------------------------
    # CENTER OFFSET
    # -------------------------
    box.prop(props, "has_centeroffset")
    if props.has_centeroffset:
        row = box.row(align=True)
        row.prop(props, "center_x")
        row.prop(props, "center_y")
        row.prop(props, "center_z")

    # -------------------------
    # FLAGS
    # -------------------------
    box.prop(props, "boundingradius")
    box.prop(props, "dagcollisions")


# =========================================================
# REGISTER
# =========================================================

def register():

    bpy.types.Object.quail_hierarchicalspritedef = PointerProperty(type=QuailHierarchicalSpriteProperties)
    bpy.types.OBJECT_PT_transform.prepend(draw_hierarchicalspritedef_in_transform)

def unregister():
    del bpy.types.Object.quail_hierarchicalspritedef
    bpy.types.OBJECT_PT_transform.remove(draw_hierarchicalspritedef_in_transform)