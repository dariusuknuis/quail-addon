import bpy
from ..wce.wce import wce
from typing import Optional


def wce_import(path:str):
    parser = wce(path)
    r = open(path+"/_root.wce", "r")
    parser.parse_definitions(path, r)