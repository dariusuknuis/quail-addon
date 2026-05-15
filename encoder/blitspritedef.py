# pyright: basic, reportGeneralTypeIssues=false

import bpy

from ..wce.blitspritedef import blitspritedef
from ..common.rendermethod import build_rendermethod_string


def encode_blitspritedef(parser, obj) -> str:

    if obj.get("quaildef") != "blitspritedef":
        return ""

    props = obj.quail_blitspritedef

    wce_sprite = blitspritedef()

    # ------------------------------------------------
    # Tag
    # ------------------------------------------------

    wce_sprite.tag = obj.name

    # ------------------------------------------------
    # SimpleSprite
    # ------------------------------------------------

    wce_sprite.sprite = (
        props.simplespritetag
        if props.simplespritetag
        else ""
    )

    # ------------------------------------------------
    # Rendermethod
    # ------------------------------------------------

    wce_sprite.rendermethod = (
        build_rendermethod_string(props)
    )

    # ------------------------------------------------
    # Transparent
    # ------------------------------------------------

    wce_sprite.transparent = (
        1 if props.transparent else 0
    )

    # ------------------------------------------------
    # Store
    # ------------------------------------------------

    parser.blitspritedefs[
        wce_sprite.tag
    ] = wce_sprite

    return ""