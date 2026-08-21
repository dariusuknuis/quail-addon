# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
from bpy_extras.io_utils import ImportHelper
import os
from bpy.props import StringProperty, FloatProperty, FloatVectorProperty, PointerProperty, IntProperty, EnumProperty, CollectionProperty
from ...logger.error import error
from ...common.eqgshaders import SHADER_FAMILIES, eqg_apply, parse_shader_tag
from ...common.eqgshaders import replace_shadertag_alpha_mode, replace_shadertag_shader
from ...common import state
from ...convert.material import convert_to_eqgmaterialdef


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

    def update_alpha_mode(self, context):
        """Update only the alpha-mode marker, then rebuild the material."""

        if state.QUAIL_UPDATING:
            return

        state.QUAIL_UPDATING = True
        try:
            self.shadertag = replace_shadertag_alpha_mode(
                self.shadertag,
                self.alpha_mode,
            )
        finally:
            state.QUAIL_UPDATING = False

        self.update_shader(context)

    def update_shader_family(self, context):
        """Update only the shader marker, then rebuild the material."""

        if state.QUAIL_UPDATING:
            return

        state.QUAIL_UPDATING = True
        try:
            self.shadertag = replace_shadertag_shader(
                self.shadertag,
                self.shader,
            )
        finally:
            state.QUAIL_UPDATING = False

        self.update_shader(context)

    property_rows: CollectionProperty(
        type=QuailEqgShaderPropertyRow,
    )

    shadertag: StringProperty(
        name="Shader Tag",
        description="Original WCE shader tag",
        default="",
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
        update=update_alpha_mode,
    )

    shader: EnumProperty(
        name="Shader",
        items=tuple(
            (name, name, "")
            for name in SHADER_FAMILIES
        ),
        default="C1",
        update=update_shader_family,
    )

    e_fShininess0: FloatProperty(
        name="e_fShininess0",
        description="Shininess",
        min=1.0,
        max=128.0,
        default=12.0,
        update=update_shader
    )

    e_TextureDiffuse0: PointerProperty(
        name="e_TextureDiffuse0",
        description="Diffuse Texture 0",
        type=bpy.types.Image,
        update=update_shader,
    )

    e_TextureDiffuse0mapChannel: StringProperty(
        name="e_TextureDiffuse0mapChannel",
        description="Diffuse Texture Map Channel",
        default="",
        update=update_shader
    )

    e_TextureDiffuse1: PointerProperty(
        name="e_TextureDiffuse1",
        description="Diffuse Texture 1",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureEnvironment: PointerProperty(
        name="e_TextureEnvironment",
        description="Environment Texture",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureEnvironment0: PointerProperty(
        name="e_TextureEnvironment0",
        description="Environment Texture 0",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureFallback: PointerProperty(
        name="e_TextureFallback",
        description="Fallback Texture",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureFallback0: PointerProperty(
        name="e_TextureFallback0",
        description="Fallback Texture 0",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureNormal0: PointerProperty(
        name="e_TextureNormal0",
        description="Normal Texture 0",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureNormal0mapChannel: StringProperty(
        name="e_TextureNormal0mapChannel",
        description="Normal Texture Map Channel",
        default="",
        update=update_shader
    )

    e_TextureNormal1: PointerProperty(
        name="e_TextureNormal1",
        description="Normal Texture 1",
        type=bpy.types.Image,
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

    e_fCoverageScale: FloatProperty(
            name="e_fCoverageScale",
            description="Coverage Scale",
            min=0.0,
            max=100.0,
            default=0.05,
            update=update_shader
        )

    e_fCoverageScale0: FloatProperty(
        name="e_fCoverageScale0",
        description="Coverage Scale 0",
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

    e_TextureCoverage: PointerProperty(
        name="e_TextureCoverage",
        description="Coverage Texture",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureCoverage0: PointerProperty(
        name="e_TextureCoverage0",
        description="Coverage Texture 0",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureDetail0: PointerProperty(
        name="e_TextureDetail0",
        description="Detail Texture 0",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureDetail1: PointerProperty(
        name="e_TextureDetail1",
        description="Detail Texture 1",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureDetail2: PointerProperty(
        name="e_TextureDetail2",
        description="Detail Texture 2",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureDetail3: PointerProperty(
        name="e_TextureDetail3",
        description="Detail Texture 3",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureDetail4: PointerProperty(
        name="e_TextureDetail4",
        description="Detail Texture 4",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureDetail5: PointerProperty(
        name="e_TextureDetail5",
        description="Detail Texture 5",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureDetail6: PointerProperty(
        name="e_TextureDetail6",
        description="Detail Texture 6",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureDetail7: PointerProperty(
        name="e_TextureDetail7",
        description="Detail Texture 7",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureDetail8: PointerProperty(
        name="e_TextureDetail8",
        description="Detail Texture 8",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureDetail9: PointerProperty(
        name="e_TextureDetail9",
        description="Detail Texture 9",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureGlow0: PointerProperty(
        name="e_TextureGlow0",
        description="Glow Texture 0",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TexturePalette0: PointerProperty(
        name="e_TexturePalette0",
        description="Palette Texture 0",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureSecond0: PointerProperty(
        name="e_TextureSecond0",
        description="Second Texture 0",
        type=bpy.types.Image,
        update=update_shader
    )

    e_TextureSecond0mapChannel: StringProperty(
        name="e_TextureSecond0mapChannel",
        description="Second Texture 0 Map Channel",
        default="",
        update=update_shader
    )

def draw_eqgmaterialdefinition_in_transform(self, context):
	material = getattr(context, "material", None)

	if material is None:
		obj = getattr(context, "object", None)

		if obj is not None:
			material = obj.active_material

	if material is None:
		return

	layout = self.layout

	if material.get("quaildef") != "eqgmaterialdef":
		box = layout.box()
		box.operator("material.add_default_eqgmatdef", text="Set EQG Material")
		return

	props = material.quail_eqgmaterialdef
	box = layout.box()
	box.label(text="EQGMATERIALDEF")

	# Original WCE shader tag.
	row = box.row()
	row.prop(props, "shadertag")

	# Parsed classifications.
	row = box.row(align=True)
	row.prop(props, "alpha_mode")
	row.prop(props, "shader")

	# Actual properties present on this material.
	for index, item in enumerate(props.property_rows):
		row = box.row(align=True)
		property_name = item.property_name

		choose = row.operator_menu_enum(
			"material.choose_eqg_shader_property",
			"property_name",
			text=property_name or "Choose Property",
		)
		choose.index = index

		if property_name and hasattr(props, property_name):
			rna_property = props.bl_rna.properties.get(property_name)

			is_image_property = (
				rna_property is not None
				and rna_property.type == 'POINTER'
				and rna_property.fixed_type.identifier == "Image"
			)

			if is_image_property:
				row.prop_search(
					props,
					property_name,
					bpy.data,
					"images",
					text="",
				)

				load = row.operator(
					"material.load_eqg_image",
					text="",
					icon="FILE_FOLDER",
				)
				load.material_name = material.name
				load.property_name = property_name

			else:
				row.prop(props, property_name, text="")

		else:
			row.label(text="Unsupported property", icon="ERROR")

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


class MATERIAL_OT_load_eqg_image(bpy.types.Operator, ImportHelper):
    bl_idname = "material.load_eqg_image"
    bl_label = "Load EQG Image"
    bl_options = {"REGISTER", "UNDO"}

    filter_glob: StringProperty(
        default="*.dds;*.bmp;*.png;*.tga",
        options={"HIDDEN"},
    )

    material_name: StringProperty(
        options={"HIDDEN"},
    )

    property_name: StringProperty(
        options={"HIDDEN"},
    )

    def execute(self, context):
        # Import locally to avoid an add-on initialization dependency loop.
        from ...common.image_loader import load_eqg_image

        material = bpy.data.materials.get(self.material_name)
        if material is None:
            self.report(
                {"ERROR"},
                f"Material not found: {self.material_name}",
            )
            return {"CANCELLED"}

        if material.get("quaildef") != "eqgmaterialdef":
            self.report(
                {"ERROR"},
                f"{material.name} is not an EQG material",
            )
            return {"CANCELLED"}

        if not hasattr(
            material.quail_eqgmaterialdef,
            self.property_name,
        ):
            self.report(
                {"ERROR"},
                f"Unknown EQG property: {self.property_name}",
            )
            return {"CANCELLED"}

        # load_eqg_image expects the filename separately from assets_path.
        assets_path = os.path.dirname(self.filepath)
        filename = bpy.path.basename(self.filepath)

        loader_context = type(
            "EqgImageLoaderContext",
            (),
            {
                "parser": type(
                    "EqgImageLoaderParser",
                    (),
                    {"assets_path": assets_path},
                )()
            },
        )()


        image, err = load_eqg_image(
            loader_context,
            filename,
            flip_tex=False,
        )

        if err:
            self.report({"ERROR"}, err)
            return {"CANCELLED"}

        if image is None:
            self.report(
                {"ERROR"},
                f"Could not load image: {self.filepath}",
            )
            return {"CANCELLED"}

        setattr(
            material.quail_eqgmaterialdef,
            self.property_name,
            image,
        )

        return {"FINISHED"}

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

        if material is None:
            return {'CANCELLED'}

        err = convert_to_eqgmaterialdef(material, context)

        if err:
            self.report({'ERROR'}, err)
            return {'CANCELLED'}

        self.report(
            {'INFO'},
            f"Converted {material.name} to EQGMATERIALDEF",
        )
        return {'FINISHED'}


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
