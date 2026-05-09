# pyright: basic, reportGeneralTypeIssues=false
# reportAttributeAccessIssue=false, reportOptionalMemberAccess=false

import bpy
from bpy.props import PointerProperty


# ----------------------------------------------------------
# Property Group
# ----------------------------------------------------------

class QuailParticleBlitProperties(bpy.types.PropertyGroup):

    sourceblit: PointerProperty(
        name="Source Blit",
        type=bpy.types.Object
    )


# ----------------------------------------------------------
# Panel
# ----------------------------------------------------------

def draw_particleblit_in_transform(self, context):

    obj = context.object

    if not obj:
        return

    if obj.get("quaildef") != "particleblit":
        return

    layout = self.layout
    props = obj.quail_particleblit

    box = layout.box()

    box.label(text="PARTICLE BLIT")

    # --------------------------------------------------
    # Source Blit
    # --------------------------------------------------

    box.prop(props, "sourceblit")


# ----------------------------------------------------------
# Register
# ----------------------------------------------------------

def register():

    bpy.types.Object.quail_particleblit = PointerProperty(
        type=QuailParticleBlitProperties
    )

    bpy.types.OBJECT_PT_transform.prepend(
        draw_particleblit_in_transform
    )


def unregister():

    bpy.types.OBJECT_PT_transform.remove(
        draw_particleblit_in_transform
    )

    del bpy.types.Object.quail_particleblit