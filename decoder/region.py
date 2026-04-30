# pyright: basic, reportGeneralTypeIssues=false, reportAttributeAccessIssue=false

import bpy
import mathutils
from .context import Context
from ..wce.region import region

def decode_region(ctx: Context, reg: region) -> str:

    # ------------------------------------------------
    # Create object
    # ------------------------------------------------
    obj = bpy.data.objects.new(reg.tag, None)
    obj.empty_display_type = 'SPHERE'
    obj['quaildef'] = 'region'

    props = obj.quail_region

    # ------------------------------------------------
    # FLAGS + VALUES
    # ------------------------------------------------

    # Sphere
    props.has_sphere = reg.sphere is not None

    if props.has_sphere:
        props.sphere_x, props.sphere_y, props.sphere_z, props.sphere_r = reg.sphere
        obj.location = mathutils.Vector((props.sphere_x, props.sphere_y, props.sphere_z))
        obj.empty_display_size = props.sphere_r

    # Reverb
    props.has_reverbvolume = reg.reverbvolume is not None
    props.reverbvolume = reg.reverbvolume if reg.reverbvolume is not None else 0.0

    props.has_reverboffset = reg.reverboffset is not None
    props.reverboffset = reg.reverboffset if reg.reverboffset is not None else 0

    # Fog / lighting
    props.regionfog = bool(reg.regionfog)
    props.gouraud2 = bool(reg.gourand2)

    # Visibility
    props.encodedvisibility = bool(reg.encodedvisibility)
    props.vislistbytes = bool(reg.vislistbytes)

    # Sprite
    props.has_sprite = reg.sprite is not None
    props.sprite = reg.sprite if reg.sprite else ""

    # Misc
    props.userdata = reg.userdata

    # ------------------------------------------------
    # VISLISTS (store raw, like your old system but cleaner)
    # ------------------------------------------------
    while len(props.vislists) > 0:
        props.vislists.remove(0)

    for vis in reg.visiblelists:
        item = props.vislists.add()
        item.range = " ".join(vis.range)

    # ------------------------------------------------
    # VISNODES
    # ------------------------------------------------
    while len(props.visnodes) > 0:
        props.visnodes.remove(0)

    for vn in reg.visnodes:
        node = props.visnodes.add()

        node.normal_x = vn.vnormalabcd[0]
        node.normal_y = vn.vnormalabcd[1]
        node.normal_z = vn.vnormalabcd[2]
        node.normal_w = vn.vnormalabcd[3]

        node.vislistindex = vn.vislistindex
        node.fronttree = vn.fronttree
        node.backtree = vn.backtree

    obj.parent = ctx.parent

    # ----------------------------------------
    # Prefer REGIONS collection if it exists
    # ----------------------------------------
    target_collection = None

    if hasattr(ctx, "region_collection") and ctx.region_collection:
        target_collection = ctx.region_collection
    else:
        target_collection = ctx.collection

    target_collection.objects.link(obj)

    return ""