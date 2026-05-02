import bpy, math
from .context import Context
from ..wce.actorinst import actorinst

def decode_actorinst(ctx: Context, inst: actorinst) -> str:

    # ------------------------------------------------
    # Build tag FROM sprite
    # ------------------------------------------------
    sprite_tag = inst.sprite or "ACTOR"

    if sprite_tag.endswith("ACTORDEF"):
        inst.tag = sprite_tag.replace("ACTORDEF", "ACTORINST")
    else:
        inst.tag = f"{sprite_tag}_ACTORINST"

    name = inst.tag  # Blender object name = tag

    # ------------------------------------------------
    # Create object
    # ------------------------------------------------
    obj = bpy.data.objects.new(name, None)
    obj["quaildef"] = "actorinst"

    ctx.collection.objects.link(obj)

    props = obj.quail_actorinst

    if inst.dmrgbtrack:
        sprite_col = bpy.data.collections.get(sprite_tag)

        if not sprite_col:
            return f"actorinst refers to collection {sprite_tag} but not found"

        # find a mesh inside the collection
        src_obj = None
        for o in sprite_col.objects:
            if o.type == 'MESH':
                src_obj = o
                break

        if not src_obj:
            return f"No mesh found in {sprite_tag}"

        new_obj = src_obj.copy()
        new_obj.data = src_obj.data.copy()

        # ----------------------------------------
        # Naming + tagging
        # ----------------------------------------

        track_name = inst.dmrgbtrack or "RGBTRACK"

        new_obj.name = track_name
        new_obj.data.name = track_name
        new_obj["quaildef"] = "rgbdeformationtrackdef"

        ctx.collection.objects.link(new_obj)
        new_obj.parent = obj

        new_obj.lock_location = (True, True, True)
        new_obj.lock_rotation = (True, True, True)
        new_obj.lock_scale = (True, True, True)

        # new_obj.hide_select = True

        # ----------------------------------------
        # Get RGB track
        # ----------------------------------------

        rgb_track = ctx.parser.rgbdeformationtrackdefs.get(inst.dmrgbtrack)

        # ----------------------------------------
        # Populate RGBDEFORMATIONTRACKDEF props
        # ----------------------------------------

        if rgb_track:
            props.has_dmrgbtack = True
            track_props = new_obj.quail_rgbdeformationtrackdef

            track_props.tag = rgb_track.tag
            track_props.sleep = rgb_track.sleep
            track_props.data4 = rgb_track.data4
            track_props.usealpha = bool(rgb_track.usealpha)
            track_props.numframes = len(rgb_track.rgbdeformationframes)

        # ----------------------------------------
        # Create color attribute (frame 0 only)
        # ----------------------------------------

        mesh = new_obj.data
        frame_index = 0
        attr_name = f"rgbatrack_{frame_index:03d}"

        attr = mesh.attributes.new(
            name=attr_name,
            type='FLOAT_COLOR',
            domain='POINT'
        )

        # ----------------------------------------
        # Fill attribute from rgb track
        # ----------------------------------------

        if rgb_track and rgb_track.rgbdeformationframes:

            frame = rgb_track.rgbdeformationframes[0]

            count = min(len(mesh.vertices), len(frame.rgbas))

            for i in range(count):
                r, g, b, a = frame.rgbas[i].rgba

                attr.data[i].color = (
                    r / 255.0,
                    g / 255.0,
                    b / 255.0,
                    a / 255.0 if rgb_track.usealpha else 1.0
                )

        # ----------------------------------------
        # Assign material (copy + set attribute name)
        # ----------------------------------------

        if new_obj.material_slots:

            base_mat = new_obj.material_slots[0].material
            if base_mat:
                mat = base_mat.copy()

                for node in mat.node_tree.nodes:
                    if node.type == 'ATTRIBUTE':
                        node.attribute_name = attr_name

                new_obj.material_slots[0].material = mat

    else:
        # ------------------------------------------------
        # COLLECTION INSTANCE
        # ------------------------------------------------
        obj.instance_type = 'COLLECTION'

        sprite_col = bpy.data.collections.get(sprite_tag)
        if not sprite_col:
            return f"actorinst refers to collection {sprite_tag} but not found"

        obj.instance_collection = sprite_col

    props.sprite = sprite_col

    # ------------------------------------------------
    # Current Action
    # ------------------------------------------------
    if inst.currentaction is None:
        props.has_currentaction = False
        props.currentaction = ""
    else:
        props.has_currentaction = True
        props.currentaction = str(inst.currentaction)

    # ------------------------------------------------
    # Location
    # ------------------------------------------------
    if inst.location:
        props.has_location = True

        x, y, z, rz, ry, rx = inst.location

        # ADD THIS
        obj.location = (x, y, z)

        scale = (2 * math.pi) / 512.0
        obj.rotation_euler = (
            ry * scale,  # X
            rx * scale,  # Y
            rz * scale,  # Z
        )
    else:
        props.has_location = False

    # ------------------------------------------------
    # Optional fields
    # ------------------------------------------------
    if inst.boundingradius is not None:
        props.has_boundingradius = True
        props.boundingradius = inst.boundingradius
    else:
        props.has_boundingradius = False
        props.boundingradius = 1.0

    if inst.scalefactor is not None:
        props.has_scalefactor = True
        obj.scale = (inst.scalefactor,) * 3
    else:
        props.has_scalefactor = False

    if inst.sound is not None:
        props.has_sound = True
        props.sound = inst.sound
    else:
        props.has_sound = False

    if inst.active is not None:
        props.has_active = True
        props.active = inst.active
    else:
        props.has_active = False

    if inst.dmrgbtrack is not None:
        props.has_dmrgbtrack = True
        props.dmrgbtrack = inst.dmrgbtrack
    else:
        props.has_dmrgbtrack = False

    # ------------------------------------------------
    # Required
    # ------------------------------------------------
    props.spritevolumeonly = bool(inst.spritevolumeonly)

    props.sphere = inst.sphere
    props.sphereradius = inst.sphereradius

    props.useboundingbox = bool(inst.useboundingbox)

    props.userdata = inst.userdata or ""

    return ""