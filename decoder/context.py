from dataclasses import dataclass
from bpy.types import Object, Collection
from ..wce.wce import wce

@dataclass
class Context:
    parser:wce
    collection:Collection
    parent:Object