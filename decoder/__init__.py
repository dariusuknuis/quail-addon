# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

from ..wce.wce import wce
from typing import Optional
from .actordef import decode_actordef
from .materialdefinition import decode_materialdefinition
from ..logger.error import error

def wce_decode(path:str):
    parser = wce(path)
    r = open(path+"/_root.wce", "r")
    parser.parse_definitions(path, r)

    for _, materialdef in parser.materialdefinitions.items():
        err = decode_materialdefinition(parser, materialdef)
        if err:
            error(err)

    for _, actordef in parser.actordefs.items():
        err = decode_actordef(parser, actordef)
        if err:
            error(err)