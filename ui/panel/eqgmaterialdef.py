# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
from bpy.types import Material
import os
from bpy.props import StringProperty, FloatProperty, FloatVectorProperty, BoolProperty, PointerProperty, IntProperty, EnumProperty, CollectionProperty
from ...logger.error import error
from ...common.eqgshaders import SHADER_FAMILIES, eqg_apply, parse_shader_tag
from ...common import state


def get_eqg_material(context):
    material = getattr(context, "material", None)

    if material is None:
        obj = getattr(context, "object", None)
        if obj is not None:
            material = obj.active_material

    if material is None:
        return None

    if material.get("quaildef") != "eqgmaterialdef":
        return None

    return material


def shader_property_items(self, context):
    """Dropdown choices for the currently parsed shader family."""

    material = get_eqg_material(context)
    if material is None:
        return ()

    family = SHADER_FAMILIES.get(
        material.quail_eqgmaterialdef.shader,
        SHADER_FAMILIES["C1"],
    )

    # Only family properties appear in the menu.
    return tuple(
        (property_name, property_name, "")
        for property_name in family.properties
    )

class QuailEqgShaderPropertyRow(bpy.types.PropertyGroup):
    # StringProperty allows an imported non-family property to be retained.
    property_name: StringProperty(
        name="Property",
        default="",
    )

# Define Actor properties
class QuailEqgMaterialDefinitionProperties(bpy.types.PropertyGroup):

    def update_shader(self, context):
        # Suppress callbacks during initial loading or another material rebuild.
        if state.QUAIL_UPDATING:
            return

        material = None

        for mat in bpy.data.materials:
            if (
                hasattr(mat, "quail_eqgmaterialdef")
                and mat.quail_eqgmaterialdef == self
            ):
                material = mat
                break

        if material is None:
            return

        state.QUAIL_UPDATING = True

        try:
            err = eqg_apply(material)
            if err:
                error(err)
                return

        finally:
            state.QUAIL_UPDATING = False

        if context.screen is not None:
            for area in context.screen.areas:
                if area.type == "PROPERTIES":
                    area.tag_redraw()

    property_rows: CollectionProperty(
        type=QuailEqgShaderPropertyRow,
    )

    shadertag: StringProperty(
        name="Shader Tag",
        description="Original WCE shader tag",
        default="",
        #update=update_shadertag,
    )

    alpha_mode: EnumProperty(
        name="Alpha Mode",
        items=(
            ("Opaque", "Opaque", ""),
            ("Alpha", "Alpha", ""),
            ("AddAlpha", "AddAlpha", ""),
            ("Chroma", "Chroma", ""),
        ),
        default="Opaque",
    )

    shader: EnumProperty(
        name="Shader",
        items=tuple(
            (name, name, "")
            for name in SHADER_FAMILIES
        ),
        default="C1",
    )

    e_fShininess0: FloatProperty(
        name="e_fShininess0",
        description="Shininess",
        min=1.0,
        max=128.0,
        default=12.0,
        update=update_shader
    )

    e_TextureDiffuse0: StringProperty(
        name="e_TextureDiffuse0",
        description="Diffuse Texture 0",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureDiffuse0mapChannel: StringProperty(
        name="e_TextureDiffuse0mapChannel",
        description="Diffuse Texture Map Channel",
        default="",
        update=update_shader
    )

    e_TextureDiffuse1: StringProperty(
        name="e_TextureDiffuse1",
        description="Diffuse Texture 1",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureEnvironment: StringProperty(
        name="e_TextureEnvironment",
        description="Environment Texture",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureEnvironment0: StringProperty(
        name="e_TextureEnvironment0",
        description="Environment Texture 0",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureFallback: StringProperty(
        name="e_TextureFallback",
        description="Fallback Texture",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureFallback0: StringProperty(
        name="e_TextureFallback0",
        description="Fallback Texture 0",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureNormal0: StringProperty(
        name="e_TextureNormal0",
        description="Normal Texture 0",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureNormal0mapChannel: StringProperty(
        name="e_TextureNormal0mapChannel",
        description="Normal Texture Map Channel",
        default="",
        update=update_shader
    )

    e_TextureNormal1: StringProperty(
        name="e_TextureNormal1",
        description="Normal Texture 1",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_fBumpiness0: FloatProperty(
        name="e_fBumpiness0",
        description="Bumpiness",
        soft_min=0.0,
        soft_max=10.0,
        default=0.0,
        update=update_shader
    )

    e_fCoverageScale0: FloatProperty(
        name="e_fCoverageScale0",
        description="Coverage Scale",
        min=0.0,
        max=100.0,
        default=0.05,
        update=update_shader
    )

    e_fEnvMapStrength0: FloatProperty(
        name="e_fEnvMapStrength0",
        description="Env Map Strength",
        min=0.1,
        max=2.0,
        default=1.0,
        update=update_shader
    )
    e_fFresnelBias: FloatProperty(
        name="e_fFresnelBias",
        description="Fresnel Bias",
        min=0.0,
        max=1.0,
        default=0.3,
        update=update_shader
    )

    e_fFresnelPower: FloatProperty(
        name="e_fFresnelPower",
        description="Fresnel Power",
        min=1.0,
        max=10.0,
        default=8.0,
        update=update_shader
    )

    e_fGloss0: FloatProperty(
        name="e_fGloss0",
        description="Gloss",
        min=0.0,
        max=1.0,
        default=0.5,
        update=update_shader
    )

    e_fGrassDensity0: FloatProperty(
        name="e_fGrassDensity0",
        description="Grass Density 0",
        default=0.0,
        update=update_shader
    )

    e_fGrassDensity1: FloatProperty(
        name="e_fGrassDensity1",
        description="Grass Density 1",
        default=0.0,
        update=update_shader
    )

    e_fGrassDensity2: FloatProperty(
        name="e_fGrassDensity2",
        description="Grass Density 2",
        default=0.0,
        update=update_shader
    )

    e_fGrassDensity3: FloatProperty(
        name="e_fGrassDensity3",
        description="Grass Density 3",
        default=0.0,
        update=update_shader
    )

    e_fGrassDensity4: FloatProperty(
        name="e_fGrassDensity4",
        description="Grass Density 4",
        default=0.0,
        update=update_shader
    )

    e_fGrassDensity5: FloatProperty(
        name="e_fGrassDensity5",
        description="Grass Density 5",
        default=0.0,
        update=update_shader
    )

    e_fGrassDensity6: FloatProperty(
        name="e_fGrassDensity6",
        description="Grass Density 6",
        default=0.0,
        update=update_shader
    )

    e_fGrassDensity7: FloatProperty(
        name="e_fGrassDensity7",
        description="Grass Density 7",
        default=0.0,
        update=update_shader
    )

    e_fGrassDensity8: FloatProperty(
        name="e_fGrassDensity8",
        description="Grass Density 8",
        default=0.0,
        update=update_shader
    )

    e_fGrassDensity9: FloatProperty(
        name="e_fGrassDensity9",
        description="Grass Density 9",
        default=0.0,
        update=update_shader
    )

    e_fReflectionAmount: FloatProperty(
        name="e_fReflectionAmount",
        description="Reflection Amount",
        min=0.0,
        max=2.0,
        default=0.8,
        update=update_shader
    )

    e_fReflectionColor: FloatVectorProperty(
        name="e_fReflectionColor",
        description="Reflection Color",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=update_shader
    )

    e_fScale0: FloatProperty(
        name="e_fScale0",
        description="Scale 0",
        default=1.0,
        update=update_shader
    )

    e_fScale1: FloatProperty(
        name="e_fScale1",
        description="Scale 1",
        default=1.0,
        update=update_shader
    )

    e_fScale2: FloatProperty(
        name="e_fScale2",
        description="Scale 2",
        default=1.0,
        update=update_shader
    )

    e_fScale3: FloatProperty(
        name="e_fScale3",
        description="Scale 3",
        default=1.0,
        update=update_shader
    )

    e_fScale4: FloatProperty(
        name="e_fScale4",
        description="Scale 4",
        default=1.0,
        update=update_shader
    )

    e_fScale5: FloatProperty(
        name="e_fScale5",
        description="Scale 5",
        default=1.0,
        update=update_shader
    )

    e_fScale6: FloatProperty(
        name="e_fScale6",
        description="Scale 6",
        default=1.0,
        update=update_shader
    )

    e_fScale7: FloatProperty(
        name="e_fScale7",
        description="Scale 7",
        default=1.0,
        update=update_shader
    )

    e_fScale8: FloatProperty(
        name="e_fScale8",
        description="Scale 8",
        default=1.0,
        update=update_shader
    )

    e_fScale9: FloatProperty(
        name="e_fScale9",
        description="Scale 9",
        default=1.0,
        update=update_shader
    )

    e_fSlide1X: FloatProperty(
        name="e_fSlide1X",
        description="Slide Speed 1 X",
        min=-100.0,
        max=100.0,
        default=0.02,
        update=update_shader
    )

    e_fSlide1Y: FloatProperty(
        name="e_fSlide1Y",
        description="Slide Speed 1 Y",
        min=-100.0,
        max=100.0,
        default=0.02,
        update=update_shader
    )

    e_fSlide2X: FloatProperty(
        name="e_fSlide2X",
        description="Slide Speed 2 X",
        min=-100.0,
        max=100.0,
        default=0.02,
        update=update_shader
    )

    e_fSlide2Y: FloatProperty(
        name="e_fSlide2Y",
        description="Slide Speed 2 Y",
        min=-100.0,
        max=100.0,
        default=0.02,
        update=update_shader
    )

    e_fWaterColor1: FloatVectorProperty(
        name="e_fWaterColor1",
        description="Water Color 1",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=update_shader
    )

    e_fWaterColor2: FloatVectorProperty(
        name="e_fWaterColor2",
        description="Water Color 2",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=update_shader
    )

    e_TextureCoverage: StringProperty(
        name="e_TextureCoverage",
        description="Coverage Texture",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureCoverage0: StringProperty(
        name="e_TextureCoverage0",
        description="Coverage Texture 0",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureDetail0: StringProperty(
        name="e_TextureDetail0",
        description="Detail Texture 0",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureDetail1: StringProperty(
        name="e_TextureDetail1",
        description="Detail Texture 1",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureDetail2: StringProperty(
        name="e_TextureDetail2",
        description="Detail Texture 2",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureDetail3: StringProperty(
        name="e_TextureDetail3",
        description="Detail Texture 3",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureDetail4: StringProperty(
        name="e_TextureDetail4",
        description="Detail Texture 4",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureDetail5: StringProperty(
        name="e_TextureDetail5",
        description="Detail Texture 5",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureDetail6: StringProperty(
        name="e_TextureDetail6",
        description="Detail Texture 6",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureDetail7: StringProperty(
        name="e_TextureDetail7",
        description="Detail Texture 7",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureDetail8: StringProperty(
        name="e_TextureDetail8",
        description="Detail Texture 8",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureDetail9: StringProperty(
        name="e_TextureDetail9",
        description="Detail Texture 9",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureGlow0: StringProperty(
        name="e_TextureGlow0",
        description="Glow Texture 0",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TexturePalette0: StringProperty(
        name="e_TexturePalette0",
        description="Palette Texture 0",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureSecond0: StringProperty(
        name="e_TextureSecond0",
        description="Second Texture 0",
        default="",
        subtype='FILE_PATH',
        options={'TEXTEDIT_UPDATE'},
        update=update_shader
    )

    e_TextureSecond0mapChannel: StringProperty(
        name="e_TextureSecond0mapChannel",
        description="Second Texture 0 Map Channel",
        default="",
        update=update_shader
    )

    animsleep: IntProperty(
        name="Anim Sleep",
        description="Anim Sleep",
        default=0
    )

def draw_eqgmaterialdefinition_in_transform(self, context):
    material = get_eqg_material(context)
    if material is None:
        return

    box = self.layout.box()
    box.label(text="EQGMATERIALDEF")

    # Original WCE shader tag.
    row = box.row()
    row.prop(material.quail_eqgmaterialdef, "shadertag")

    # Parsed classifications.
    row = box.row(align=True)
    row.prop(material.quail_eqgmaterialdef, "alpha_mode")
    row.prop(material.quail_eqgmaterialdef, "shader")

    # Actual properties present on this material.
    for index, item in enumerate(material.quail_eqgmaterialdef.property_rows):
        row = box.row(align=True)

        property_name = item.property_name

        # This button displays the stored property name.
        # The popup only contains properties from settings.shader.
        choose = row.operator_menu_enum(
            "material.choose_eqg_shader_property",
            "property_name",
            text=property_name or "Choose Property",
        )
        choose.index = index

        # Draw the corresponding typed Blender property.
        if property_name and hasattr(material.quail_eqgmaterialdef, property_name):
            row.prop(
                material.quail_eqgmaterialdef,
                property_name,
                text="",
            )
        else:
            row.label(
                text="Unsupported property",
                icon="ERROR",
            )

        remove = row.operator(
            "material.remove_eqg_shader_property",
            text="",
            icon="X",
        )
        remove.index = index

    # Add a new property from the current family's choices.
    row = box.row()

    add = row.operator_menu_enum(
        "material.choose_eqg_shader_property",
        "property_name",
        text="Add Property",
        icon="ADD",
    )
    add.index = -1

    row = box.row()
    row.prop(material.quail_eqgmaterialdef, "animsleep")

class MATERIAL_OT_choose_eqg_shader_property(bpy.types.Operator):
    bl_idname = "material.choose_eqg_shader_property"
    bl_label = "Choose EQG Shader Property"
    bl_options = {"REGISTER", "UNDO"}

    # -1 means add a new row.
    index: IntProperty(default=-1)

    property_name: EnumProperty(
        name="Property",
        items=shader_property_items,
    )

    def execute(self, context):
        material = get_eqg_material(context)
        if material is None:
            return {"CANCELLED"}

        # Prevent duplicate rows.
        for index, item in enumerate(material.quail_eqgmaterialdef.property_rows):
            if index == self.index:
                continue

            if item.property_name == self.property_name:
                self.report(
                    {"WARNING"},
                    f"{self.property_name} is already present",
                )
                return {"CANCELLED"}

        if self.index == -1:
            item = material.quail_eqgmaterialdef.property_rows.add()
            item.property_name = self.property_name

        elif 0 <= self.index < len(material.quail_eqgmaterialdef.property_rows):
            item = material.quail_eqgmaterialdef.property_rows[self.index]
            item.property_name = self.property_name

        else:
            return {"CANCELLED"}

        err = eqg_apply(material)
        if err:
            self.report({"ERROR"}, err)
            return {"CANCELLED"}

        return {"FINISHED"}

class MATERIAL_OT_remove_eqg_shader_property(bpy.types.Operator):
    bl_idname = "material.remove_eqg_shader_property"
    bl_label = "Remove EQG Shader Property"
    bl_options = {"REGISTER", "UNDO"}

    index: IntProperty()

    def execute(self, context):
        material = get_eqg_material(context)
        if material is None:
            return {"CANCELLED"}

        if not 0 <= self.index < len(material.quail_eqgmaterialdef.property_rows):
            return {"CANCELLED"}

        material.quail_eqgmaterialdef.property_rows.remove(self.index)

        err = eqg_apply(material)
        if err:
            self.report({"ERROR"}, err)
            return {"CANCELLED"}

        return {"FINISHED"}

class MATERIAL_OT_add_default_eqgmatdef(bpy.types.Operator):
    """Add default EQG Material Def properties to the selected material"""
    bl_idname = "material.add_default_eqgmatdef"
    bl_label = "Add Default EQG MatDef"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object and context.object.active_material

    def execute(self, context):
        material = context.object.active_material
        if not material:
            return {"CANCELLED"}

        material["quaildef"] = "eqgmaterialdef"

        previous_updating = state.QUAIL_UPDATING
        state.QUAIL_UPDATING = True

        try:
            material.quail_eqgmaterialdef.shadertag = "Opaque_MaxCB1.fx"

            alpha_mode, shader = parse_shader_tag(
                material.quail_eqgmaterialdef.shadertag
            )

            material.quail_eqgmaterialdef.alpha_mode = alpha_mode
            material.quail_eqgmaterialdef.shader = shader

            material.quail_eqgmaterialdef.e_fShininess0 = 12.0
            material.quail_eqgmaterialdef.e_fBumpiness0 = 0.0
            material.quail_eqgmaterialdef.e_fCoverageScale0 = 0.05
            material.quail_eqgmaterialdef.e_fEnvMapStrength0 = 1.0
            material.quail_eqgmaterialdef.e_fFresnelBias = 0.3
            material.quail_eqgmaterialdef.e_fFresnelPower = 8.0
            material.quail_eqgmaterialdef.e_fGloss0 = 0.5
            material.quail_eqgmaterialdef.e_fReflectionAmount = 0.8

            material.quail_eqgmaterialdef.e_fReflectionColor = (
                1.0, 1.0, 1.0, 1.0
            )
            material.quail_eqgmaterialdef.e_fWaterColor1 = (
                1.0, 1.0, 1.0, 1.0
            )
            material.quail_eqgmaterialdef.e_fWaterColor2 = (
                1.0, 1.0, 1.0, 1.0
            )

            for i in range(10):
                setattr(material.quail_eqgmaterialdef, f"e_fScale{i}", 1.0)
                setattr(material.quail_eqgmaterialdef, f"e_fGrassDensity{i}", 0.0)
                setattr(material.quail_eqgmaterialdef, f"e_TextureDetail{i}", "")

            material.quail_eqgmaterialdef.e_fSlide1X = 0.02
            material.quail_eqgmaterialdef.e_fSlide1Y = 0.02
            material.quail_eqgmaterialdef.e_fSlide2X = 0.02
            material.quail_eqgmaterialdef.e_fSlide2Y = 0.02

            # String texture properties can correctly use "".
            material.quail_eqgmaterialdef.e_TextureDiffuse0 = ""
            material.quail_eqgmaterialdef.e_TextureNormal0 = ""
            material.quail_eqgmaterialdef.e_TextureCoverage0 = ""
            # Continue resetting the remaining texture strings.

        finally:
            state.QUAIL_UPDATING = previous_updating

        err = eqg_apply(material)
        if err:
            error(err)
            return {"CANCELLED"}

        return {"FINISHED"}


# Register classes
def register():
    # ignored, auto_load bpy.utils.register_class(QuailMaterialDefinitionProperties)
    # Add this line to register the operator
    # bpy.utils.register_class(MATERIAL_OT_add_default_quaildef)

    bpy.types.Material.quail_eqgmaterialdef = PointerProperty(
        type=QuailEqgMaterialDefinitionProperties)

    # Try multiple Surface panel variants (Blender 4.2.1 has different panels per render engine)
    try:
        # For Cycles render engine
        import _cycles
        bpy.types.CYCLES_MATERIAL_PT_surface.prepend(
            draw_eqgmaterialdefinition_in_transform)
    except (AttributeError, ImportError):
        pass

    try:
        # For Eevee render engine
        bpy.types.EEVEE_MATERIAL_PT_surface.prepend(
            draw_eqgmaterialdefinition_in_transform)
    except AttributeError:
        pass

    # Generic surface panel (fallback)
    try:
        bpy.types.MATERIAL_PT_surface.prepend(
            draw_eqgmaterialdefinition_in_transform)
    except AttributeError:
        # Last resort, use viewport panel
        print("Using viewport panel as fallback")
        # Keep your existing code as fallback
        bpy.types.MATERIAL_PT_viewport.prepend(
            draw_eqgmaterialdefinition_in_transform)


def unregister():
    # Add this line to unregister the operator
    # bpy.utils.unregister_class(MATERIAL_OT_add_default_quaildef)
    del bpy.types.Material.quail_eqgmaterialdef

    # Remove from all possible panels
    try:
        bpy.types.CYCLES_MATERIAL_PT_surface.remove(
            draw_eqgmaterialdefinition_in_transform)
    except AttributeError:
        pass

    try:
        bpy.types.EEVEE_MATERIAL_PT_surface.remove(
            draw_eqgmaterialdefinition_in_transform)
    except AttributeError:
        pass

    try:
        bpy.types.MATERIAL_PT_surface.remove(
            draw_eqgmaterialdefinition_in_transform)
    except AttributeError:
        pass

    try:
        bpy.types.MATERIAL_PT_viewport.remove(
            draw_eqgmaterialdefinition_in_transform)
    except AttributeError:
        pass
