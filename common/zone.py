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
    userdata = props.userdata

    source = name if name.endswith("_ZONE") else userdata

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