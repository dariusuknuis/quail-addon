# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
import os
from bpy.props import StringProperty, FloatProperty, FloatVectorProperty,BoolProperty, PointerProperty, IntProperty, EnumProperty
from ...common.rendermethod import apply_userdefined, sync_rendermethod_node

def update_userdefined(self, context):
    if not self.use_userdefined:
        return
    apply_userdefined(self, self.userdefined_index)
    mat = context.material
    if not mat:
        return

def update_rendermethod_node(self, context):
    mat = self.id_data
    if not isinstance(mat, bpy.types.Material):
        return

    sync_rendermethod_node(mat)

class QuailMaterialDefinitionProperties(bpy.types.PropertyGroup):

    # ---------------------------
    # Transparent Override
    # ---------------------------

    transparent_override: bpy.props.BoolProperty(
        name="Transparent",
        description="Force material to behave as fully transparent",
        default=False
    )

    # ---------------------------
    # Userdefined
    # ---------------------------

    use_userdefined: BoolProperty(
        name="Userdefined",
        default=False
    )

    userdefined_index: IntProperty(
        name="Userdefined Index",
        min=1,
        max=42,
        default=2,
        update=update_userdefined
    )

    # ---------------------------
    # Drawstyle
    # ---------------------------

    drawstyle: EnumProperty(
        name="Drawstyle",
        items=[
            ('DRAW0', "Draw0", ""),
            ('DRAW1', "Draw1", ""),
            ('WIREFRAME', "Wireframe", ""),
            ('SOLIDFILL', "SolidFill", ""),
        ],
        default='SOLIDFILL',
        update=update_rendermethod_node
    )

    # ---------------------------
    # Lighting
    # ---------------------------

    lighting: EnumProperty(
        name="Lighting",
        items=[
            ('ZEROINTENSITY', "ZeroIntensity", ""),
            ('LIGHT1', "Light1", ""),
            ('CONSTANT', "Constant", ""),
            ('LIGHT3', "Light3", ""),
            ('AMBIENT', "Ambient", ""),
            ('SCALEDAMBIENT', "ScaledAmbient", ""),
            ('LIGHT6', "Light6", ""),
            ('LIGHT7', "Light7", ""),
        ],
        default='AMBIENT',
        update=update_rendermethod_node
    )

    # ---------------------------
    # Shading
    # ---------------------------

    shading: EnumProperty(
        name="Shading",
        items=[
            ('SHADE0', "Shade0", ""),
            ('SHADE1', "Shade1", ""),
            ('GOURAUD1', "Gouraud1", ""),
            ('GOURAUD2', "Gouraud2", ""),
        ],
        default='GOURAUD1',
        update=update_rendermethod_node
    )

    # ---------------------------
    # Texture index
    # ---------------------------

    texture_index: IntProperty(
        name="Texture",
        min=0,
        max=255,
        default=5,
        update=update_rendermethod_node
    )

    # ---------------------------
    # Toggles
    # ---------------------------

    masked: BoolProperty(name="Masked Transparency", default=False, update=update_rendermethod_node)
    alphablend: BoolProperty(name="Alpha Blend", default=False, update=update_rendermethod_node)
    additive: BoolProperty(name="Additive", default=False, update=update_rendermethod_node)
    dynamic: BoolProperty(name="Dynamic Lighting", default=False, update=update_rendermethod_node)
    prelit: BoolProperty(name="Prelit", default=False, update=update_rendermethod_node)

    opacity: FloatProperty(
        name="Opacity %",
        min=0.0,
        max=100.0,
        default=100.0,
        update=update_rendermethod_node
    )

    rgbpen: FloatVectorProperty(
        name="RGB",
        description="RGB Pen",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0)
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

    simplespritehaveskipframes: BoolProperty(
        name="Simplesprite Have Skip Frames",
        description="Simplesprite Have Skip Frames",
        default=True
    )

    simplespriteskipframes: BoolProperty(
        name="Simplesprite Skip Frames",
        description="Simplesprite Skip Frames",
        default=True
    )

    uvshiftperms: FloatVectorProperty(
        name="UV Shift / ms",
        description="UV shift per millisecond (U, V)",
        size=2,
        subtype='NONE',  # keep numeric, not color
        default=(0.0, 0.0),
        precision=4
    )

    twosided: BoolProperty(
        name="Two-Sided",
        description="Two-Sided",
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
        material.quail_materialdefinition.rgbpen = (1.0, 1.0, 1.0)
        material.quail_materialdefinition.brightness = 1
        material.quail_materialdefinition.scaledambient = 1
        material.quail_materialdefinition.simplespritehaveskipframes = True
        material.quail_materialdefinition.simplespriteskipframes = True
        material.quail_materialdefinition.uvshiftperms = (0.0, 0.0)
        material.quail_materialdefinition.twosided = False
        return {'FINISHED'}

def add_default_quaildef(self, context):
    obj = context.object
    if not obj or not obj.active_material:
        return
    material = obj.active_material
    if not material.get('quaildef') == 'materialdefinition':
        return
    material.quail_materialdefinition.rendermethod = 'TRANSPARENT'
    material.quail_materialdefinition.rgbpen = (1.0, 1.0, 1.0)
    material.quail_materialdefinition.brightness = 1
    material.quail_materialdefinition.scaledambient = 1
    material.quail_materialdefinition.simplespritehaveskipframes = True
    material.quail_materialdefinition.simplespriteskipframes = True
    material.quail_materialdefinition.uvshiftperms = (0.0, 0.0)
    material.quail_materialdefinition.twosided = False

def draw_materialdefinition_in_transform(self, context):
    obj = context.object
    if not obj or not obj.active_material:
        return

    mat = obj.active_material
    layout = self.layout

    if mat.get('quaildef') != 'materialdefinition':
        box = layout.box()
        row = box.row()
        row.operator("material.add_default_wldmatdef", text="Set WLD Material")
        return

    props = mat.quail_materialdefinition

    # ----------------------------------------------------
    # MAIN BOX
    # ----------------------------------------------------

    box = layout.box()
    box.label(text="MATERIALDEFINITION")

    # ----------------------------------------------------
    # RENDERMETHOD SECTION
    # ----------------------------------------------------

    box.label(text="Rendermethod")

    if props.use_userdefined:
        # Show only userdefined controls
        box.prop(props, "use_userdefined")
        box.prop(props, "userdefined_index")

    elif props.transparent_override:
        # Show only transparent toggle
        box.prop(props, "transparent_override")

    else:
        # Normal Mode (show everything)
        box.prop(props, "use_userdefined")
        box.prop(props, "transparent_override")

        box.prop(props, "drawstyle")
        box.prop(props, "lighting")
        box.prop(props, "shading")
        box.prop(props, "texture_index")
        box.prop(props, "masked")
        box.prop(props, "alphablend")

        if props.alphablend:
            box.prop(props, "opacity")

        box.prop(props, "additive")
        box.prop(props, "dynamic")
        box.prop(props, "prelit")

    # ----------------------------------------------------
    # VISUAL SEPARATOR
    # ----------------------------------------------------

    line = box.row()
    line.alignment = 'CENTER'
    line.label(text="────────────────────────────")

    # ----------------------------------------------------
    # OTHER MATERIAL FIELDS
    # ----------------------------------------------------

    row = box.row(align=True)
    row.prop(props, "rgbpen", text="RGBPen")

    box.prop(props, "brightness")
    box.prop(props, "scaledambient")
    box.prop(props, "simplespritehaveskipframes")
    box.prop(props, "simplespriteskipframes")
    box.prop(props, "uvshiftperms")
    box.prop(props, "twosided")

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
