import bpy
from ..wce.polyhedrondefinition import polyhedrondefinition


def encode_polyhedrondefinition(parser, obj) -> str:

    if obj.get("quaildef") != "polyhedrondefinition":
        return ""

    props = obj.quail_polyhedrondefinition

    # ------------------------------------------------
    # Create WCE object
    # ------------------------------------------------
    wce_poly = polyhedrondefinition()

    # -------------------------
    # Tag
    # -------------------------
    wce_poly.tag = obj.name

    # -------------------------
    # Bounding Radius
    # -------------------------
    wce_poly.boundingradius = float(props.boundingradius)

    # -------------------------
    # Scale Factor
    # -------------------------
    if props.has_scalefactor:
        wce_poly.scalefactor = float(props.scalefactor)
    else:
        wce_poly.scalefactor = None

    # ------------------------------------------------
    # Mesh Data (Vertices + Faces)
    # ------------------------------------------------
    if obj.type != 'MESH':
        parser.polyhedrondefinitions[wce_poly.tag] = wce_poly
        return ""

    mesh = obj.data

    # Ensure evaluated mesh (modifiers applied if needed)
    mesh.calc_loop_triangles()

    # -------------------------
    # Vertices
    # -------------------------
    wce_poly.vertices = []

    for v in mesh.vertices:
        vert = polyhedrondefinition.xyz()
        vert.xyz = (float(v.co.x), float(v.co.y), float(v.co.z))
        wce_poly.vertices.append(vert)

    # -------------------------
    # Faces
    # -------------------------
    wce_poly.faces = []

    for poly in mesh.polygons:
        face = polyhedrondefinition.vertexlist()

        # IMPORTANT:
        # WCE expects string indices
        face.vertexlist = [str(v_idx) for v_idx in poly.vertices]

        wce_poly.faces.append(face)

    # ------------------------------------------------
    # Store in parser
    # ------------------------------------------------
    parser.polyhedrondefinitions[wce_poly.tag] = wce_poly

    return ""