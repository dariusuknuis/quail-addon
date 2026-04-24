# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty, CollectionProperty
from ...common import state
from ...common.armature import attach_object_to_dag

def update_polyhedron(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "hierarchicalspritedef":
        return

    arm = obj

    # ----------------------------------------
    # Remove ALL polyhedrondefinition children
    # ----------------------------------------
    for child in list(arm.children):
        if child.get("quaildef") == "polyhedrondefinition":
            child.parent = None

    # ----------------------------------------
    # Assign new polyhedron (if any)
    # ----------------------------------------
    new_obj = self.polyhedron

    if not new_obj:
        return

    new_obj.parent = arm

def update_bounding_radius(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "hierarchicalspritedef":
        return

    empty_name = f"{obj.name}_BOUNDINGRADIUS"
    empty = bpy.data.objects.get(empty_name)

    if not empty:
        return

    if self.has_boundingradius:
        empty.empty_display_size = self.boundingradius
    else:
        # Default fallback
        empty.empty_display_size = 1.0

def update_centeroffset(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "hierarchicalspritedef":
        return

    arm = obj

    if self.has_centeroffset:
        arm.location[0] = self.center_x
        arm.location[1] = self.center_y
        arm.location[2] = self.center_z
    else:
        arm.location[0] = 0.0
        arm.location[1] = 0.0
        arm.location[2] = 0.0

def update_dag_sprite(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.get("quaildef") != "hierarchicalspritedef":
        return

    arm = obj
    dag_tag = self.tag

    # ----------------------------------------
    # Initialize previous sprite if missing
    # ----------------------------------------
    if "_prev_sprite_name" not in self:
        for obj_child in bpy.data.objects:
            if obj_child.get("quaildef") in {"dmspritedef2", "dmspritedefinition"}:
                for c in obj_child.constraints:
                    if (
                        c.type == 'CHILD_OF' and
                        c.target == arm and
                        c.subtarget == dag_tag
                    ):
                        self["_prev_sprite_name"] = obj_child.name
                        break

    # ----------------------------------------
    # Remove previous object from THIS DAG only
    # ----------------------------------------
    prev_obj = None

    if self.spritetag:
        prev_obj = self.spritetag
    else:
        prev_name = self.get("_prev_sprite_name")
        if prev_name:
            prev_obj = bpy.data.objects.get(prev_name)

    if prev_obj:
        for c in list(prev_obj.constraints):
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

    bpy.context.view_layer.update()

    bpy.context.view_layer.objects.active = new_obj
    bpy.ops.object.select_all(action='DESELECT')
    new_obj.select_set(True)

    # Store for next time
    self["_prev_sprite_name"] = new_obj.name

def update_dag_tag(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = context.object
    if not obj or obj.type != 'ARMATURE':
        return

    arm_obj = obj
    arm = arm_obj.data
    props = arm_obj.quail_hierarchicalspritedef

    new_name = self.tag

    # ----------------------------------------
    # Find THIS dag's index
    # ----------------------------------------
    dag_index = None
    for i, dag in enumerate(props.dags):
        if dag == self:
            dag_index = i
            break

    if dag_index is None:
        return

    # ----------------------------------------
    # Get the bone by index (NOT name)
    # ----------------------------------------
    if dag_index >= len(arm.bones):
        return

    bone = arm.bones[dag_index]

    old_name = bone.name

    if old_name == new_name:
        return

    # ----------------------------------------
    # Rename
    # ----------------------------------------
    bone.name = new_name

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
        name="DAG Index"
    )
class QuailDAGProperties(bpy.types.PropertyGroup):
    tag: StringProperty(name="Tag", update=lambda self, context: update_dag_tag(self, context))
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

    dags: CollectionProperty(type=QuailDAGProperties)
    selected_dag_index: IntProperty(name="DAG Index", default=0, min=0)

    haveattachedskins: BoolProperty(name="Attached Skins", default=False)
    numattachedskins: IntProperty(
        name="Num Attached Skins",
        default=0,
        min=0,
        update=update_numattachedskins
    )
    attachedskins: CollectionProperty(type=QuailAttachedSkinProperties)

    polyhedron: PointerProperty(
        name="Polyhedron",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.get("quaildef") == "polyhedrondefinition",
        update=update_polyhedron
    )

    has_centeroffset: BoolProperty(name="Center Offset", default=False, update=update_centeroffset)
    center_x: FloatProperty(name="X", default=0.0, update=update_centeroffset)
    center_y: FloatProperty(name="Y", default=0.0, update=update_centeroffset)
    center_z: FloatProperty(name="Z", default=0.0, update=update_centeroffset)

    has_boundingradius: BoolProperty(
        name="Bounding Radius",
        default=False,
        update=update_bounding_radius
    )
    boundingradius: FloatProperty(
        name="Radius",
        default=1.0,
        update=update_bounding_radius
    )

    # Flags
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

            row.label(text=str(sub.dag_index))

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
    # OTHER PROPERTIES
    # -------------------------
    box.prop(props, "polyhedron")

    box.prop(props, "has_centeroffset")
    if props.has_centeroffset:
        row = box.row(align=True)
        row.prop(props, "center_x")
        row.prop(props, "center_y")
        row.prop(props, "center_z")

    box.prop(props, "has_boundingradius")
    if props.has_boundingradius:
        row = box.row(align=True)
        row.prop(props, "boundingradius")

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