# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from ..wce.wce import wce
from typing import Optional
from .actordef import decode_actordef
from .materialdefinition import decode_materialdefinition
from .eqgmodeldef import decode_eqgmodeldef
from .eqgterdef import decode_eqgterdef
from ..logger.error import error
from .context import Context
import os

def wce_decode(path:str):
    parser = wce(path)
    r = open(path+"/_root.wce", "r")
    parser.parse_definitions(path, r)
    base_file_name = os.path.basename(path)
    base_collection = bpy.data.collections.new(base_file_name)
    bpy.context.scene.collection.children.link(base_collection)
    # base_file_name_no_ext = os.path.splitext(base_file_name)[0]
    base_parent = None

    ctx = Context(parser, base_collection, base_parent)

    for _, materialdef in parser.materialdefinitions.items():
        ctx.collection = base_collection
        ctx.parent = base_parent

        err = decode_materialdefinition(ctx, materialdef)
        if err:
            error(err)

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