# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from ..wce.wce import wce
from typing import Optional
from ..logger.error import error
from .context import Context
import os

def wce_encode(path:str) -> str:
    # iterate every object in the scene
    for obj in bpy.context.scene.objects:
        print(f"object {obj.name}")
        if obj.type == 'EMPTY' and obj['quaildef'] == 'actordef':
            print(f"actordef {obj.name}")

    return "TODO"