import mathutils

_trackdefs = {}
_trackinsts = {}
_tracks = {}


class Track:
    def __init__(self, inst, definition):

        self.name = inst.tag
        self.instance = inst
        self.definition = definition

        self.frames = []

        for f in definition.frames:

            scale, x, y, z, qw, qx, qy, qz = f.frame

            translation = (x/256, y/256, z/256)

            rotation = mathutils.Quaternion((
                qw/16384,
                qx/16384,
                qy/16384,
                qz/16384
            ))

            scale = scale / 256

            self.frames.append({
                "translation": translation,
                "rotation": rotation,
                "scale": scale
            })


def _try_build_track(name):

    inst = _trackinsts.get(name)

    if not inst:
        return

    definition = _trackdefs.get(inst.sprite)

    if not definition:
        return

    _tracks[name] = Track(inst, definition)


def decode_trackdefinition(ctx, trackdef):

    _trackdefs[trackdef.tag] = trackdef

    # some instances might already exist
    for inst_name, inst in _trackinsts.items():
        if inst.sprite == trackdef.tag:
            _try_build_track(inst_name)

    return ""


def decode_trackinstance(ctx, trackinst):

    _trackinsts[trackinst.tag] = trackinst

    _try_build_track(trackinst.tag)

    return ""


def get_track(name):
    return _tracks.get(name)