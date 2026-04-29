# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import FloatProperty, BoolProperty, IntProperty, StringProperty, CollectionProperty, PointerProperty

class QUAIL_OT_select_none_regions(bpy.types.Operator):
    bl_idname = "quail.select_none_regions"
    bl_label = "Select None"

    def execute(self, context):
        props = context.object.quail_region
        for vis in props.vislists:
            for item in vis.visible_regions:
                item.selected = False
        return {'FINISHED'}

class QUAIL_OT_select_all_regions(bpy.types.Operator):
    bl_idname = "quail.select_all_regions"
    bl_label = "Select All"

    def execute(self, context):
        props = context.object.quail_region
        for vis in props.vislists:
            for item in vis.visible_regions:
                item.selected = True
        return {'FINISHED'}

class QUAIL_OT_select_visible_regions(bpy.types.Operator):
    bl_idname = "quail.select_visible_regions"
    bl_label = "Select Visible Regions"

    def execute(self, context):
        obj = context.object
        props = obj.quail_region

        # Deselect everything first
        for o in context.view_layer.objects:
            o.select_set(False)

        for vis in props.vislists:
            for item in vis.visible_regions:
                if item.selected and item.region:
                    item.region.select_set(True)

        return {'FINISHED'}

class QUAIL_UL_region_visible(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):

        row = layout.row(align=True)

        if item.region:
            row.prop(item, "selected", text="")
            row.label(text=item.region.name, icon='OBJECT_DATA')
        else:
            row.label(text="(None)")

class QuailRegionVisibleItem(bpy.types.PropertyGroup):
    region: PointerProperty(
        name="Region",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.get("quaildef") == "region"
    )

    selected: BoolProperty(default=False)

# ------------------------------------------------
# VISLIST ITEM
# ------------------------------------------------
class QuailRegionVisList(bpy.types.PropertyGroup):
    range: StringProperty(name="Range", default="")

    visible_regions: CollectionProperty(type=QuailRegionVisibleItem)
    selected_index: IntProperty(default=0)

# ------------------------------------------------
# VISNODE ITEM
# ------------------------------------------------
class QuailRegionVisNode(bpy.types.PropertyGroup):
    normal_x: FloatProperty(name="X", default=0.0)
    normal_y: FloatProperty(name="Y", default=0.0)
    normal_z: FloatProperty(name="Z", default=0.0)
    normal_w: FloatProperty(name="W", default=0.0)

    vislistindex: IntProperty(name="VisList Index", default=0)
    fronttree: IntProperty(name="Front Tree", default=0)
    backtree: IntProperty(name="Back Tree", default=0)


# ------------------------------------------------
# MAIN REGION PROPERTIES
# ------------------------------------------------
class QuailRegionProperties(bpy.types.PropertyGroup):

    # -------------------------
    # Sphere (optional)
    # -------------------------
    has_sphere: BoolProperty(name="Has Sphere", default=False)

    sphere_x: FloatProperty(name="X", default=0.0)
    sphere_y: FloatProperty(name="Y", default=0.0)
    sphere_z: FloatProperty(name="Z", default=0.0)
    sphere_r: FloatProperty(name="Radius", default=0.0)

    # -------------------------
    # Reverb (optional)
    # -------------------------
    has_reverbvolume: BoolProperty(name="Has Reverb Volume", default=False)
    reverbvolume: FloatProperty(name="Reverb Volume", default=0.0)

    has_reverboffset: BoolProperty(name="Has Reverb Offset", default=False)
    reverboffset: IntProperty(name="Reverb Offset", default=0)

    # -------------------------
    # Flags
    # -------------------------
    regionfog: BoolProperty(name="Region Fog", default=False)
    gouraud2: BoolProperty(name="Gouraud 2", default=False)
    encodedvisibility: BoolProperty(name="Encoded Visibility", default=False)
    vislistbytes: BoolProperty(name="VisList Bytes (RLE)", default=True)

    # -------------------------
    # Sprite (optional)
    # -------------------------
    has_sprite: BoolProperty(name="Has Sprite", default=False)
    sprite: StringProperty(name="Sprite", default="")

    # -------------------------
    userdata: StringProperty(name="User Data", default="")

    # -------------------------
    # Collections
    # -------------------------
    vislists: CollectionProperty(type=QuailRegionVisList)
    visnodes: CollectionProperty(type=QuailRegionVisNode)


# ------------------------------------------------
# DRAW UI
# ------------------------------------------------
def draw_region_in_transform(self, context):
    obj = context.object
    if not obj or obj.get("quaildef") != "region":
        return

    props = obj.quail_region
    layout = self.layout

    box = layout.box()
    box.label(text="REGION")

    # -------------------------
    # Sphere
    # -------------------------
    box.prop(props, "has_sphere")
    if props.has_sphere:
        col = box.column(align=True)
        col.prop(props, "sphere_x")
        col.prop(props, "sphere_y")
        col.prop(props, "sphere_z")
        col.prop(props, "sphere_r")

    # -------------------------
    # Reverb
    # -------------------------
    box.prop(props, "has_reverbvolume")
    if props.has_reverbvolume:
        box.prop(props, "reverbvolume")

    box.prop(props, "has_reverboffset")
    if props.has_reverboffset:
        box.prop(props, "reverboffset")

    # -------------------------
    # Flags
    # -------------------------
    col = box.column(align=True)
    col.label(text="Flags")
    col.prop(props, "regionfog")
    col.prop(props, "gouraud2")
    col.prop(props, "encodedvisibility")
    col.prop(props, "vislistbytes")

    # -------------------------
    # Sprite
    # -------------------------
    box.prop(props, "has_sprite")
    if props.has_sprite:
        box.prop(props, "sprite")

    # -------------------------
    box.prop(props, "userdata")

    # -------------------------
    # VISNODES
    # -------------------------
    box.label(text="VisNodes")
    for i, node in enumerate(props.visnodes):
        nbox = box.box()
        nbox.label(text=f"Node {i}")

        row = nbox.row(align=True)
        row.prop(node, "normal_x")
        row.prop(node, "normal_y")
        row.prop(node, "normal_z")
        row.prop(node, "normal_w")

        nbox.prop(node, "vislistindex")
        nbox.prop(node, "fronttree")
        nbox.prop(node, "backtree")

    # -------------------------
    # VISLISTS
    # -------------------------
    box.label(text="Visible Regions")

    for i, vis in enumerate(props.vislists):

        vbox = box.box()
        vbox.label(text=f"VisList {i}")

        row = vbox.row()
        row.template_list(
            "QUAIL_UL_region_visible",
            "",
            vis,
            "visible_regions",
            vis,
            "selected_index"
        )

        row = vbox.row(align=True)
        row.operator("quail.select_visible_regions", text="Select Checked")

        row = vbox.row(align=True)
        row.operator("quail.select_all_regions", text="All")
        row.operator("quail.select_none_regions", text="None")


# ------------------------------------------------
# REGISTER
# ------------------------------------------------
def register():
    bpy.types.Object.quail_region = PointerProperty(type=QuailRegionProperties)
    bpy.types.OBJECT_PT_transform.prepend(draw_region_in_transform)


def unregister():
    del bpy.types.Object.quail_region
    bpy.types.OBJECT_PT_transform.remove(draw_region_in_transform)