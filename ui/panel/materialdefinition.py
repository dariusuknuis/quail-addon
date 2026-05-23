# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
import os
from bpy.props import StringProperty, FloatProperty, FloatVectorProperty,BoolProperty, PointerProperty, IntProperty, EnumProperty
from ...common.s3dmaterial import update_userdefined, update_rendermethod_node, update_transparent, update_simplesprite, update_twosided, sprite_items
from ...common.rendermethod import create_rendermethod_nodegroup

class QuailMaterialDefinitionProperties(bpy.types.PropertyGroup):

    # ---------------------------
    # Transparent Override
    # ---------------------------

    transparent_override: BoolProperty(
        name="Transparent",
        description="Force material to behave as fully transparent",
        default=False,
        update=update_transparent
    )

    # ---------------------------
    # Userdefined
    # ---------------------------

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
        max=93.75,
        default=50.0,
        update=update_rendermethod_node
    )

    variation: BoolProperty(
        name="Variation",
        default = False
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

    simplespritetag: EnumProperty(
        name="SimpleSprite",
        description="Select a SimpleSprite node group",
        items=sprite_items,
        update=update_simplesprite
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

    has_uvshiftperms: BoolProperty(
        name="UV Shift / ms",
        description="UV shift per millisecond (U, V)",
        default=True
    )

    uvshiftperms: FloatVectorProperty(
        size=2,
        subtype='NONE',  # keep numeric, not color
        default=(0.0, 0.0),
        precision=8
    )

    twosided: BoolProperty(
        name="Two-Sided",
        description="Two-Sided",
        default=False,
        update = update_twosided
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

        # ------------------------------------------------
        # Rename
        # ------------------------------------------------

        base_name = material.name.upper()

        if not base_name.endswith("_MDF"):
            material.name = f"{base_name}_MDF"

        # ------------------------------------------------
        # Tag
        # ------------------------------------------------

        material['quaildef'] = 'materialdefinition'

        props = material.quail_materialdefinition

        # ------------------------------------------------
        # Defaults
        # ------------------------------------------------

        props.transparent_override = True
        props.variation = False
        props.rgbpen = (1.0, 1.0, 1.0)
        props.brightness = 1
        props.scaledambient = 1
        props.simplespritehaveskipframes = False
        props.simplespriteskipframes = False
        props.has_uvshiftperms = True
        props.uvshiftperms = (0.0, 0.0)
        props.twosided = False

        # ------------------------------------------------
        # Build material node tree
        # ------------------------------------------------

        material.use_nodes = True

        if not material.node_tree:
            return {'CANCELLED'}

        nodes = material.node_tree.nodes
        links = material.node_tree.links

        nodes.clear()

        group_tree = create_rendermethod_nodegroup()

        group_node = nodes.new("ShaderNodeGroup")
        group_node.node_tree = group_tree
        group_node.location = (0, 0)

        output = nodes.new("ShaderNodeOutputMaterial")
        output.location = (300, 0)

        links.new(
            group_node.outputs["Shader"],
            output.inputs["Surface"]
        )

        hide_inputs = {
            "PassableDisplay",
            "Masked",
            "AlphaBlend",
            "Additive",
            "Opacity",
            "Drawstyle",
            "TextureIndex",
            "Transparent Blit",
            "Particle Tint",
        }

        for socket in group_node.inputs:
            if socket.name in hide_inputs:
                socket.hide = True

        # ------------------------------------------------
        # Apply panel-driven settings
        # ------------------------------------------------

        update_rendermethod_node(props, context)
        update_simplesprite(props, context)
        update_twosided(props, context)

        return {'FINISHED'}

def draw_materialdefinition_panel(self, context):
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

    # ----------------------------------------------------
    # VISUAL SEPARATOR
    # ----------------------------------------------------

    line = box.row()
    line.alignment = 'CENTER'
    line.label(text="────────────────────────────")

    # ----------------------------------------------------
    # SIMPLESPRITEINST
    # ----------------------------------------------------

    box.label(text="SimpleSpriteInst")
    box.prop(props, "simplespritetag")
    box.prop(props, "simplespritehaveskipframes")
    box.prop(props, "simplespriteskipframes")

    # ----------------------------------------------------
    # VISUAL SEPARATOR
    # ----------------------------------------------------

    line = box.row()
    line.alignment = 'CENTER'
    line.label(text="────────────────────────────")

    box.prop(props, "has_uvshiftperms")
    if props.has_uvshiftperms:
        row = box.row(align=True)
        row.prop(props, "uvshiftperms")
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
        bpy.types.CYCLES_MATERIAL_PT_surface.prepend(draw_materialdefinition_panel)
    except (AttributeError, ImportError):
        pass

    try:
        bpy.types.EEVEE_MATERIAL_PT_surface.prepend(draw_materialdefinition_panel)
    except AttributeError:
        pass

    try:
        bpy.types.MATERIAL_PT_surface.prepend(draw_materialdefinition_panel)
    except AttributeError:
        bpy.types.MATERIAL_PT_viewport.prepend(draw_materialdefinition_panel)

def unregister():
    # Only unregister things we manually registered
    del bpy.types.Material.quail_materialdefinition

    # Remove from panels
    try:
        bpy.types.CYCLES_MATERIAL_PT_surface.remove(draw_materialdefinition_panel)
    except AttributeError:
        pass

    try:
        bpy.types.EEVEE_MATERIAL_PT_surface.remove(draw_materialdefinition_panel)
    except AttributeError:
        pass

    try:
        bpy.types.MATERIAL_PT_surface.remove(draw_materialdefinition_panel)
    except AttributeError:
        pass

    try:
        bpy.types.MATERIAL_PT_viewport.remove(draw_materialdefinition_panel)
    except AttributeError:
        pass
