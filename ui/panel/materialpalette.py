# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import StringProperty, PointerProperty, CollectionProperty, IntProperty
from ...common import state

def update_mesh_materials_from_palette(palette_obj):

    props = palette_obj.quail_materialpalette

    for obj in bpy.data.objects:

        if obj.type != 'MESH':
            continue

        if obj.get("quaildef") not in {"dmspritedef2", "dmspritedefinition"}:
            continue

        if not hasattr(obj, "quail_dmspritedef2"):
            continue

        if obj.quail_dmspritedef2.materialpalette != palette_obj:
            continue

        mesh = obj.data

        # ----------------------------------------
        # Rebuild material slots
        # ----------------------------------------
        materials = mesh.materials
        palette_mats = [item.material for item in props.materials if item.material]

        # Expand slots if needed
        while len(materials) < len(palette_mats):
            materials.append(None)

        # Assign in-place (preserves indices)
        for i, mat in enumerate(palette_mats):
            materials[i] = mat

        # Trim extra slots if palette shrank
        while len(materials) > len(palette_mats):
            materials.pop(index=len(materials) - 1)

# =========================================================
# PROPERTY GROUPS
# =========================================================

class QUAIL_UL_materialpalette_items(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon,
        active_data, active_propname, index
    ):
        # item is QuailMaterialPaletteItem
        layout.prop(item, "material", text="")

class QUAIL_OT_add_palette_material(bpy.types.Operator):
    bl_idname = "quail.add_palette_material"
    bl_label = "Add Material"

    def execute(self, context):
        obj = context.object
        props = obj.quail_materialpalette

        props.materials.add()
        props.selected_index = len(props.materials) - 1

        return {'FINISHED'}


class QUAIL_OT_remove_palette_material(bpy.types.Operator):
    bl_idname = "quail.remove_palette_material"
    bl_label = "Remove Material"

    def execute(self, context):
        obj = context.object
        props = obj.quail_materialpalette

        idx = props.selected_index

        if 0 <= idx < len(props.materials):
            props.materials.remove(idx)
            props.selected_index = max(0, idx - 1)

        return {'FINISHED'}

class QuailMaterialPaletteItem(bpy.types.PropertyGroup):

    def update_material(self, context):

        if state.QUAIL_UPDATING:
            return

        obj = context.object
        if not obj or obj.get("quaildef") != "materialpalette":
            return

        update_mesh_materials_from_palette(obj)

    material: PointerProperty(
        name="Material",
        type=bpy.types.Material,
        update=update_material
    )


class QuailMaterialPaletteProperties(bpy.types.PropertyGroup):
    tag: StringProperty(name="Tag")
    materials: CollectionProperty(type=QuailMaterialPaletteItem)
    selected_index: IntProperty(name="Index", default=0, min=0)


# =========================================================
# PANEL DRAW (MATCHES YOUR STYLE)
# =========================================================

def draw_materialpalette_in_transform(self, context):
    obj = context.object
    if not obj or obj.get("quaildef") != "materialpalette":
        return

    props = obj.quail_materialpalette
    layout = self.layout

    box = layout.box()
    box.label(text="MATERIALPALETTE")

    box.prop(props, "tag")

    box.label(text=f"Num Materials: {len(props.materials)}")

    row = box.row()

    row.template_list(
        "QUAIL_UL_materialpalette_items",
        "",
        props,
        "materials",
        props,
        "selected_index"
    )

    col = row.column(align=True)
    col.operator("quail.add_palette_material", icon='ADD', text="")
    col.operator("quail.remove_palette_material", icon='REMOVE', text="")


# =========================================================
# REGISTER
# =========================================================

def register():

    bpy.types.Object.quail_materialpalette = PointerProperty(type=QuailMaterialPaletteProperties)

    bpy.types.OBJECT_PT_transform.prepend(draw_materialpalette_in_transform)


def unregister():

    del bpy.types.Object.quail_materialpalette

    bpy.types.OBJECT_PT_transform.remove(draw_materialpalette_in_transform)