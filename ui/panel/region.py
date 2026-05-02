# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import FloatProperty, BoolProperty, IntProperty, StringProperty, CollectionProperty, PointerProperty
from ...common.region import encode_vislist

def update_region_sphere(self, context):
    obj = context.object

    if not obj or obj.get("quaildef") != "region":
        return

    props = obj.quail_region

    if not props.has_sphere:
        return

    # Update position
    obj.location = (
        props.sphere_x,
        props.sphere_y,
        props.sphere_z
    )

    # Update radius (visual size)
    obj.empty_display_size = props.sphere_r

def rebuild_vislist_range(obj):
    props = obj.quail_region

    for vis in props.vislists:
        indices = []

        # collect indices from region names
        for item in vis.visible_regions:
            name = item.region_name
            if not name:
                continue
            if name.startswith("R"):
                try:
                    idx = int(name[1:])
                    indices.append(idx)
                except:
                    pass

        indices = sorted(set(indices))

        # encode
        if props.vislistbytes:
            data = encode_vislist(indices)
        else:
            data = []
            for rid in indices:
                idx0 = rid - 1
                data.append(idx0 & 0xFF)
                data.append((idx0 >> 8) & 0xFF)

        # rebuild RANGE string (with count)
        full = [len(data)] + data
        vis.range = " ".join(str(x) for x in full)

class QUAIL_OT_remove_selected_from_vislist(bpy.types.Operator):
    bl_idname = "quail.remove_selected_from_vislist"
    bl_label = "Remove Selected Regions"

    def execute(self, context):
        obj = context.object
        props = obj.quail_region

        vis = props.vislists[0]

        selected_set = set(context.selected_objects)

        i = 0
        while i < len(vis.visible_regions):
            item = vis.visible_regions[i]
            obj = bpy.data.objects.get(item.region_name)
            if obj in selected_set:
                vis.visible_regions.remove(i)
            else:
                i += 1

        rebuild_vislist_range(obj)

        return {'FINISHED'}

class QUAIL_OT_add_selected_to_vislist(bpy.types.Operator):
    bl_idname = "quail.add_selected_to_vislist"
    bl_label = "Add Selected Regions"

    def execute(self, context):
        obj = context.object
        props = obj.quail_region

        vis = props.vislists[0]

        existing = {item.region_name for item in vis.visible_regions}

        for o in context.selected_objects:
            if o.get("quaildef") != "region":
                continue

            if o.name not in existing:
                item = vis.visible_regions.add()
                item.region_name = o.name

        rebuild_vislist_range(obj)

        return {'FINISHED'}

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
                if item.selected:
                    obj = bpy.data.objects.get(item.region_name)
                    if obj:
                        obj.select_set(True)

        return {'FINISHED'}

class QUAIL_UL_region_visible(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_propname, index):

        row = layout.row(align=True)

        obj = bpy.data.objects.get(item.region_name)

        if obj:
            row.prop(item, "selected", text="")
            row.label(text=obj.name, icon='OBJECT_DATA')
        else:
            row.label(text="(None)")

class QuailRegionVisibleItem(bpy.types.PropertyGroup):
    # region: PointerProperty(
    #     name="Region",
    #     type=bpy.types.Object,
    #     poll=lambda self, obj: obj.get("quaildef") == "region"
    # )
    region_name: StringProperty()

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
    has_sphere: BoolProperty(name="Sphere", default=False)

    sphere_x: FloatProperty(name="X", default=0.0, update=update_region_sphere)
    sphere_y: FloatProperty(name="Y", default=0.0, update=update_region_sphere)
    sphere_z: FloatProperty(name="Z", default=0.0, update=update_region_sphere)
    sphere_r: FloatProperty(name="Radius", default=0.0, update=update_region_sphere)

    # -------------------------
    # Reverb (optional)
    # -------------------------
    has_reverbvolume: BoolProperty(name="Reverb Volume", default=False)
    reverbvolume: FloatProperty(default=0.0)

    has_reverboffset: BoolProperty(name="Reverb Offset", default=False)
    reverboffset: IntProperty(default=0)

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
    has_sprite: BoolProperty(name="Sprite", default=False)
    sprite: StringProperty(default="")

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

        row = vbox.row(align=True)
        row.operator("quail.add_selected_to_vislist", text="Add Selected")
        row.operator("quail.remove_selected_from_vislist", text="Remove Selected")

# ------------------------------------------------
# REGISTER
# ------------------------------------------------
def register():
    bpy.types.Object.quail_region = PointerProperty(type=QuailRegionProperties)
    bpy.types.OBJECT_PT_transform.prepend(draw_region_in_transform)


def unregister():
    del bpy.types.Object.quail_region
    bpy.types.OBJECT_PT_transform.remove(draw_region_in_transform)