# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import EnumProperty, BoolProperty, StringProperty, CollectionProperty, IntProperty, PointerProperty
from ...common.zone import apply_zone_rules

ZONE_TYPE_ITEMS = [
    ('DR', "Dry", ""),
    ('WT', "Water", ""),
    ('LA', "Lava", ""),
    ('SL', "Slime", ""),
    ('VW', "Velious Water", ""),
    ('W2', "Water v2", ""),
    ('W3', "Water v3", ""),
]

def update_zone_name(self, context):
    obj = context.object
    if not obj or obj.get("quaildef") != "zone":
        return

    apply_zone_rules(obj)

class QUAIL_OT_add_selected_to_zone_regions(bpy.types.Operator):
    bl_idname = "quail.add_selected_to_zone_regions"
    bl_label = "Add Selected Regions"

    def execute(self, context):
        obj = context.object
        props = obj.quail_zone

        existing = {item.region_name for item in props.regionlist}

        for o in context.selected_objects:
            if o.get("quaildef") != "region":
                continue

            if o.name not in existing:
                item = props.regionlist.add()
                item.region_name = o.name

        return {'FINISHED'}


class QUAIL_OT_remove_selected_from_zone_regions(bpy.types.Operator):
    bl_idname = "quail.remove_selected_from_zone_regions"
    bl_label = "Remove Selected Regions"

    def execute(self, context):
        obj = context.object
        props = obj.quail_zone

        selected_set = set(context.selected_objects)

        i = 0
        while i < len(props.regionlist):
            item = props.regionlist[i]
            region_obj = bpy.data.objects.get(item.region_name)

            if region_obj in selected_set or item.selected:
                props.regionlist.remove(i)
            else:
                i += 1

        return {'FINISHED'}


class QUAIL_OT_select_all_zone_regions(bpy.types.Operator):
    bl_idname = "quail.select_all_zone_regions"
    bl_label = "Select All"

    def execute(self, context):
        props = context.object.quail_zone

        for item in props.regionlist:
            item.selected = True

        return {'FINISHED'}


class QUAIL_OT_select_none_zone_regions(bpy.types.Operator):
    bl_idname = "quail.select_none_zone_regions"
    bl_label = "Select None"

    def execute(self, context):
        props = context.object.quail_zone

        for item in props.regionlist:
            item.selected = False

        return {'FINISHED'}


class QUAIL_OT_select_zone_regions(bpy.types.Operator):
    bl_idname = "quail.select_zone_regions"
    bl_label = "Select Checked Regions"

    def execute(self, context):
        obj = context.object
        props = obj.quail_zone

        for o in context.view_layer.objects:
            o.select_set(False)

        obj.select_set(True)
        context.view_layer.objects.active = obj

        for item in props.regionlist:
            if not item.selected:
                continue

            region_obj = bpy.data.objects.get(item.region_name)
            if region_obj:
                region_obj.select_set(True)

        return {'FINISHED'}


class QUAIL_UL_zone_regions(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):

        row = layout.row(align=True)

        region_obj = bpy.data.objects.get(item.region_name)

        if region_obj:
            row.prop(item, "selected", text="")
            row.label(text=region_obj.name, icon='EMPTY_AXIS')
        else:
            row.prop(item, "selected", text="")
            row.label(text=item.region_name if item.region_name else "(None)", icon='ERROR')

class QuailZoneRegionItem(bpy.types.PropertyGroup):
    region_name: StringProperty()
    selected: BoolProperty(default=False)

class QuailZoneProperties(bpy.types.PropertyGroup):

    zone_type: EnumProperty(
        name="Zone Type",
        items=ZONE_TYPE_ITEMS,
        default='DR'
    )

    is_pvp: BoolProperty(name="PvP", default=False)
    has_tp: BoolProperty(name="Teleport (TP)", default=False)
    slippery: BoolProperty(name="Slippery", default=False)

    userdata: StringProperty(name="User Data", default="")

    regionlist: CollectionProperty(type=QuailZoneRegionItem)
    regionlist_index: IntProperty(default=0)

def draw_zone_in_transform(self, context):

    obj = context.object
    if not obj or obj.get("quaildef") != "zone":
        return

    props = obj.quail_zone
    layout = self.layout

    box = layout.box()
    box.label(text="ZONE")

    # -------------------------
    # TYPE
    # -------------------------
    box.prop(props, "zone_type")

    # -------------------------
    # FLAGS
    # -------------------------
    col = box.column(align=True)
    col.prop(props, "is_pvp")
    col.prop(props, "has_tp")
    col.prop(props, "slippery")

    # -------------------------
    # USERDATA
    # -------------------------
    box.prop(props, "userdata")

    # -------------------------
    # REGION LIST
    # -------------------------
    box.label(text="Region List")

    row = box.row()
    row.template_list(
        "QUAIL_UL_zone_regions",
        "",
        props,
        "regionlist",
        props,
        "regionlist_index"
    )

    row = box.row(align=True)
    row.operator("quail.select_zone_regions", text="Select Checked")

    row = box.row(align=True)
    row.operator("quail.select_all_zone_regions", text="All")
    row.operator("quail.select_none_zone_regions", text="None")

    row = box.row(align=True)
    row.operator("quail.add_selected_to_zone_regions", text="Add Selected")
    row.operator("quail.remove_selected_from_zone_regions", text="Remove Selected")

def register():
    bpy.types.Object.quail_zone = PointerProperty(type=QuailZoneProperties)
    bpy.types.OBJECT_PT_transform.prepend(draw_zone_in_transform)


def unregister():
    del bpy.types.Object.quail_zone
    bpy.types.OBJECT_PT_transform.remove(draw_zone_in_transform)