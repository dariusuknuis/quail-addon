# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from ..wce.wce import wce
from typing import Optional
from ..logger.error import error
from .context import Context
import os

def gather_export_objects(root_objects):
    visited = set()
    stack = list(root_objects)

    def add(obj):
        if obj and obj not in visited:
            stack.append(obj)

    while stack:
        obj = stack.pop()

        if obj in visited:
            continue

        visited.add(obj)

        # ----------------------------------------
        # Children
        # ----------------------------------------
        for child in obj.children:
            add(child)

        # ----------------------------------------
        # References (your quail system)
        # ----------------------------------------
        qdef = obj.get("quaildef")

        if qdef == "dmspritedef2":
            props = obj.quail_dmspritedef2
            add(props.materialpalette)

        elif qdef == "dmspritedefinition":
            props = obj.quail_dmspritedefinition
            add(props.materialpalette)

    return visited


def wce_encode(folder_path: str, context, selected_only: bool) -> str:

    # ------------------------------------------------
    # Setup parser (same class as decode)
    # ------------------------------------------------
    parser = wce(folder_path)

    errors = []

    # ------------------------------------------------
    # Build root set
    # ------------------------------------------------
    if selected_only:
        root_objects = list(context.selected_objects)
    else:
        root_objects = list(bpy.context.scene.objects)

    # ------------------------------------------------
    # Gather dependency graph
    # ------------------------------------------------
    export_objects = gather_export_objects(root_objects)

    print("Export set:")
    for obj in export_objects:
        print("  ", obj.name, obj.get("quaildef"))

    # ------------------------------------------------
    # Gather Blender objects by type (FILTERED SET)
    # ------------------------------------------------
    actordefs = []
    simplesprites = []
    materialdefs = []
    materialpalettes = []
    polyhedrons = []
    dmsprite_defs = []
    dmsprite2_defs = []
    hierarchicalsprites = []
    eqgmodels = []
    eqgters = []
    eqganis = []

    for obj in export_objects:

        qdef = obj.get("quaildef")

        if not qdef:
            continue

        if qdef == "actordef":
            actordefs.append(obj)

        elif qdef == "hierarchicalspritedef":
            hierarchicalsprites.append(obj)

        elif qdef == "dmspritedefinition":
            dmsprite_defs.append(obj)

        elif qdef == "dmspritedef2":
            dmsprite2_defs.append(obj)

        elif qdef == "polyhedrondefinition":
            polyhedrons.append(obj)

        elif qdef == "materialpalette":
            materialpalettes.append(obj)

        elif qdef == "materialdefinition":
            materialdefs.append(obj)

        elif qdef == "simplespritedef":
            simplesprites.append(obj)

        elif qdef == "eqgmodeldef":
            eqgmodels.append(obj)

        elif qdef == "eqgterdef":
            eqgters.append(obj)

        elif qdef == "eqganidef":
            eqganis.append(obj)

    # ------------------------------------------------
    # Encode (order matters!)
    # ------------------------------------------------

    for obj in actordefs:
        err = encode_actordef(parser, obj)
        if err:
            errors.append(err)

    # for obj in hierarchicalsprites:
    #     err = encode_hierarchicalspritedef(parser, obj)
    #     if err:
    #         errors.append(err)

    # for obj in dmsprite_defs:
    #     err = encode_dmspritedefinition(parser, obj)
    #     if err:
    #         errors.append(err)

    # for obj in dmsprite2_defs:
    #     err = encode_dmspritedef2(parser, obj)
    #     if err:
    #         errors.append(err)

    # for obj in polyhedrons:
    #     err = encode_polyhedrondefinition(parser, obj)
    #     if err:
    #         errors.append(err)

    # for obj in materialpalettes:
    #     err = encode_materialpalette(parser, obj)
    #     if err:
    #         errors.append(err)

    # for obj in materialdefs:
    #     err = encode_materialdefinition(parser, obj)
    #     if err:
    #         errors.append(err)

    # for obj in simplesprites:
    #     err = encode_simplespritedef(parser, obj)
    #     if err:
    #         errors.append(err)

    # for obj in eqgters:
    #     err = encode_eqgterdef(parser, obj)
    #     if err:
    #         errors.append(err)

    # for obj in eqgmodels:
    #     err = encode_eqgmodeldef(parser, obj)
    #     if err:
    #         errors.append(err)

    # for obj in eqganis:
    #     err = encode_eqganidef(parser, obj)
    #     if err:
    #         errors.append(err)

    # ------------------------------------------------
    # Write _root.wce
    # ------------------------------------------------
    root_path = os.path.join(folder_path, "_root.wce")

    print("Writing:", root_path)

    with open(root_path, "w") as w:
        err = parser.write(w)
        if err:
            return err

    # ------------------------------------------------
    # Return errors if any
    # ------------------------------------------------
    if errors:
        return "\n".join(errors)

    return ""