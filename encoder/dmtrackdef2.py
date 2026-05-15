# encoder/dmtrackdef2.py

from ..wce.dmtrackdef2 import dmtrackdef2


def encode_dmtrackdef2(parser, obj) -> str:

    if obj.get("quaildef") != "dmspritedef2":
        return ""

    mesh = obj.data
    key_data = mesh.shape_keys

    if not key_data or key_data.get("quaildef") != "dmtrackdef2":
        return ""

    props = key_data.quail_dmtrackdef2

    wce_track = dmtrackdef2()

    wce_track.tag = props.tag
    wce_track.sleep = props.sleep
    wce_track.param2 = props.param2
    wce_track.size6 = props.size6

    if hasattr(obj, "quail_dmspritedef2"):
        wce_track.fpscale = obj.quail_dmspritedef2.fpscale
    else:
        wce_track.fpscale = 0

    wce_track.frames = []

    for key in key_data.key_blocks:

        if key.name == "Basis":
            continue

        frame = dmtrackdef2.numvertices()
        frame.vertices = []

        for sk_vert in key.data:
            xyz = dmtrackdef2.numvertices.xyz()
            xyz.xyz = (
                float(sk_vert.co.x),
                float(sk_vert.co.y),
                float(sk_vert.co.z),
            )

            frame.vertices.append(xyz)

        wce_track.frames.append(frame)

    parser.dmtrackdef2s[wce_track.tag] = wce_track

    return ""