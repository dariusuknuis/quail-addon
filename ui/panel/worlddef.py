# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
from bpy.props import BoolProperty, IntProperty, PointerProperty

class QuailWorldDefProperties(bpy.types.PropertyGroup):

    newworld: BoolProperty(
        name="New World",
        default=False
    )

    zone: BoolProperty(
        name="Zone",
        default=False
    )

    use_eqg: BoolProperty(
        name="EQG",
        default=False
    )

    eqgversion: IntProperty(
        name="EQG Version",
        default=0
    )

class QUAIL_PT_worlddef_collection(bpy.types.Panel):
    bl_label = "WORLDDEF"
    bl_idname = "QUAIL_PT_worlddef_collection"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "collection"

    def draw(self, context):
        layout = self.layout
        col = context.collection

        if not col or col.get("quaildef") != "worlddef":
            return

        props = col.quail_worlddef

        box = layout.box()
        box.label(text="WORLDDEF")

        box.prop(props, "newworld")
        box.prop(props, "zone")

        box.prop(props, "use_eqg")
        if props.use_eqg:
            box.prop(props, "eqgversion")


# =========================================================
# REGISTER
# =========================================================

def register():

    bpy.types.Collection.quail_worlddef = PointerProperty(
        type=QuailWorldDefProperties
    )

def unregister():

    del bpy.types.Collection.quail_worlddef
