# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
import os
from bpy.props import StringProperty, FloatProperty, FloatVectorProperty,BoolProperty, PointerProperty, IntProperty, EnumProperty
from ...common.s3dmaterial import update_userdefined, update_rendermethod_node, update_transparent, update_simplesprite, update_twosided, sprite_items

class QuailRenderInfoProperties(bpy.types.PropertyGroup):

    transparent_override: BoolProperty(
        name="Transparent",
        default=False,
        update=update_transparent
    )

    use_userdefined: BoolProperty(
        name="Userdefined",
        default=False,
        update=update_userdefined
    )

    userdefined_index: IntProperty(
        name="Userdefined Index",
        min=1,
        max=41,
        default=2,
        update=update_userdefined
    )

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

    texture_index: IntProperty(
        name="Texture",
        min=0,
        max=255,
        default=0,
        update=update_rendermethod_node
    )

    masked: BoolProperty(default=False, update=update_rendermethod_node)
    alphablend: BoolProperty(default=False, update=update_rendermethod_node)
    additive: BoolProperty(default=False, update=update_rendermethod_node)
    dynamic: BoolProperty(default=False, update=update_rendermethod_node)
    prelit: BoolProperty(default=False, update=update_rendermethod_node)

    opacity: FloatProperty(
        name="Opacity %",
        min=0.0,
        max=93.75,
        default=50.0,
        update=update_rendermethod_node
    )

    rgbpen: FloatVectorProperty(
        name="RGB",
        subtype='COLOR',
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0)
    )

    has_brightness: BoolProperty(default=False)
    brightness: FloatProperty(default=1.0)

    has_scaledambient: BoolProperty(default=False)
    scaledambient: FloatProperty(default=1.0)

    has_simplesprite: BoolProperty(default=False)
    simplespritetag: EnumProperty(
        name="SimpleSprite",
        items=sprite_items,
        update=update_simplesprite
    )

    simplespritehaveskipframes: BoolProperty(default=False)
    simplespriteskipframes: BoolProperty(default=False)

    twosided: BoolProperty(
        name="Two-Sided",
        default=False,
        update=update_twosided
    )

def draw_renderinfo_panel(self, context):

    obj = context.object
    if not obj or not obj.active_material:
        return

    mat = obj.active_material
    layout = self.layout

    if mat.get('quaildef') != 'renderinfo':
        return

    props = mat.quail_renderinfo

    box = layout.box()
    box.label(text="RENDERINFO")

    # ----------------------------------------
    # Rendermethod
    # ----------------------------------------

    box.label(text="Rendermethod")

    if props.use_userdefined:
        box.prop(props, "use_userdefined")
        box.prop(props, "userdefined_index")

    elif props.transparent_override:
        box.prop(props, "transparent_override")

    else:
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

    # ----------------------------------------
    # Separator
    # ----------------------------------------

    line = box.row()
    line.alignment = 'CENTER'
    line.label(text="────────────────────────────")

    row = box.row()
    row.prop(props, "rgbpen")

    box.prop(props, "has_brightness")
    if props.has_brightness:
        box.prop(props, "brightness")

    box.prop(props, "has_scaledambient")
    if props.has_scaledambient:
        box.prop(props, "scaledambient")

    # ----------------------------------------
    # Separator
    # ----------------------------------------

    line = box.row()
    line.alignment = 'CENTER'
    line.label(text="────────────────────────────")

    box.label(text="SimpleSpriteInst")

    box.prop(props, "has_simplesprite")
    if props.has_simplesprite:
        box.prop(props, "simplespritetag")
    box.prop(props, "simplespritehaveskipframes")
    box.prop(props, "simplespriteskipframes")

    # ----------------------------------------
    # Separator
    # ----------------------------------------

    line = box.row()
    line.alignment = 'CENTER'
    line.label(text="────────────────────────────")

    box.prop(props, "twosided")

def register():

    bpy.types.Material.quail_renderinfo = PointerProperty(
        type=QuailRenderInfoProperties
    )

    try:
        bpy.types.CYCLES_MATERIAL_PT_surface.prepend(draw_renderinfo_panel)
    except:
        pass

    try:
        bpy.types.EEVEE_MATERIAL_PT_surface.prepend(draw_renderinfo_panel)
    except:
        pass

    try:
        bpy.types.MATERIAL_PT_surface.prepend(draw_renderinfo_panel)
    except:
        bpy.types.MATERIAL_PT_viewport.prepend(draw_renderinfo_panel)


def unregister():

    del bpy.types.Material.quail_renderinfo

    try:
        bpy.types.CYCLES_MATERIAL_PT_surface.remove(draw_renderinfo_panel)
    except:
        pass

    try:
        bpy.types.EEVEE_MATERIAL_PT_surface.remove(draw_renderinfo_panel)
    except:
        pass

    try:
        bpy.types.MATERIAL_PT_surface.remove(draw_renderinfo_panel)
    except:
        pass

    try:
        bpy.types.MATERIAL_PT_viewport.remove(draw_renderinfo_panel)
    except:
        pass