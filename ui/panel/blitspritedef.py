# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false
# reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import BoolProperty, PointerProperty, IntProperty, EnumProperty, StringProperty, FloatProperty
from ...common.s3dmaterial import update_userdefined, update_rendermethod_node, update_transparent, update_simplesprite, sprite_items


# ----------------------------------------------------------
# Property Group
# ----------------------------------------------------------

class QuailBlitSpriteDefProperties(bpy.types.PropertyGroup):

    # --------------------------------------------------
    # Sprite
    # --------------------------------------------------

    simplespritetag: EnumProperty(
        name="SimpleSprite",
        description="Select a SimpleSprite node group",
        items=sprite_items,
        update=update_simplesprite
    )

    # --------------------------------------------------
    # Transparency
    # --------------------------------------------------

    transparent_override: BoolProperty(
        name="Transparent Override",
        description="Force material to behave as fully transparent",
        default=False,
        update=update_transparent
    )

    # --------------------------------------------------
    # Userdefined
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Drawstyle
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Lighting
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Shading
    # --------------------------------------------------

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

    # --------------------------------------------------
    # Texture Index
    # --------------------------------------------------

    texture_index: IntProperty(
        name="Texture",
        min=0,
        max=255,
        default=5,
        update=update_rendermethod_node
    )

    # --------------------------------------------------
    # Toggles
    # --------------------------------------------------

    masked: BoolProperty(
        name="Masked Transparency",
        default=False,
        update=update_rendermethod_node
    )

    alphablend: BoolProperty(
        name="Alpha Blend",
        default=False,
        update=update_rendermethod_node
    )

    additive: BoolProperty(
        name="Additive",
        default=False,
        update=update_rendermethod_node
    )

    dynamic: BoolProperty(
        name="Dynamic Lighting",
        default=False,
        update=update_rendermethod_node
    )

    prelit: BoolProperty(
        name="Prelit",
        default=False,
        update=update_rendermethod_node
    )

    opacity: FloatProperty(
        name="Opacity %",
        min=0.0,
        max=93.75,
        default=50.0,
        update=update_rendermethod_node
    )

    # Transparent BlitSprite flag

    transparent: BoolProperty(
        name="Transparent Blit Flag",
        default=False
    )


# ----------------------------------------------------------
# Panel
# ----------------------------------------------------------

def draw_blitspritedef_panel(self, context):

    obj = context.object

    if not obj:
        return

    if obj.get("quaildef") != "blitspritedef":
        return

    layout = self.layout
    props = obj.quail_blitspritedef

    box = layout.box()

    box.label(text="BLITSPRITEDEF")

    # --------------------------------------------------
    # Sprite
    # --------------------------------------------------

    box.label(text="Sprite")

    box.prop(props, "simplespritetag")

    # --------------------------------------------------
    # Separator
    # --------------------------------------------------

    line = box.row()
    line.alignment = 'CENTER'
    line.label(text="────────────────────────────")

    # --------------------------------------------------
    # Transparency
    # --------------------------------------------------

    box.prop(props, "transparent")

    # --------------------------------------------------
    # Separator
    # --------------------------------------------------

    line = box.row()
    line.alignment = 'CENTER'
    line.label(text="────────────────────────────")

    # --------------------------------------------------
    # Rendermethod
    # --------------------------------------------------

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


# ----------------------------------------------------------
# Register
# ----------------------------------------------------------

def register():

    bpy.types.Object.quail_blitspritedef = PointerProperty(
        type=QuailBlitSpriteDefProperties
    )

    bpy.types.OBJECT_PT_transform.prepend(
        draw_blitspritedef_panel
    )


def unregister():

    bpy.types.OBJECT_PT_transform.remove(
        draw_blitspritedef_panel
    )

    del bpy.types.Object.quail_blitspritedef