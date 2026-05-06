import bpy
from ..common import _add_group_socket, _get_group_io_sockets
import mathutils

ZONE_TYPE_ITEMS = [
    ('DR', "Dry", ""),
    ('WT', "Water", ""),
    ('LA', "Lava", ""),
    ('SL', "Slime", ""),
    ('VW', "Velious Water", ""),
    ('W2', "Water v2", ""),
    ('W3', "Water v3", ""),
]

def apply_zone_rules(obj):

    props = obj.quail_zone

    name = obj.name
    userdata = props.userdata.strip()

    # ----------------------------------------
    # Prefer USERDATA if present
    # ----------------------------------------
    source = userdata if userdata != "" else name

    if len(source) < 2:
        return

    # -------------------------
    # TYPE (first 2 chars)
    # -------------------------
    prefix = source[:2]

    if prefix in {'DR','WT','LA','SL','VW','W2','W3'}:
        props.zone_type = prefix

    # -------------------------
    # PvP (3rd char)
    # -------------------------
    if len(source) >= 3:
        props.is_pvp = (source[2] == 'P')

    # -------------------------
    # TP (4-5)
    # -------------------------
    if len(source) >= 5:
        props.has_tp = (source[3:5] == 'TP')

    # -------------------------
    # Slippery
    # -------------------------
    props.slippery = "_S_" in source

ZONE_MAT_MAP = {
    "DR": ("DRY_ZONE",     0xFFFFFF, 0.00),
    "WT": ("WATER_ZONE",   0x0F2417, 0.75),
    "LA": ("LAVA_ZONE",    0x570101, 0.75),
    "SL": ("SLIME_ZONE",   0x2A2A01, 0.75),
    "VW": ("V_WATER_ZONE", 0x01012D, 0.75),
    "W2": ("WATER2_ZONE",  0x1E2026, 0.75),
    "W3": ("WATER3_ZONE",  0xFFFFFF, 0.10),
}


def get_zone_source(obj):
    props = obj.quail_zone
    userdata = props.userdata.strip()
    return userdata if userdata else obj.name


def get_zone_overlay_codes(source):
    codes = []

    if len(source) >= 3 and source[2] == "P":
        codes.append("PVP")

    if len(source) >= 5 and source[3:5] == "TP":
        codes.append("TP")

    if "_S_" in source:
        codes.append("SLP")

    return codes

def ensure_pvp_node_group():
    name = "PVP_ZONE"
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]
    ng, nodes, links = bpy.data.node_groups.new(name, 'ShaderNodeTree'), None, None
    ng = bpy.data.node_groups[name]
    nodes, links = ng.nodes, ng.links

    # Group I/O
    inp = nodes.new('NodeGroupInput');  inp.location=(-700,225)
    out = nodes.new('NodeGroupOutput'); out.location=( 800,330)
    _add_group_socket(ng, 'Shader', 'NodeSocketShader', is_input=True)
    _add_group_socket(ng, 'Shader', 'NodeSocketShader', is_input=False)

    # Wave→Ramp→Mix #1
    w1 = nodes.new('ShaderNodeTexWave');     w1.location=(-335,590)
    w1.wave_type='BANDS'; w1.bands_direction='DIAGONAL'; w1.wave_profile='SIN'
    for k,v in (("Scale",5.0),("Distortion",12.0),("Detail",2.0),
                ("Detail Scale",1.0),("Detail Roughness",0.75)):
        w1.inputs[k].default_value = v

    r1 = nodes.new('ShaderNodeValToRGB');  r1.location=(-125,440)
    r1.color_ramp.interpolation = 'CONSTANT'
    r1.color_ramp.elements[0].position = 0.0
    r1.color_ramp.elements[0].color    = (1,1,1,1)
    r1.color_ramp.elements[1].position = 0.2
    r1.color_ramp.elements[1].color    = (0,0,0,1)

    m1 = nodes.new('ShaderNodeMixShader');  m1.location=(270,300)

    # Wave→Ramp→Mix #2
    w2 = nodes.new('ShaderNodeTexWave');     w2.location=(-35,800)
    w2.wave_type='BANDS'; w2.bands_direction='DIAGONAL'; w2.wave_profile='SIN'
    for attr in ("Scale","Distortion","Detail","Detail Scale","Detail Roughness"):
        w2.inputs[attr].default_value = w1.inputs[attr].default_value

    r2 = nodes.new('ShaderNodeValToRGB');  r2.location=(210,550)
    r2.color_ramp.interpolation = 'CONSTANT'
    r2.color_ramp.elements[0].position = 0.0
    r2.color_ramp.elements[0].color    = (1,1,1,1)
    r2.color_ramp.elements[1].position = 0.1
    r2.color_ramp.elements[1].color    = (0,0,0,1)

    m2 = nodes.new('ShaderNodeMixShader');  m2.location=(520,355)

    # Two colored Principled BSDFs
    p1 = nodes.new('ShaderNodeBsdfPrincipled'); p1.location=(-125,110)
    p1.inputs["Base Color"].default_value = (0x26/255,0x07/255,0x51/255,1)
    p1.inputs["Alpha"].default_value      = 1.0

    p2 = nodes.new('ShaderNodeBsdfPrincipled'); p2.location=(200,110)
    p2.inputs["Base Color"].default_value = (0x6D/255,0x03/255,0x0F/255,1)
    p2.inputs["Alpha"].default_value      = 1.0

    # internal links
    in_sock, out_sock = _get_group_io_sockets(ng)
    links.new(w1.outputs["Fac"], r1.inputs["Fac"])
    links.new(r1.outputs["Color"], m1.inputs["Fac"])

    links.new(w2.outputs["Fac"], r2.inputs["Fac"])
    links.new(r2.outputs["Color"], m2.inputs["Fac"])

    links.new(in_sock["Shader"], m1.inputs[1])
    links.new(p1.outputs["BSDF"],   m1.inputs[2])

    links.new(m1.outputs["Shader"], m2.inputs[1])
    links.new(p2.outputs["BSDF"],   m2.inputs[2])

    links.new(m2.outputs["Shader"], out_sock["Shader"])
    return ng

def ensure_tp_node_group():
    name = "TELEPORT_ZONE"
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]
    ng = bpy.data.node_groups.new(name, 'ShaderNodeTree')
    nodes, links = ng.nodes, ng.links

    # Group I/O
    inp = nodes.new('NodeGroupInput');  inp.location=(-700,225)
    out = nodes.new('NodeGroupOutput'); out.location=( 800,330)
    _add_group_socket(ng, 'Shader', 'NodeSocketShader', is_input=True)
    _add_group_socket(ng, 'Shader', 'NodeSocketShader', is_input=False)

    # Voronoi→Ramp→Mix #1
    v1 = nodes.new('ShaderNodeTexVoronoi')
    v1.location = (-335,590)
    # remove v1.dimension
    v1.feature = 'DISTANCE_TO_EDGE'
    v1.inputs["Scale"].default_value      = 3.0
    v1.inputs["Randomness"].default_value = 0.75

    r1 = nodes.new('ShaderNodeValToRGB');  r1.location = (-125,440)
    r1.color_ramp.interpolation = 'CONSTANT'
    r1.color_ramp.elements[0].position = 0.0
    r1.color_ramp.elements[0].color    = (1,1,1,1)
    r1.color_ramp.elements[1].position   = 0.03
    r1.color_ramp.elements[1].color    = (0,0,0,1)

    m1 = nodes.new('ShaderNodeMixShader');  m1.location = (270,300)

    # Voronoi→Ramp→Mix #2
    v2 = nodes.new('ShaderNodeTexVoronoi')
    v2.location = (-35,800)
    v2.feature = 'DISTANCE_TO_EDGE'
    v2.inputs["Scale"].default_value      = 3.0
    v2.inputs["Randomness"].default_value = 0.75

    r2 = nodes.new('ShaderNodeValToRGB');  r2.location = (210,550)
    r2.color_ramp.interpolation = 'LINEAR'
    r2.color_ramp.elements[0].position = 0.0
    r2.color_ramp.elements[0].color    = (1,1,1,1)
    r2.color_ramp.elements[1].position   = 0.03
    r2.color_ramp.elements[1].color    = (0,0,0,1)

    m2 = nodes.new('ShaderNodeMixShader');  m2.location = (520,355)

    # colored BSDFs
    p1 = nodes.new('ShaderNodeBsdfPrincipled'); p1.location=(-125,110)
    p1.inputs["Base Color"].default_value=(0xBD/255,0xCB/255,0xCE/255,1); p1.inputs["Alpha"].default_value=1
    p2 = nodes.new('ShaderNodeBsdfPrincipled'); p2.location=(200,110)
    p2.inputs["Base Color"].default_value=(0x83/255,0x94/255,0x8F/255,1); p2.inputs["Alpha"].default_value=1

    # links
    in_sock, out_sock = _get_group_io_sockets(ng)
    links.new(v1.outputs["Distance"], r1.inputs["Fac"])
    links.new(r1.outputs["Color"],   m1.inputs["Fac"])

    links.new(v2.outputs["Distance"],r2.inputs["Fac"])
    links.new(r2.outputs["Color"],   m2.inputs["Fac"])

    links.new(in_sock["Shader"], m1.inputs[1])
    links.new(p1.outputs["BSDF"],    m1.inputs[2])

    links.new(m1.outputs["Shader"], m2.inputs[1])
    links.new(p2.outputs["BSDF"],    m2.inputs[2])

    links.new(m2.outputs["Shader"], out_sock["Shader"])
    return ng

def ensure_slippery_node_group():
    name = "SLIPPERY_ZONE"
    if name in bpy.data.node_groups:
        return bpy.data.node_groups[name]
    ng, nodes, links = bpy.data.node_groups.new(name,'ShaderNodeTree'),None,None
    ng = bpy.data.node_groups[name]; nodes, links = ng.nodes, ng.links

    # Group I/O
    inp = nodes.new('NodeGroupInput');  inp.location=(-700,225)
    out = nodes.new('NodeGroupOutput'); out.location=( 800,330)
    _add_group_socket(ng, 'Shader', 'NodeSocketShader', is_input=True)
    _add_group_socket(ng, 'Shader', 'NodeSocketShader', is_input=False)

    # Noise→Ramp→Mix #1
    n1 = nodes.new('ShaderNodeTexNoise'); n1.location=(-335,590)
    n1.inputs["Scale"].default_value      = 12.0
    n1.inputs["Detail"].default_value     = 2.0
    n1.inputs["Roughness"].default_value  = 0.5
    n1.inputs["Distortion"].default_value = 1.4

    r1 = nodes.new('ShaderNodeValToRGB');  r1.location=(-125,440)
    r1.color_ramp.interpolation = 'CONSTANT'
    r1.color_ramp.elements[0].position = 0.0
    r1.color_ramp.elements[0].color    = (1,1,1,1)
    r1.color_ramp.elements[1].position = 0.45
    r1.color_ramp.elements[1].color    = (0,0,0,1)

    m1 = nodes.new('ShaderNodeMixShader');  m1.location=(270,300)

    # Noise→Ramp→Mix #2
    n2 = nodes.new('ShaderNodeTexNoise'); n2.location=(-35,800)
    for attr in ("Scale","Detail","Roughness","Distortion"):
        n2.inputs[attr].default_value = n1.inputs[attr].default_value

    r2 = nodes.new('ShaderNodeValToRGB');  r2.location=(210,550)
    r2.color_ramp.interpolation = 'LINEAR'
    r2.color_ramp.elements[0].position = 0.0
    r2.color_ramp.elements[0].color    = (1,1,1,1)
    r2.color_ramp.elements[1].position = 0.45
    r2.color_ramp.elements[1].color    = (0,0,0,1)

    m2 = nodes.new('ShaderNodeMixShader');  m2.location=(520,355)

    # colored BSDFs
    p1 = nodes.new('ShaderNodeBsdfPrincipled'); p1.location=(-125,110)
    p1.inputs["Base Color"].default_value=(0x64/255,0x76/255,0x94/255,1); p1.inputs["Alpha"].default_value=1
    p2 = nodes.new('ShaderNodeBsdfPrincipled'); p2.location=(200,110)
    p2.inputs["Base Color"].default_value=(0xA4/255,0xC1/255,0xD0/255,1); p2.inputs["Alpha"].default_value=1

    # links
    in_sock, out_sock = _get_group_io_sockets(ng)
    links.new(n1.outputs["Fac"],    r1.inputs["Fac"])
    links.new(r1.outputs["Color"],  m1.inputs["Fac"])

    links.new(n2.outputs["Fac"],    r2.inputs["Fac"])
    links.new(r2.outputs["Color"],  m2.inputs["Fac"])

    links.new(in_sock["Shader"],m1.inputs[1])
    links.new(p1.outputs["BSDF"],   m1.inputs[2])

    links.new(m1.outputs["Shader"],m2.inputs[1])
    links.new(p2.outputs["BSDF"],   m2.inputs[2])

    links.new(m2.outputs["Shader"], out_sock["Shader"])
    return ng

# ─── CHAINED OVERLAY UTILITY ────────────────────────────────────────────────

def apply_overlays(mat, base_bsdf, overlays):
    """overlays: list of (node_group, label) in order they should apply."""
    tree = mat.node_tree
    out  = tree.nodes.get("Material Output")

    # remove existing BSDF → output links
    for link in list(out.inputs['Surface'].links):
        tree.links.remove(link)

    # create a group‑node for each overlay and connect base_bsdf → each
    grp_nodes = []
    for i,(ng,name) in enumerate(overlays):
        g = tree.nodes.new('ShaderNodeGroup')
        g.node_tree = ng
        # stagger them horizontally
        g.location = base_bsdf.location + mathutils.Vector((300*(i+1), 0))
        tree.links.new(base_bsdf.outputs['BSDF'], g.inputs['Shader'])
        grp_nodes.append((g,name))

    # chain them via MixShader
    if not grp_nodes:
        # no overlays at all: direct BSDF→output
        tree.links.new(base_bsdf.outputs['BSDF'], out.inputs['Surface'])
        return

    # if only one overlay: its output → surface
    if len(grp_nodes)==1:
        tree.links.new(grp_nodes[0][0].outputs['Shader'], out.inputs['Surface'])
    else:
        prev_out = None
        # mix pairwise
        for idx,(g,name) in enumerate(grp_nodes):
            if idx==0:
                prev_out = g.outputs['Shader']
                continue
            mix = tree.nodes.new('ShaderNodeMixShader')
            mix.location = base_bsdf.location + mathutils.Vector((300*idx, -200))
            mix.inputs['Fac'].default_value = 0.5
            # mix prev_out with this group's output
            tree.links.new(prev_out, mix.inputs[1])
            tree.links.new(g.outputs['Shader'], mix.inputs[2])
            prev_out = mix.outputs['Shader']
        tree.links.new(prev_out, out.inputs['Surface'])

def ensure_zone_material(obj):
    source = get_zone_source(obj)
    prefix = source[:2]

    base_name, hexcol, alpha = ZONE_MAT_MAP.get(prefix, ZONE_MAT_MAP["DR"])

    overlay_codes = get_zone_overlay_codes(source)

    base_key = base_name[:-5]
    suffix = "".join(f"_{c}" for c in overlay_codes)
    final_name = f"{base_key}{suffix}_ZONE"

    mat = bpy.data.materials.get(final_name)
    if mat:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        return mat

    mat = bpy.data.materials.new(final_name)
    mat.use_nodes = True
    mat.blend_method = 'BLEND'
    mat.use_backface_culling = True

    r = ((hexcol >> 16) & 0xFF) / 255.0
    g = ((hexcol >> 8) & 0xFF) / 255.0
    b = (hexcol & 0xFF) / 255.0

    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (r, g, b, 1)
        bsdf.inputs["Alpha"].default_value = alpha

        overlays = []
        for code in overlay_codes:
            if code == "PVP":
                overlays.append((ensure_pvp_node_group(), "PVP"))
            elif code == "TP":
                overlays.append((ensure_tp_node_group(), "TP"))
            elif code == "SLP":
                overlays.append((ensure_slippery_node_group(), "SLP"))

        apply_overlays(mat, bsdf, overlays)

    obj.data.materials.clear()
    obj.data.materials.append(mat)

    return mat