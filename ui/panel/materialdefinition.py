# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
import os
from bpy.props import StringProperty, FloatProperty, BoolProperty, PointerProperty, IntProperty, EnumProperty

# Define Actor properties


class QuailMaterialDefinitionProperties(bpy.types.PropertyGroup):
    rendermethod: EnumProperty(
        name="Render Method",
        description="Render Method",
        items=[
            ('TRANSPARENT', "TRANSPARENT", ""),
            ('WIREFRAME', "WIREFRAME", ""),
            ('WIREFRAMECONSTANTZEROINTENSITY',
             "WIREFRAMECONSTANTZEROINTENSITY", ""),
            ('WIREFRAMECONSTANT', "WIREFRAMECONSTANT", ""),
            ('WIREFRAMEAMBIENT', "WIREFRAMEAMBIENT", ""),
            ('WIREFRAMESCALEDAMBIENT', "WIREFRAMESCALEDAMBIENT", ""),
            ('SOLIDFILL', "SOLIDFILL", ""),
            ('SOLIDFILLZEROINTENSITY', "SOLIDFILLZEROINTENSITY", ""),
            ('SOLIDFILLCONSTANT', "SOLIDFILLCONSTANT", ""),
            ('SOLIDFILLAMBIENT', "SOLIDFILLAMBIENT", ""),
            ('SOLIDFILLSCALEDAMBIENT', "SOLIDFILLSCALEDAMBIENT", ""),
            ('SOLIDFILLGOURAUD1', "SOLIDFILLGOURAUD1", ""),
            ('SOLIDFILLGOURAUD2', "SOLIDFILLGOURAUD2", ""),
            ('SOLIDFILLCONSTANTGOURAUD1', "SOLIDFILLCONSTANTGOURAUD1", ""),
            ('SOLIDFILLCONSTANTGOURAUD2', "SOLIDFILLCONSTANTGOURAUD2", ""),
            ('SOLIDFILLAMBIENTGOURAUD1', "SOLIDFILLAMBIENTGOURAUD1", ""),
            ('SOLIDFILLAMBIENTGOURAUD2', "SOLIDFILLAMBIENTGOURAUD2", ""),
            ('SOLIDFILLSCALEDAMBIENTGOURAUD1',
             "SOLIDFILLSCALEDAMBIENTGOURAUD1", ""),
            ('SOLIDFILLSCALEDAMBIENTGOURAUD2',
             "SOLIDFILLSCALEDAMBIENTGOURAUD2", ""),
            ('TEXTURE1', "TEXTURE1", ""),
            ('TEXTURE1CONSTANT', "TEXTURE1CONSTANT", ""),
            ('TEXTURE1AMBIENT', "TEXTURE1AMBIENT", ""),
            ('TEXTURE1SCALEDAMBIENT', "TEXTURE1SCALEDAMBIENT", ""),
            ('TEXTURE1GOURAUD1', "TEXTURE1GOURAUD1", ""),
            ('TEXTURE1GOURAUD2', "TEXTURE1GOURAUD2", ""),
            ('TEXTURE1CONSTANTGOURAUD1', "TEXTURE1CONSTANTGOURAUD1", ""),
            ('TEXTURE1CONSTANTGOURAUD2', "TEXTURE1CONSTANTGOURAUD2", ""),
            ('TEXTURE1AMBIENTGOURAUD1', "TEXTURE1AMBIENTGOURAUD1", ""),
            ('TEXTURE1AMBIENTGOURAUD2', "TEXTURE1AMBIENTGOURAUD2", ""),
            ('TEXTURE1SCALEDAMBIENTGOURAUD1', "TEXTURE1SCALEDAMBIENTGOURAUD1", ""),
            ('TEXTURE1SCALEDAMBIENTGOURAUD2', "TEXTURE1SCALEDAMBIENTGOURAUD2", ""),
            ('TRANSTEXTURE1', "TRANSTEXTURE1", ""),
            ('TRANSTEXTURE1ZEROINTENSITY', "TRANSTEXTURE1ZEROINTENSITY", ""),
            ('TRANSTEXTURE1CONSTANT', "TRANSTEXTURE1CONSTANT", ""),
            ('TRANSTEXTURE1AMBIENT', "TRANSTEXTURE1AMBIENT", ""),
            ('TRANSTEXTURE1SCALEDAMBIENT', "TRANSTEXTURE1SCALEDAMBIENT", ""),
            ('TRANSTEXTURE1GOURAUD1', "TRANSTEXTURE1GOURAUD1", ""),
            ('TRANSTEXTURE1GOURAUD2', "TRANSTEXTURE1GOURAUD2", ""),
            ('TRANSTEXTURE1CONSTANTGOURAUD1', "TRANSTEXTURE1CONSTANTGOURAUD1", ""),
            ('TRANSTEXTURE1CONSTANTGOURAUD2', "TRANSTEXTURE1CONSTANTGOURAUD2", ""),
            ('TRANSTEXTURE1AMBIENTGOURAUD1', "TRANSTEXTURE1AMBIENTGOURAUD1", ""),
            ('TRANSTEXTURE1AMBIENTGOURAUD2', "TRANSTEXTURE1AMBIENTGOURAUD2", ""),
            ('TRANSTEXTURE1SCALEDAMBIENTGOURAUD1',
             "TRANSTEXTURE1SCALEDAMBIENTGOURAUD1", ""),
            ('TRANSTEXTURE1SCALEDAMBIENTGOURAUD2',
             "TRANSTEXTURE1SCALEDAMBIENTGOURAUD2", ""),
            ('TEXTURE2', "TEXTURE2", ""),
            ('TEXTURE2CONSTANT', "TEXTURE2CONSTANT", ""),
            ('TEXTURE2AMBIENT', "TEXTURE2AMBIENT", ""),
            ('TEXTURE2SCALEDAMBIENT', "TEXTURE2SCALEDAMBIENT", ""),
            ('TEXTURE2GOURAUD1', "TEXTURE2GOURAUD1", ""),
            ('TEXTURE2GOURAUD2', "TEXTURE2GOURAUD2", ""),
            ('TEXTURE2CONSTANTGOURAUD1', "TEXTURE2CONSTANTGOURAUD1", ""),
            ('TEXTURE2CONSTANTGOURAUD2', "TEXTURE2CONSTANTGOURAUD2", ""),
            ('TEXTURE2AMBIENTGOURAUD1', "TEXTURE2AMBIENTGOURAUD1", ""),
            ('TEXTURE2AMBIENTGOURAUD2', "TEXTURE2AMBIENTGOURAUD2", ""),
            ('TEXTURE2SCALEDAMBIENTGOURAUD1', "TEXTURE2SCALEDAMBIENTGOURAUD1", ""),
            ('TEXTURE2SCALEDAMBIENTGOURAUD2', "TEXTURE2SCALEDAMBIENTGOURAUD2", ""),
            ('TRANSTEXTURE2', "TRANSTEXTURE2", ""),
            ('TRANSTEXTURE2ZEROINTENSITY', "TRANSTEXTURE2ZEROINTENSITY", ""),
            ('TRANSTEXTURE2CONSTANT', "TRANSTEXTURE2CONSTANT", ""),
            ('TRANSTEXTURE2AMBIENT', "TRANSTEXTURE2AMBIENT", ""),
            ('TRANSTEXTURE2SCALEDAMBIENT', "TRANSTEXTURE2SCALEDAMBIENT", ""),
            ('TRANSTEXTURE2GOURAUD1', "TRANSTEXTURE2GOURAUD1", ""),
            ('TRANSTEXTURE2GOURAUD2', "TRANSTEXTURE2GOURAUD2", ""),
            ('TRANSTEXTURE2CONSTANTGOURAUD1', "TRANSTEXTURE2CONSTANTGOURAUD1", ""),
            ('TRANSTEXTURE2CONSTANTGOURAUD2', "TRANSTEXTURE2CONSTANTGOURAUD2", ""),
            ('TRANSTEXTURE2AMBIENTGOURAUD1', "TRANSTEXTURE2AMBIENTGOURAUD1", ""),
            ('TRANSTEXTURE2AMBIENTGOURAUD2', "TRANSTEXTURE2AMBIENTGOURAUD2", ""),
            ('TRANSTEXTURE2SCALEDAMBIENTGOURAUD1',
             "TRANSTEXTURE2SCALEDAMBIENTGOURAUD1", ""),
            ('TRANSTEXTURE2SCALEDAMBIENTGOURAUD2',
             "TRANSTEXTURE2SCALEDAMBIENTGOURAUD2", ""),
            ('TEXTURE3', "TEXTURE3", ""),
            ('TEXTURE3CONSTANT', "TEXTURE3CONSTANT", ""),
            ('TEXTURE3AMBIENT', "TEXTURE3AMBIENT", ""),
            ('TEXTURE3SCALEDAMBIENT', "TEXTURE3SCALEDAMBIENT", ""),
            ('TEXTURE3GOURAUD1', "TEXTURE3GOURAUD1", ""),
            ('TEXTURE3GOURAUD2', "TEXTURE3GOURAUD2", ""),
            ('TEXTURE3CONSTANTGOURAUD1', "TEXTURE3CONSTANTGOURAUD1", ""),
            ('TEXTURE3CONSTANTGOURAUD2', "TEXTURE3CONSTANTGOURAUD2", ""),
            ('TEXTURE3AMBIENTGOURAUD1', "TEXTURE3AMBIENTGOURAUD1", ""),
            ('TEXTURE3AMBIENTGOURAUD2', "TEXTURE3AMBIENTGOURAUD2", ""),
            ('TEXTURE3SCALEDAMBIENTGOURAUD1', "TEXTURE3SCALEDAMBIENTGOURAUD1", ""),
            ('TEXTURE3SCALEDAMBIENTGOURAUD2', "TEXTURE3SCALEDAMBIENTGOURAUD2", ""),
            ('TEXTURE4', "TEXTURE4", ""),
            ('TEXTURE4CONSTANT', "TEXTURE4CONSTANT", ""),
            ('TEXTURE4AMBIENT', "TEXTURE4AMBIENT", ""),
            ('TEXTURE4SCALEDAMBIENT', "TEXTURE4SCALEDAMBIENT", ""),
            ('TEXTURE4GOURAUD1', "TEXTURE4GOURAUD1", ""),
            ('TEXTURE4GOURAUD2', "TEXTURE4GOURAUD2", ""),
            ('TEXTURE4CONSTANTGOURAUD1', "TEXTURE4CONSTANTGOURAUD1", ""),
            ('TEXTURE4CONSTANTGOURAUD2', "TEXTURE4CONSTANTGOURAUD2", ""),
            ('TEXTURE4AMBIENTGOURAUD1', "TEXTURE4AMBIENTGOURAUD1", ""),
            ('TEXTURE4AMBIENTGOURAUD2', "TEXTURE4AMBIENTGOURAUD2", ""),
            ('TEXTURE4SCALEDAMBIENTGOURAUD1', "TEXTURE4SCALEDAMBIENTGOURAUD1", ""),
            ('TEXTURE4SCALEDAMBIENTGOURAUD2', "TEXTURE4SCALEDAMBIENTGOURAUD2", ""),
            ('TRANSTEXTURE4', "TRANSTEXTURE4", ""),
            ('TRANSTEXTURE4ZEROINTENSITY', "TRANSTEXTURE4ZEROINTENSITY", ""),
            ('TRANSTEXTURE4CONSTANT', "TRANSTEXTURE4CONSTANT", ""),
            ('TRANSTEXTURE4AMBIENT', "TRANSTEXTURE4AMBIENT", ""),
            ('TRANSTEXTURE4SCALEDAMBIENT', "TRANSTEXTURE4SCALEDAMBIENT", ""),
            ('TRANSTEXTURE4GOURAUD1', "TRANSTEXTURE4GOURAUD1", ""),
            ('TRANSTEXTURE4GOURAUD2', "TRANSTEXTURE4GOURAUD2", ""),
            ('TRANSTEXTURE4CONSTANTGOURAUD1', "TRANSTEXTURE4CONSTANTGOURAUD1", ""),
            ('TRANSTEXTURE4CONSTANTGOURAUD2', "TRANSTEXTURE4CONSTANTGOURAUD2", ""),
            ('TRANSTEXTURE4AMBIENTGOURAUD1', "TRANSTEXTURE4AMBIENTGOURAUD1", ""),
            ('TRANSTEXTURE4AMBIENTGOURAUD2', "TRANSTEXTURE4AMBIENTGOURAUD2", ""),
            ('TRANSTEXTURE4SCALEDAMBIENTGOURAUD1',
             "TRANSTEXTURE4SCALEDAMBIENTGOURAUD1", ""),
            ('TRANSTEXTURE4SCALEDAMBIENTGOURAUD2',
             "TRANSTEXTURE4SCALEDAMBIENTGOURAUD2", ""),
            ('TEXTURE5', "TEXTURE5", ""),
            ('TEXTURE5CONSTANT', "TEXTURE5CONSTANT", ""),
            ('TEXTURE5AMBIENT', "TEXTURE5AMBIENT", ""),
            ('TEXTURE5SCALEDAMBIENT', "TEXTURE5SCALEDAMBIENT", ""),
            ('TEXTURE5GOURAUD1', "TEXTURE5GOURAUD1", ""),
            ('TEXTURE5GOURAUD2', "TEXTURE5GOURAUD2", ""),
            ('TEXTURE5CONSTANTGOURAUD1', "TEXTURE5CONSTANTGOURAUD1", ""),
            ('TEXTURE5CONSTANTGOURAUD2', "TEXTURE5CONSTANTGOURAUD2", ""),
            ('TEXTURE5AMBIENTGOURAUD1', "TEXTURE5AMBIENTGOURAUD1", ""),
            ('TEXTURE5AMBIENTGOURAUD2', "TEXTURE5AMBIENTGOURAUD2", ""),
            ('TEXTURE5SCALEDAMBIENTGOURAUD1', "TEXTURE5SCALEDAMBIENTGOURAUD1", ""),
            ('TEXTURE5SCALEDAMBIENTGOURAUD2', "TEXTURE5SCALEDAMBIENTGOURAUD2", ""),
            ('TRANSTEXTURE5', "TRANSTEXTURE5", ""),
            ('TRANSTEXTURE5ZEROINTENSITY', "TRANSTEXTURE5ZEROINTENSITY", ""),
            ('TRANSTEXTURE5CONSTANT', "TRANSTEXTURE5CONSTANT", ""),
            ('TRANSTEXTURE5AMBIENT', "TRANSTEXTURE5AMBIENT", ""),
            ('TRANSTEXTURE5SCALEDAMBIENT', "TRANSTEXTURE5SCALEDAMBIENT", ""),
            ('TRANSTEXTURE5GOURAUD1', "TRANSTEXTURE5GOURAUD1", ""),
            ('TRANSTEXTURE5GOURAUD2', "TRANSTEXTURE5GOURAUD2", ""),
            ('TRANSTEXTURE5CONSTANTGOURAUD1', "TRANSTEXTURE5CONSTANTGOURAUD1", ""),
            ('TRANSTEXTURE5CONSTANTGOURAUD2', "TRANSTEXTURE5CONSTANTGOURAUD2", ""),
            ('TRANSTEXTURE5AMBIENTGOURAUD1', "TRANSTEXTURE5AMBIENTGOURAUD1", ""),
            ('TRANSTEXTURE5AMBIENTGOURAUD2', "TRANSTEXTURE5AMBIENTGOURAUD2", ""),
            ('TRANSTEXTURE5SCALEDAMBIENTGOURAUD1',
             "TRANSTEXTURE5SCALEDAMBIENTGOURAUD1", ""),
            ('TRANSTEXTURE5SCALEDAMBIENTGOURAUD2',
             "TRANSTEXTURE5SCALEDAMBIENTGOURAUD2", ""),
            ('USERDEFINED_1', "USERDEFINED_1", ""),
            ('USERDEFINED_2', "USERDEFINED_2", ""),
            ('USERDEFINED_3', "USERDEFINED_3", ""),
            ('USERDEFINED_4', "USERDEFINED_4", ""),
            ('USERDEFINED_5', "USERDEFINED_5", ""),
            ('USERDEFINED_6', "USERDEFINED_6", ""),
            ('USERDEFINED_7', "USERDEFINED_7", ""),
            ('USERDEFINED_8', "USERDEFINED_8", ""),
            ('USERDEFINED_9', "USERDEFINED_9", ""),
            ('USERDEFINED_10', "USERDEFINED_10", ""),
            ('USERDEFINED_11', "USERDEFINED_11", ""),
            ('USERDEFINED_12', "USERDEFINED_12", ""),
            ('USERDEFINED_13', "USERDEFINED_13", ""),
            ('USERDEFINED_14', "USERDEFINED_14", ""),
            ('USERDEFINED_15', "USERDEFINED_15", ""),
            ('USERDEFINED_16', "USERDEFINED_16", ""),
            ('USERDEFINED_17', "USERDEFINED_17", ""),
            ('USERDEFINED_18', "USERDEFINED_18", ""),
            ('USERDEFINED_19', "USERDEFINED_19", ""),
            ('USERDEFINED_20', "USERDEFINED_20", ""),
            ('USERDEFINED_21', "USERDEFINED_21", ""),
            ('USERDEFINED_22', "USERDEFINED_22", ""),
            ('USERDEFINED_23', "USERDEFINED_23", ""),
            ('USERDEFINED_24', "USERDEFINED_24", ""),
            ('USERDEFINED_25', "USERDEFINED_25", ""),
            ('USERDEFINED_26', "USERDEFINED_26", ""),
            ('USERDEFINED_27', "USERDEFINED_27", ""),
            ('USERDEFINED_28', "USERDEFINED_28", ""),
            ('USERDEFINED_29', "USERDEFINED_29", ""),
            ('USERDEFINED_30', "USERDEFINED_30", ""),
            ('USERDEFINED_31', "USERDEFINED_31", ""),
            ('USERDEFINED_32', "USERDEFINED_32", ""),
            ('USERDEFINED_33', "USERDEFINED_33", ""),
        ],
        default='USERDEFINED_2'
    )

    rgbpen: StringProperty(
        name="RGB",
        description="RGB Pen",
        default=""
    )

    brightness: FloatProperty(
        name="Brightness",
        description="Brightness",
        default=1
    )

    scaledambient: FloatProperty(
        name="Scaled Ambient",
        description="Scaled Ambient",
        default=1
    )

    simplespritehexfiftyflag: BoolProperty(
        name="Sprite Hex Fifty Flags",
        description="Sprite Hex Fifty Flags",
        default=False
    )

    doublesided: BoolProperty(
        name="Double Sided",
        description="Double Sided",
        default=False
    )


class MATERIAL_OT_add_default_wldmatdef(bpy.types.Operator):
    """Add default World Material Def properties to the selected material"""
    bl_idname = "material.add_default_wldmatdef"
    bl_label = "Add Default World MatDef"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_material

    def execute(self, context):
        material = context.object.active_material
        if not material:
            return {'CANCELLED'}
        material['quaildef'] = 'materialdefinition'
        material.quail_materialdefinition.rendermethod = 'TRANSPARENT'
        material.quail_materialdefinition.rgbpen = "255 255 255 255"
        material.quail_materialdefinition.brightness = 1
        material.quail_materialdefinition.scaledambient = 1
        material.quail_materialdefinition.simplespritehexfiftyflag = False
        material.quail_materialdefinition.doublesided = False
        return {'FINISHED'}




def add_default_quaildef(self, context):
    obj = context.object
    if not obj or not obj.active_material:
        return
    material = obj.active_material
    if not material.get('quaildef') == 'materialdefinition':
        return
    material.quail_materialdefinition.rendermethod = 'TRANSPARENT'
    material.quail_materialdefinition.rgbpen = "255 255 255 255"
    material.quail_materialdefinition.brightness = 1
    material.quail_materialdefinition.scaledambient = 1
    material.quail_materialdefinition.simplespritehexfiftyflag = False
    material.quail_materialdefinition.doublesided = False


def draw_materialdefinition_in_transform(self, context):
    obj = context.object
    if not obj or not obj.active_material:
        return

    material = obj.active_material
    if not material.get('quaildef') == 'materialdefinition' and not material.get('quaildef') == 'eqgmaterialdef':
        layout = self.layout
        box = layout.box()
        row = box.row(align=True)
        row.operator("material.add_default_wldmatdef", text="Set WLD Material")
        row.operator("material.add_default_eqgmatdef", text="Set EQG Material")
        return

    if material.get('quaildef') == 'eqgmaterialdef':
        return

    layout = self.layout
    box = layout.box()

    box.label(text="MATERIALDEFINITION")

    row = box.row()
    row.prop(material.quail_materialdefinition, "rendermethod")

    row = box.row()
    row.prop(material.quail_materialdefinition, "rgbpen")

    row = box.row()
    row.prop(material.quail_materialdefinition, "brightness")

    row = box.row()
    row.prop(material.quail_materialdefinition, "scaledambient")

    row = box.row()
    row.prop(material.quail_materialdefinition, "simplespritehexfiftyflag")

    row = box.row()
    row.prop(material.quail_materialdefinition, "doublesided")


# Register classes
def register():
    # Let auto_load handle class registration
    # (it will register QuailMaterialDefinitionProperties, MATERIAL_OT_add_default_wldmatdef, etc.)

    # Only register the property pointer which auto_load can't handle
    bpy.types.Material.quail_materialdefinition = PointerProperty(
        type=QuailMaterialDefinitionProperties)

    # Attach the panel to the UI
    try:
        import _cycles
        bpy.types.CYCLES_MATERIAL_PT_surface.prepend(draw_materialdefinition_in_transform)
    except (AttributeError, ImportError):
        pass

    try:
        bpy.types.EEVEE_MATERIAL_PT_surface.prepend(draw_materialdefinition_in_transform)
    except AttributeError:
        pass

    try:
        bpy.types.MATERIAL_PT_surface.prepend(draw_materialdefinition_in_transform)
    except AttributeError:
        bpy.types.MATERIAL_PT_viewport.prepend(draw_materialdefinition_in_transform)

def unregister():
    # Only unregister things we manually registered
    del bpy.types.Material.quail_materialdefinition

    # Remove from panels
    try:
        bpy.types.CYCLES_MATERIAL_PT_surface.remove(draw_materialdefinition_in_transform)
    except AttributeError:
        pass

    try:
        bpy.types.EEVEE_MATERIAL_PT_surface.remove(draw_materialdefinition_in_transform)
    except AttributeError:
        pass

    try:
        bpy.types.MATERIAL_PT_surface.remove(draw_materialdefinition_in_transform)
    except AttributeError:
        pass

    try:
        bpy.types.MATERIAL_PT_viewport.remove(draw_materialdefinition_in_transform)
    except AttributeError:
        pass
