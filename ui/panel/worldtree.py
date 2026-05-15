# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import mathutils, bpy
from bpy.props import FloatProperty, IntProperty, StringProperty, PointerProperty
from ...common.bsp import rotation_from_normal


# ----------------------------------------
# Update (runs when values change in UI)
# ----------------------------------------
def update_worldnode(self, context):

    obj = self.id_data  # <-- THIS is the object now
    if not obj:
        return

    normal = mathutils.Vector((
        self.normal_x,
        self.normal_y,
        self.normal_z
    ))

    if normal.length == 0:
        return

    normal.normalize()
    d = self.normal_w

    # Update position
    obj.location = -d * normal

    # Update rotation
    obj.rotation_euler = rotation_from_normal(normal)


# ----------------------------------------
# Per-node properties (ON OBJECT)
# ----------------------------------------
class QuailWorldNodeProperties(bpy.types.PropertyGroup):

    normal_x: FloatProperty(name="X", update=update_worldnode)
    normal_y: FloatProperty(name="Y", update=update_worldnode)
    normal_z: FloatProperty(name="Z", update=update_worldnode)
    normal_w: FloatProperty(name="W", update=update_worldnode)

    region_tag: StringProperty(name="Region Tag")

    front_tree: IntProperty(name="Front Tree")
    back_tree: IntProperty(name="Back Tree")


# ----------------------------------------
# UI Panel (per object)
# ----------------------------------------
def draw_worldnode_in_transform(self, context):
    obj = context.object

    if not obj or obj.get("quaildef") != "worldnode":
        return

    props = obj.quail_worldnode
    layout = self.layout

    box = layout.box()
    box.label(text="WORLDNODE")

    col = box.column(align=True)

    col.label(text="Normal")
    row = col.row(align=True)
    row.prop(props, "normal_x")
    row.prop(props, "normal_y")
    row.prop(props, "normal_z")
    row.prop(props, "normal_w")

    col.prop(props, "region_tag")

    row = col.row(align=True)
    row.prop(props, "front_tree")
    row.prop(props, "back_tree")


# ----------------------------------------
# Register
# ----------------------------------------
def register():

    bpy.types.Object.quail_worldnode = PointerProperty(
        type=QuailWorldNodeProperties
    )

    bpy.types.OBJECT_PT_transform.prepend(draw_worldnode_in_transform)


def unregister():

    del bpy.types.Object.quail_worldnode

    bpy.types.OBJECT_PT_transform.remove(draw_worldnode_in_transform)