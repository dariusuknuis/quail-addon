import bpy
from ..wce.sprite3ddef import sprite3ddef
from ..common.rendermethod import build_rendermethod_string


def encode_sprite3ddef(parser, obj) -> str:

    if obj.get("quaildef") != "sprite3ddef":
        return ""

    # ------------------------------------------------
    # Create WCE object
    # ------------------------------------------------

    wce_sprite = sprite3ddef()

    # -------------------------
    # Tag
    # -------------------------
    wce_sprite.tag = obj.name

    # -------------------------
    # Defaults
    # -------------------------
    wce_sprite.enablegouraud2 = 0
    wce_sprite.centeroffset = None
    wce_sprite.boundingradius = None

    # ------------------------------------------------
    # Mesh Data
    # ------------------------------------------------

    if obj.type != 'MESH':
        parser.sprite3ddefs[wce_sprite.tag] = wce_sprite
        return ""

    mesh = obj.data
    mesh.calc_loop_triangles()

    # -------------------------
    # Vertices
    # -------------------------

    wce_sprite.vertices = []

    for v in mesh.vertices:
        vert = sprite3ddef.xyz()
        vert.xyz = (float(v.co.x), float(v.co.y), float(v.co.z))
        wce_sprite.vertices.append(vert)

    # -------------------------
    # BSP Nodes (1 face = 1 node)
    # -------------------------

    wce_sprite.bspnodes = []

    for poly in mesh.polygons:

        node_wrapper = sprite3ddef.bspnode()
        node = node_wrapper.bspnode

        # ----------------------------------------
        # NORMALABCD (unused → NULL)
        # ----------------------------------------
        node.normalabcd = None

        # ----------------------------------------
        # Vertex list
        # ----------------------------------------
        indices = list(poly.vertices)
        node.vertexlist = [str(len(indices))] + [str(i) for i in indices]

        # ----------------------------------------
        # Material / RenderInfo
        # ----------------------------------------
        mat = None
        if obj.data.materials and poly.material_index < len(obj.data.materials):
            mat = obj.data.materials[poly.material_index]

        if mat and mat.get("quaildef") == "renderinfo":

            props = mat.quail_renderinfo

            # ----------------------------------------
            # RenderMethod
            # ----------------------------------------
            node.rendermethod = build_rendermethod_string(props)

            # ----------------------------------------
            # RenderInfo block
            # ----------------------------------------
            ri = node.renderinfo

            # PEN
            ri.pen = props.pen if props.has_pen else None

            # Brightness / Ambient
            ri.brightness = props.brightness if props.has_brightness else None
            ri.scaledambient = props.scaledambient if props.has_scaledambient else None

            # SimpleSprite
            if props.has_simplesprite and props.simplespritetag and props.simplespritetag != "NONE":
                ri.simplespriteinst.simplespritetag = props.simplespritetag
            else:
                ri.simplespriteinst.simplespritetag = None

            ri.simplespriteinst.simplespritehaveskipframes = 1 if props.simplespritehaveskipframes else 0
            ri.simplespriteinst.simplespriteskipframes = 1 if props.simplespriteskipframes else 0

            # Two-sided
            ri.twosided = 1 if props.twosided else 0

        else:
            # ----------------------------------------
            # Fallback (no renderinfo material)
            # ----------------------------------------
            node.rendermethod = ""

            ri = node.renderinfo
            ri.pen = None
            ri.brightness = None
            ri.scaledambient = None
            ri.simplespriteinst.simplespritetag = None
            ri.simplespriteinst.simplespritehaveskipframes = 0
            ri.simplespriteinst.simplespriteskipframes = 0
            ri.twosided = 0

        # ----------------------------------------
        # UV fields (not implemented)
        # ----------------------------------------
        ri.uvorigin = None
        ri.uaxis = None
        ri.vaxis = None
        ri.uvs = []

        # ----------------------------------------
        # Trees
        # ----------------------------------------
        node.fronttree = 0
        node.backtree = 0

        wce_sprite.bspnodes.append(node_wrapper)

    # ------------------------------------------------
    # Sphere list (unused)
    # ------------------------------------------------
    wce_sprite.spherelist.definition = ""
    wce_sprite.spherelist.scalefactor = None

    # ------------------------------------------------
    # Store
    # ------------------------------------------------
    parser.sprite3ddefs[wce_sprite.tag] = wce_sprite

    return ""