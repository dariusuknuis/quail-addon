import re
import bpy
from bpy.props import IntProperty, PointerProperty
from ...common import base_tag

VARIATION_REGEX = re.compile(
    r'^[A-Z]{3}(CH|FA|FT|HE|HN|LG|MN|TA|TL|UA)\d{4}_MDF$'
)

# =========================================================
# TAG PARSING
# =========================================================

def parse_variation_tag(tag):

    original_tag = base_tag(tag)

    # ------------------------------------------------
    # Eyes
    # ------------------------------------------------

    if original_tag.startswith("CHR_EYE"):

        digits = original_tag[-7:-4]

        if digits.isdigit():

            return {
                "type": "eye",
                "family": original_tag[:-7],
                "eye_index": int(digits),
            }

    # ------------------------------------------------
    # Cloaks
    # ------------------------------------------------

    if original_tag.startswith("CLK"):

        if len(original_tag) >= 11:

            return {
                "type": "cloak",
                "prefix": "CLK",
                "material_index": int(original_tag[3:5]),
                "face_index": int(original_tag[5]),
                "material_number": int(original_tag[6]),
            }

    # ------------------------------------------------
    # Standard materials
    # ------------------------------------------------

    if VARIATION_REGEX.match(original_tag):

        return {
            "type": "material",
            "prefix": original_tag[:5],
            "material_index": int(original_tag[5:7]),
            "face_index": int(original_tag[7]),
            "material_number": int(original_tag[8]),
        }

    return None

# =========================================================
# MATERIAL PALETTE LOOKUP
# =========================================================

def get_material_palette_materials(obj):

    props = None

    if obj.get("quaildef") == "dmspritedef2":
        props = obj.quail_dmspritedef2

    elif obj.get("quaildef") == "dmspritedefinition":
        props = obj.quail_dmspritedefinition

    if not props:
        return set()

    palette_obj = props.materialpalette

    if not palette_obj:
        return set()

    palette_props = palette_obj.quail_materialpalette

    result = set()

    for item in palette_props.materials:
        if item.material:
            result.add(base_tag(item.material.name))

    return result

# =========================================================
# UPDATE
# =========================================================

def update_variation_materials(self, context):

    obj = context.object

    if not obj:
        return

    if obj.type != 'MESH':
        return

    if obj.get("quaildef") not in {
        "dmspritedef2",
        "dmspritedefinition"
    }:
        return

    palette_materials = get_material_palette_materials(obj)

    # ------------------------------------------------
    # Build palette lookup
    # ------------------------------------------------

    palette_lookup = {}

    props = None

    if obj.get("quaildef") == "dmspritedef2":
        props = obj.quail_dmspritedef2

    elif obj.get("quaildef") == "dmspritedefinition":
        props = obj.quail_dmspritedefinition

    if props and props.materialpalette:

        palette_props = props.materialpalette.quail_materialpalette

        for item in palette_props.materials:

            if not item.material:
                continue

            parsed = parse_variation_tag(item.material.name)

            if not parsed:
                continue

            # ----------------------------------------
            # BODY + CLOAK
            # ----------------------------------------

            if parsed["type"] in {"material", "cloak"}:

                key = (
                    parsed["prefix"],
                    parsed["face_index"],
                    parsed["material_number"],
                )

                palette_lookup[key] = item.material

            # ----------------------------------------
            # EYES
            # ----------------------------------------

            elif parsed["type"] == "eye":

                palette_lookup[("eye",)] = item.material

    face_index = self.face_index
    material_index = self.material_index
    eye_index = self.eye_index

    print("FACE:", face_index)
    print("MATERIAL:", material_index)
    print("EYE:", eye_index)

    for i, mat in enumerate(obj.data.materials):

        if not mat:
            continue

        parsed = parse_variation_tag(mat.name)

        if not parsed:
            print("SKIP:", mat.name)
            continue

        replacement = None

        # ------------------------------------------------
        # BODY MATERIALS
        # ------------------------------------------------

        if parsed["type"] == "material":

            # ----------------------------------------
            # Restore palette material
            # ----------------------------------------

            if material_index == 0:

                key = (
                    parsed["prefix"],
                    parsed["face_index"],
                    parsed["material_number"],
                )

                replacement = palette_lookup.get(key)

                if replacement:
                    print("RESTORE:", mat.name, "->", replacement.name)
                    obj.data.materials[i] = replacement

                continue

            # ----------------------------------------
            # External variation
            # ----------------------------------------

            target_tag = (
                f"{parsed['prefix']}"
                f"{material_index:02d}"
                f"{face_index}"
                f"{parsed['material_number']}"
                "_MDF"
            )

        # ------------------------------------------------
        # CLOAKS
        # ------------------------------------------------

        elif parsed["type"] == "cloak":

            if material_index == 0:

                key = (
                    parsed["prefix"],
                    parsed["face_index"],
                    parsed["material_number"],
                )

                replacement = palette_lookup.get(key)

                if replacement:
                    print("RESTORE:", mat.name, "->", replacement.name)
                    obj.data.materials[i] = replacement

                continue

            target_tag = (
                "CLK"
                f"{material_index:02d}"
                f"{face_index}"
                f"{parsed['material_number']}"
                "_MDF"
            )

        # ------------------------------------------------
        # EYES
        # ------------------------------------------------

        elif parsed["type"] == "eye":

            if eye_index == 0:

                replacement = palette_lookup.get(("eye",))

                if replacement:
                    print("RESTORE:", mat.name, "->", replacement.name)
                    obj.data.materials[i] = replacement

                continue

            target_tag = (
                f"{parsed['family']}"
                f"{eye_index:03d}"
                "_MDF"
            )

        else:
            continue

        print(mat.name, "->", target_tag)

        # ------------------------------------------------
        # Never swap TO materials already
        # on the palette
        # ------------------------------------------------

        if target_tag in palette_materials:
            print("ON PALETTE, SKIP:", target_tag)
            continue

        replacement = bpy.data.materials.get(target_tag)

        if not replacement:
            print("NOT FOUND:", target_tag)
            continue

        print("SWAP:", mat.name, "->", replacement.name)

        obj.data.materials[i] = replacement

    obj.data.update()

# =========================================================
# PROPERTIES
# =========================================================

class QuailVariationToolbarProperties(bpy.types.PropertyGroup):

    eye_index: IntProperty(
        name="Eye",
        default=0,
        min=0,
        max=999,
        update=update_variation_materials
    )

    face_index: IntProperty(
        name="Face",
        default=0,
        min=0,
        max=99,
        update=update_variation_materials
    )

    material_index: IntProperty(
        name="Material",
        default=0,
        min=0,
        max=99,
        update=update_variation_materials
    )

# =========================================================
# PANEL
# =========================================================

class VIEW3D_PT_quail_material_variations(bpy.types.Panel):
    bl_label = "Material Variations"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Quail"

    @classmethod
    def poll(cls, context):

        obj = context.object

        if not obj:
            return False

        return obj.get("quaildef") in {
            "dmspritedef2",
            "dmspritedefinition"
        }

    def draw(self, context):

        layout = self.layout
        scene = context.scene
        props = scene.quail_variation_toolbar

        row = layout.row(align=True)
        row.prop(props, "face_index")

        row = layout.row(align=True)
        row.prop(props, "material_index")

        row = layout.row(align=True)
        row.prop(props, "eye_index")

# REGISTER

def register():

    bpy.types.Scene.quail_variation_toolbar = PointerProperty(
        type=QuailVariationToolbarProperties
    )

def unregister():

    del bpy.types.Scene.quail_variation_toolbar