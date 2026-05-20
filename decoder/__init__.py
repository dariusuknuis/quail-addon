# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from ..wce.wce import wce
from typing import Optional
from .worlddef import decode_worlddef
from .globalambientlightdef import decode_globalambientlightdef
from .actordef import decode_actordef
from .actorinst import decode_actorinst
from .simplespritedef import decode_simplespritedef
from .blitspritedef import decode_blitspritedef
from .materialdefinition import decode_materialdefinition
from .materialpalette import decode_materialpalette
from .polyhedrondefinition import decode_polyhedrondefinition
from .light import decode_light
from .zone import decode_zone
from .worldtree import decode_worldtree
from .region import decode_region
from .sprite3ddef import decode_sprite3ddef
from .particleclouddef import decode_particleclouddef
from .dmspritedefinition import decode_dmspritedefinition
from .dmspritedef2 import decode_dmspritedef2
from .track import decode_trackdefinition, decode_trackinstance, build_wld_animations, reset_track_cache
from .hierarchicalspritedef import decode_hierarchicalspritedef
from .eqgmodeldef import decode_eqgmodeldef
from .eqgterdef import decode_eqgterdef
from .eqganidef import decode_eqganidef
from ..logger.error import error
from .context import Context
from ..common import state
from ..common.region import resolve_region_visibility
from ..common.bsp import build_bsp
import os

def find_assets_root(start_path: str) -> str | None:
    """Walk upward to find a directory containing 'assets'"""
    current = os.path.abspath(start_path)

    # If a file was passed, start from its directory
    if os.path.isfile(current):
        current = os.path.dirname(current)

    while True:
        assets_path = os.path.join(current, "assets")
        if os.path.isdir(assets_path):
            return assets_path

        parent = os.path.dirname(current)
        if parent == current:
            # Reached filesystem root
            return None

        current = parent

def ensure_material_fake_users():

    for mat in bpy.data.materials:

        if mat.get("quaildef") != "materialdefinition":
            continue

        # If nothing is using it, preserve it
        if mat.users == 0:
            mat.use_fake_user = True

def wce_decode(path: str, parent_collection=None):

    state.QUAIL_UPDATING = True

    reset_track_cache()

    # ------------------------------------------------
    # Ensure scene camera exists
    # ------------------------------------------------

    if not bpy.context.scene.camera:

        cam_data = bpy.data.cameras.new("Camera")

        cam_obj = bpy.data.objects.new(
            "Camera",
            cam_data
        )

        bpy.context.scene.collection.objects.link(
            cam_obj
        )

        cam_obj.location = (0.0, -6.0, 3.0)

        cam_obj.rotation_euler = (
            1.109319,
            0.0,
            0.0
        )

        bpy.context.scene.camera = cam_obj

        # ------------------------------------------------
        # Viewport camera settings
        # ------------------------------------------------

        for window in bpy.context.window_manager.windows:

            for area in window.screen.areas:

                if area.type != 'VIEW_3D':
                    continue

                for space in area.spaces:

                    if space.type != 'VIEW_3D':
                        continue

                    space.overlay.show_camera_passepartout = False
                    space.lock_camera = True

    if os.path.isfile(path) and path.lower().endswith(".wce"):
        # Single WCE file
        root_path = path
        base_dir = os.path.dirname(path)
        base_file_name = os.path.splitext(os.path.basename(path))[0]
    else:
        # Quail output directory
        base_dir = path
        root_path = os.path.join(path, "_root.wce")
        base_file_name = os.path.splitext(os.path.basename(path))[0]

    parser = wce(base_dir)
    with open(root_path, "r") as r:
        parser.parse_definitions(base_dir, r)

    assets = find_assets_root(root_path)

    if assets is None:
        raise RuntimeError(f"Could not locate 'assets' folder from {root_path}")

    parser.assets_path = assets

    print(f"Resolved assets path: {parser.assets_path}")

    if parent_collection and os.path.splitext(os.path.basename(path))[0] == parent_collection.name:
        base_collection = parent_collection
    else:
        base_collection = parent_collection.children.get(base_file_name) if parent_collection else None

        if not base_collection:
            base_collection = bpy.data.collections.new(base_file_name)

            if parent_collection:
                parent_collection.children.link(base_collection)
            else:
                bpy.context.scene.collection.children.link(base_collection)

    base_parent = None

    ctx = Context(parser, base_collection, base_parent)

    if not ctx.parser.bsp_root:
        build_bsp(ctx.parser)

    for _, worlddef in parser.worlddefs.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_worlddef(ctx, worlddef)
        if err:
            error(err)

    for _, globalambientlightdef in parser.globalambientlightdefs.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_globalambientlightdef(ctx, globalambientlightdef)
        if err:
            error(err)

    for _, spritedef in parser.simplespritedefs.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_simplespritedef(ctx, spritedef)
        if err:
            error(err)

    for _, blitspritedef in parser.blitspritedefs.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_blitspritedef(ctx, blitspritedef)
        if err:
            error(err)

    for _, materialdef in parser.materialdefinitions.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_materialdefinition(ctx, materialdef)
        if err:
            error(err)

    for _, materialpalette in parser.materialpalettes.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_materialpalette(ctx, materialpalette)
        if err:
            error(err)

    for _, polyhdef in parser.polyhedrondefinitions.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_polyhedrondefinition(ctx, polyhdef)
        if err:
            error(err)

    for _, particleclouddef in parser.particleclouddefs.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_particleclouddef(ctx, particleclouddef)
        if err:
            error(err)

    for _, sprite3ddef in parser.sprite3ddefs.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_sprite3ddef(ctx, sprite3ddef)
        if err:
            error(err)

    for _, dmspritedefinition in parser.dmspritedefinitions.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_dmspritedefinition(ctx, dmspritedefinition)
        if err:
            error(err)

    for _, dmspritedef2 in parser.dmspritedef2s.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_dmspritedef2(ctx, dmspritedef2)
        if err:
            error(err)

    for _, region in parser.regions.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_region(ctx, region)
        if err:
            error(err)

    resolve_region_visibility()

    for _, worldtree in parser.worldtrees.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_worldtree(ctx, worldtree)
        if err:
            error(err)

    for _, zone in parser.zones.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_zone(ctx, zone)
        if err:
            error(err)

    for _, light in parser.pointlights.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_light(ctx, light)
        if err:
            error(err)

    for _, trackdef in parser.trackdefinitions.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_trackdefinition(ctx, trackdef)
        if err:
            error(err)

    for _, trackinst in parser.trackinstances.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_trackinstance(ctx, trackinst)
        if err:
            error(err)

    for _, hierarchicalspritedef in parser.hierarchicalspritedefs.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_hierarchicalspritedef(ctx, hierarchicalspritedef)
        if err:
            error(err)

    build_wld_animations()

    for _, actordef in parser.actordefs.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_actordef(ctx, actordef)
        if err:
            error(err)

    for _, actorinst in parser.actorinsts.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_actorinst(ctx, actorinst)
        if err:
            error(err)

    for _, eqgmodel in parser.eqgmodeldefs.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_eqgmodeldef(ctx, eqgmodel, mathutils.Vector())
        if err:
            error(err)

    for _, eqgter in parser.eqgterdefs.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_eqgterdef(ctx, eqgter, mathutils.Vector())
        if err:
            error(err)

    for _, eqgani in parser.eqganidefs.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_eqganidef(ctx, eqgani)
        if err:
            error(err)

    organize_collections(parser, base_collection)

    ensure_material_fake_users()

    state.QUAIL_UPDATING = False

def organize_collections(parser, base_collection):

    # ------------------------------------------------
    # Build folder -> actordef collection lookup
    # ------------------------------------------------

    folder_to_collection = {}

    for actordef_tag in parser.actordefs.keys():

        folder = parser.folders.get(actordef_tag)

        if not folder:
            continue

        collection = bpy.data.collections.get(actordef_tag)

        if not collection:
            continue

        folder_to_collection[folder.lower()] = collection

    # ------------------------------------------------
    # Move supported quaildefs
    # ------------------------------------------------

    supported_defs = {
        "blitspritedef",
        "materialpalette",
        "particleclouddef",
        "particleblit",
    }

    for obj in bpy.data.objects:

        quaildef = obj.get("quaildef")

        if quaildef not in supported_defs:
            continue

        tag = obj.name

        # ------------------------------------------------
        # Particle blits inherit folder from parent cloud
        # ------------------------------------------------

        if quaildef == "particleblit":

            parent = obj.parent

            if not parent:
                continue

            folder = parser.folders.get(parent.name)

        else:

            folder = parser.folders.get(tag)

        if not folder:
            continue

        target_collection = folder_to_collection.get(
            folder.lower()
        )

        if not target_collection:
            continue

        # already linked
        if target_collection in obj.users_collection:
            continue

        # ------------------------------------------------
        # Link into target collection
        # ------------------------------------------------

        target_collection.objects.link(obj)

        # ------------------------------------------------
        # Remove from other collections
        # except scene root
        # ------------------------------------------------

        for col in list(obj.users_collection):

            if col == target_collection:
                continue

            try:
                col.objects.unlink(obj)
            except:
                pass