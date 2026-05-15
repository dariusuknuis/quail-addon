# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false
# reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import BoolProperty, PointerProperty, IntProperty, EnumProperty, StringProperty, FloatProperty
from ...common.s3dmaterial import update_userdefined, update_rendermethod_node, update_transparent, update_simplesprite, sprite_items
from ...common import state

def update_blit_and_particle_trans(self, context):

    if state.QUAIL_UPDATING:
        return

    update_transparent(self, context)

    obj = self.id_data

    if not obj:
        return

    if obj.get("quaildef") != "blitspritedef":
        return

    propagate_particleblits(obj)

def update_blit_and_particle_ud(self, context):

    if state.QUAIL_UPDATING:
        return

    update_userdefined(self, context)

    obj = self.id_data

    if not obj:
        return

    if obj.get("quaildef") != "blitspritedef":
        return

    propagate_particleblits(obj)

def update_blit_and_particle_ss(self, context):

    if state.QUAIL_UPDATING:
        return

    update_simplesprite(self, context)

    obj = self.id_data

    if not obj:
        return

    if obj.get("quaildef") != "blitspritedef":
        return

    propagate_particleblits(obj)

def update_blit_and_particle_rm(self, context):

    if state.QUAIL_UPDATING:
        return

    print("UPDATE:", context.object.name if context.object else None)

    update_rendermethod_node(self, context)

    obj = self.id_data

    if not obj:
        return

    if obj.get("quaildef") != "blitspritedef":
        return

    propagate_particleblits(obj)

def propagate_particleblits(source_obj):

    if state.QUAIL_UPDATING:
        return

    print("PROPAGATE:", source_obj.name)

    if not source_obj:
        return

    source_props = source_obj.quail_blitspritedef

    for obj in bpy.data.objects:

        if obj.get("quaildef") != "particleblit":
            continue

        particle_props = obj.quail_particleblit

        if particle_props.sourceblit.name != source_obj.name:
            continue

        # ----------------------------------------
        # Copy property values
        # ----------------------------------------
        print("MATCH:", obj.name, particle_props.sourceblit.name)

        props = obj.quail_blitspritedef

        print(
            "COPY SIMPLESPRITE:",
            obj.name,
            "->",
            source_props.simplespritetag
        )

        if props.simplespritetag != source_props.simplespritetag:
            props.simplespritetag = source_props.simplespritetag

        if props.transparent_override != source_props.transparent_override:
            props.transparent_override = source_props.transparent_override

        if props.use_userdefined != source_props.use_userdefined:
            props.use_userdefined = source_props.use_userdefined

        if props.userdefined_index != source_props.userdefined_index:
            props.userdefined_index = source_props.userdefined_index

        if props.drawstyle != source_props.drawstyle:
            props.drawstyle = source_props.drawstyle

        if props.lighting != source_props.lighting:
            props.lighting = source_props.lighting

        if props.shading != source_props.shading:
            props.shading = source_props.shading

        if props.texture_index != source_props.texture_index:
            props.texture_index = source_props.texture_index

        if props.masked != source_props.masked:
            props.masked = source_props.masked

        if props.alphablend != source_props.alphablend:
            props.alphablend = source_props.alphablend

        if props.additive != source_props.additive:
            props.additive = source_props.additive

        if props.dynamic != source_props.dynamic:
            props.dynamic = source_props.dynamic

        if props.prelit != source_props.prelit:
            props.prelit = source_props.prelit

        if props.opacity != source_props.opacity:
            props.opacity = source_props.opacity

        if props.transparent != source_props.transparent:
            props.transparent = source_props.transparent

        # ----------------------------------------
        # Copy material node settings
        # but preserve Particle Tint
        # ----------------------------------------

        if not source_obj.data.materials:
            continue

        if not obj.data.materials:
            continue

        src_mat = source_obj.data.materials[0]
        dst_mat = obj.data.materials[0]

        if not src_mat.use_nodes or not dst_mat.use_nodes:
            continue

        src_nodes = src_mat.node_tree.nodes
        dst_nodes = dst_mat.node_tree.nodes

        src_group = None
        dst_group = None

        for n in src_nodes:
            if (
                n.type == 'GROUP' and
                n.node_tree and
                n.node_tree.name == "RENDERMETHOD"
            ):
                src_group = n
                break

        for n in dst_nodes:
            if (
                n.type == 'GROUP' and
                n.node_tree and
                n.node_tree.name == "RENDERMETHOD"
            ):
                dst_group = n
                break

        if not src_group or not dst_group:
            continue

        # # preserve tint
        # tint = dst_group.inputs["Particle Tint"].default_value[:]

        # # copy everything except tint
        # for inp in src_group.inputs:

        #     if inp.name == "Particle Tint":
        #         continue

        #     if inp.name not in dst_group.inputs:
        #         continue

        #     try:
        #         dst_group.inputs[inp.name].default_value = inp.default_value
        #     except:
        #         pass

        # dst_group.inputs["Particle Tint"].default_value = tint

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
        update=update_blit_and_particle_ss
    )

    # --------------------------------------------------
    # Transparency
    # --------------------------------------------------

    transparent_override: BoolProperty(
        name="Transparent Override",
        description="Force material to behave as fully transparent",
        default=False,
        update=update_blit_and_particle_trans
    )

    # --------------------------------------------------
    # Userdefined
    # --------------------------------------------------

    use_userdefined: BoolProperty(
        name="Userdefined",
        default=False,
        update=update_blit_and_particle_ud
    )

    userdefined_index: IntProperty(
        name="Userdefined Index",
        min=1,
        max=41,
        default=2,
        update=update_blit_and_particle_ud
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
        update=update_blit_and_particle_rm
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
        update=update_blit_and_particle_rm
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
        update=update_blit_and_particle_rm
    )

    # --------------------------------------------------
    # Texture Index
    # --------------------------------------------------

    texture_index: IntProperty(
        name="Texture",
        min=0,
        max=255,
        default=5,
        update=update_blit_and_particle_rm
    )

    # --------------------------------------------------
    # Toggles
    # --------------------------------------------------

    masked: BoolProperty(
        name="Masked Transparency",
        default=False,
        update=update_blit_and_particle_rm
    )

    alphablend: BoolProperty(
        name="Alpha Blend",
        default=False,
        update=update_blit_and_particle_rm
    )

    additive: BoolProperty(
        name="Additive",
        default=False,
        update=update_blit_and_particle_rm
    )

    dynamic: BoolProperty(
        name="Dynamic Lighting",
        default=False,
        update=update_blit_and_particle_rm
    )

    prelit: BoolProperty(
        name="Prelit",
        default=False,
        update=update_blit_and_particle_rm
    )

    opacity: FloatProperty(
        name="Opacity %",
        min=0.0,
        max=93.75,
        default=50.0,
        update=update_blit_and_particle_rm
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