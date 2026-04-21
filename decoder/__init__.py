# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from ..wce.wce import wce
from typing import Optional
from .actordef import decode_actordef
from .simplespritedef import decode_simplespritedef
from .materialdefinition import decode_materialdefinition
from .polyhedrondefinition import decode_polyhedrondefinition
from .dmspritedefinition import decode_dmspritedefinition
from .dmspritedef2 import decode_dmspritedef2
from .track import decode_trackdefinition, decode_trackinstance, build_wld_animations
from .hierarchicalspritedef import decode_hierarchicalspritedef
from .eqgmodeldef import decode_eqgmodeldef
from .eqgterdef import decode_eqgterdef
from .eqganidef import decode_eqganidef
from ..logger.error import error
from .context import Context
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

def wce_decode(path: str):

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

    base_collection = bpy.data.collections.new(base_file_name)
    bpy.context.scene.collection.children.link(base_collection)
    base_parent = None

    ctx = Context(parser, base_collection, base_parent)

    for _, spritedef in parser.simplespritedefs.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_simplespritedef(ctx, spritedef)
        if err:
            error(err)

    for _, materialdef in parser.materialdefinitions.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_materialdefinition(ctx, materialdef)
        if err:
            error(err)

    for _, polyhdef in parser.polyhedrondefinitions.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_polyhedrondefinition(ctx, polyhdef)
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