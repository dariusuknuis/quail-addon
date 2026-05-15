# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false


import bpy
from bpy.props import PointerProperty, BoolProperty, IntProperty, FloatProperty, FloatVectorProperty, EnumProperty
from ...common import state
from ...common.s3dparticle import apply_particlecloud_settings, apply_particlecloud_blit, apply_particlecloud_visuals

def update_particlecloud_lifespan(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = self.id_data

    if not obj:
        return

    if obj.get("quaildef") != "particleclouddef":
        return

    apply_particlecloud_settings(obj)

    # ------------------------------------------------
    # Extend scene end frame
    # ------------------------------------------------

    fps = bpy.context.scene.render.fps

    lifespan_seconds = max(
        self.lifespan / 1000.0,
        0.001
    )

    lifetime_frames = max(
        lifespan_seconds * fps,
        1.0
    )

    bpy.context.scene.frame_end = int(
        lifetime_frames
    )

def update_particlecloud(self, context):

    if state.QUAIL_UPDATING:
        return

    obj = self.id_data

    if not obj:
        return

    if obj.get("quaildef") != "particleclouddef":
        return

    apply_particlecloud_blit(obj)

    apply_particlecloud_settings(obj)

    apply_particlecloud_visuals(obj)

# =========================================================
# PROPERTY GROUP
# =========================================================

class QuailParticleCloudDefProperties(bpy.types.PropertyGroup):

    # --------------------------------------------------
    # Core
    # --------------------------------------------------

    blittag: PointerProperty(
        name="BlitSprite",
        type=bpy.types.Object,
        poll=lambda self, obj: obj.get("quaildef") == "blitspritedef",
         update=update_particlecloud
    )

    particletype: IntProperty(name="Particle Type")
    movement: EnumProperty(
        name="Movement",
        items=[
            ('BOX', "BOX", ""),
            ('SPHERE', "SPHERE", ""),
            ('PLANE', "PLANE", ""),
            ('STREAM', "STREAM", ""),
            ('DISK', "DISK", ""),
        ],
        update=update_particlecloud
    )

    size: IntProperty(name="Size", update=update_particlecloud)
    gravity: FloatProperty(name="Gravity", update=update_particlecloud)

    spawnnormal: FloatVectorProperty(
        name="Spawn Normal",
        subtype='XYZ',
        size=3,
        update=update_particlecloud
    )

    duration: IntProperty(name="Duration", update=update_particlecloud)

    spawnradius: FloatProperty(name="Spawn Radius", update=update_particlecloud)

    spawnangle: FloatProperty(name="Spawn Angle", update=update_particlecloud)

    lifespan: IntProperty(name="Lifespan", update=update_particlecloud_lifespan)

    spawnvelocitymultiplier: FloatProperty(
        name="Velocity Multiplier",
        update=update_particlecloud
    )

    spawnvelocity: FloatVectorProperty(
        name="Spawn Velocity",
        subtype='XYZ',
        size=3,
        update=update_particlecloud
    )

    spawnrate: IntProperty(name="Spawn Rate", update=update_particlecloud)

    spawnscale: FloatProperty(name="Spawn Scale", update=update_particlecloud)

    tint: FloatVectorProperty(
        name="Tint",
        subtype='COLOR',
        size=4,
        min=0.0,
        max=1.0,
        update=update_particlecloud
    )

    # --------------------------------------------------
    # Nullable Boxes
    # --------------------------------------------------

    has_spawnbox: BoolProperty(name="Spawn Box")

    spawnboxmin: FloatVectorProperty(
        name="Spawn Box Min",
        subtype='XYZ',
        size=3
    )

    spawnboxmax: FloatVectorProperty(
        name="Spawn Box Max",
        subtype='XYZ',
        size=3
    )

    has_box: BoolProperty(name="Box")

    boxmin: FloatVectorProperty(
        name="Box Min",
        subtype='XYZ',
        size=3
    )

    boxmax: FloatVectorProperty(
        name="Box Max",
        subtype='XYZ',
        size=3
    )

    # --------------------------------------------------
    # Flags
    # --------------------------------------------------

    usesprite: BoolProperty(name="Use Sprite")
    free: BoolProperty(name="Free")
    collision: BoolProperty(name="Collision")
    respawn: BoolProperty(name="Respawn")

    viewrelx: BoolProperty(name="View Rel X")
    viewrely: BoolProperty(name="View Rel Y")
    viewrelz: BoolProperty(name="View Rel Z")

    viewwarp: BoolProperty(name="View Warp")

    brownian: BoolProperty(name="Brownian", update=update_particlecloud)
    fade: BoolProperty(name="Fade")

    boundingbox: BoolProperty(name="Bounding Box")
    updatebbox: BoolProperty(name="Update BBox")

    pointgravity: BoolProperty(name="Point Gravity")
    gravityflag: BoolProperty(name="Gravity Flag")

    freedef: BoolProperty(name="Free Def")

    objectrelative: BoolProperty(name="Object Relative")
    parentobjrelative: BoolProperty(name="Parent Object Relative")

    spawnscalerelative: BoolProperty(name="Spawn Scale Relative")

    hidewithspawnobject: BoolProperty(
        name="Hide With Spawn Object"
    )


# =========================================================
# PANEL
# =========================================================

def draw_particleclouddef_in_transform(self, context):

    obj = context.object

    if not obj:
        return

    if obj.get("quaildef") != "particleclouddef":
        return

    layout = self.layout

    props = obj.quail_particleclouddef

    box = layout.box()

    box.label(text="PARTICLECLOUDDEF")

    # --------------------------------------------------
    # Core
    # --------------------------------------------------

    box.prop(props, "blittag")

    box.prop(props, "particletype")

    box.prop(props, "movement")

    box.prop(props, "size")

    box.prop(props, "gravity")

    box.prop(props, "spawnnormal")

    box.prop(props, "duration")

    box.prop(props, "spawnradius")

    box.prop(props, "spawnangle")

    box.prop(props, "lifespan")

    box.prop(props, "spawnvelocitymultiplier")

    box.prop(props, "spawnvelocity")

    box.prop(props, "spawnrate")

    box.prop(props, "spawnscale")

    box.prop(props, "tint")

    # --------------------------------------------------
    # Spawn Box
    # --------------------------------------------------

    box.prop(props, "has_spawnbox")

    if props.has_spawnbox:

        row = box.row(align=True)
        row.prop(props, "spawnboxmin")

        row = box.row(align=True)
        row.prop(props, "spawnboxmax")

    # --------------------------------------------------
    # Box
    # --------------------------------------------------

    box.prop(props, "has_box")

    if props.has_box:

        row = box.row(align=True)
        row.prop(props, "boxmin")

        row = box.row(align=True)
        row.prop(props, "boxmax")

    # --------------------------------------------------
    # Flags
    # --------------------------------------------------

    box.label(text="Flags")

    box.prop(props, "usesprite")
    box.prop(props, "free")
    box.prop(props, "collision")
    box.prop(props, "respawn")

    box.prop(props, "viewrelx")
    box.prop(props, "viewrely")
    box.prop(props, "viewrelz")

    box.prop(props, "viewwarp")

    box.prop(props, "brownian")
    box.prop(props, "fade")

    box.prop(props, "boundingbox")
    box.prop(props, "updatebbox")

    box.prop(props, "pointgravity")
    box.prop(props, "gravityflag")

    box.prop(props, "freedef")

    box.prop(props, "objectrelative")
    box.prop(props, "parentobjrelative")

    box.prop(props, "spawnscalerelative")

    box.prop(props, "hidewithspawnobject")


# =========================================================
# REGISTER
# =========================================================

def register():

    bpy.types.Object.quail_particleclouddef = PointerProperty(
        type=QuailParticleCloudDefProperties
    )

    bpy.types.OBJECT_PT_transform.prepend(
        draw_particleclouddef_in_transform
    )


def unregister():

    bpy.types.OBJECT_PT_transform.remove(
        draw_particleclouddef_in_transform
    )

    del bpy.types.Object.quail_particleclouddef