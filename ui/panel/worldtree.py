# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import mathutils, bpy
from bpy.props import FloatProperty, BoolProperty, IntProperty, StringProperty, CollectionProperty, PointerProperty
from ...common.bsp import rotation_from_normal

def update_worldnode(self, context):

    obj = self.object
    if not obj:
        return

    normal = mathutils.Vector((
        self.normal_x,
        self.normal_y,
        self.normal_z
    )).normalized()

    d = self.normal_w

    # update position
    obj.location = -d * normal

    # update rotation
    obj.rotation_euler = rotation_from_normal(normal)

class QuailWorldTreeNode(bpy.types.PropertyGroup):

    object: PointerProperty(type=bpy.types.Object)

    normal_x: FloatProperty(name="X")
    normal_y: FloatProperty(name="Y")
    normal_z: FloatProperty(name="Z")
    normal_w: FloatProperty(name="W")

    region_tag: StringProperty(name="Region Tag")

    front_tree: IntProperty(name="Front Tree")
    back_tree: IntProperty(name="Back Tree")


class QuailWorldTreeProperties(bpy.types.PropertyGroup):
    nodes: CollectionProperty(type=QuailWorldTreeNode)
    selected_index: IntProperty(default=0)

def register():

    bpy.types.Object.quail_worldtree = PointerProperty(
        type=QuailWorldTreeProperties
    )


def unregister():

    del bpy.types.Object.quail_worldtree