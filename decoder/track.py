# pyright: basic, reportGeneralTypeIssues=false, reportInvalidTypeForm=false, reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportMissingImports=false

import bpy
import mathutils
import re
import math

regexAniPrefix = re.compile(r"^[CDLOPST](0[1-9]|[1-9][0-9])")
regexItemModel = re.compile(r"IT\d+")

item_patterns = [
    re.compile(r"^[CDLOPST](0[1-9]|[1-9][0-9])IT\d+_TRACK$"),
    re.compile(r"^[CDLOPST](0[1-9]|[1-9][0-9])_IT\d+_TRACK$"),
    re.compile(r"^([CDLOPST](0[1-9]|[1-9][0-9])){2}_IT\d+_TRACK$")
]

animation_patterns = [
    re.compile(r"^[CDLOPST](0[1-9]|[1-9][0-9])[A-Z]{3}_TRACK$"),
    re.compile(r"^([CDLOPST](0[1-9]|[1-9][0-9])){2}[A-Z]{3}_TRACK$"),
    re.compile(r"^([CDLOPST](0[1-9]|[1-9][0-9])){2}_[A-Z]{3}_TRACK$"),
    re.compile(r"^[CDLOPST](0[1-9]|[1-9][0-9])[A-Z]{3}[CDLOPST](0[1-9]|[1-9][0-9])[A-Z]{3}_TRACK$"),
    re.compile(r"^[CDLOPST](0[1-9]|[1-9][0-9])[A-Z]{3}[CDLOPST](0[1-9]|[1-9][0-9])_[A-Z]{3}_TRACK$"),
    re.compile(r"^[CDLOPST](0[1-9]|[1-9][0-9])[A,B,G][A-Z]{3}[CDLOPST](0[1-9]|[1-9][0-9])[A,B,G]_[A-Z]{3}_TRACK$"),
    re.compile(r"^[CDLOPST](0[1-9]|[1-9][0-9])[A,B,G][CDLOPST](0[1-9]|[1-9][0-9])_[A-Z]{3}_TRACK$")
]

dummy_strings = [
    "10404P0", "2HNSWORD", "BARDING", "BELT", "BODY", "BONE",
    "BOW", "BOX", "DUMMY", "HUMEYE", "MESH", "POINT", "POLYSURF",
    "RIDER", "SHOULDER"
]

character_suffixes = {
    "SED": ["FDD"],
    "FMP": ["PE", "CH", "NE", "HE", "BI", "FO", "TH", "CA", "BO"],
    "SKE": ["BI", "BO", "CA", "CH", "FA", "FI", "FO", "HA", "HE",
            "L_POINT", "NE", "PE", "R_POINT", "SH", "TH", "TO", "TU"]
}

item_suffixes = {
    "IT157": ["SNA"],
    "IT61": ["WIP"]
}

_trackdefs = {}
_trackinsts = {}
_tracks = {}

class TrackParseState:
    def __init__(self):
        self.currentAniCode = ""
        self.currentAniModelCode = ""
        self.previousAnimations = {}
class Track:
    def __init__(self, inst, definition):

        self.tag = inst.tag
        self.interpolate = inst.interpolate
        self.reverse = inst.reverse
        self.sleep = inst.sleep

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

def get_all_tracks():
    """Return all combined track objects."""
    return list(_tracks.values())

def parse_track_tag(tag: str, state: TrackParseState):
    """
    Parses a WLD track tag and returns (animation_code, model_code)
    """

    is_character = not bool(regexItemModel.search(tag))

    combined_code = state.currentAniCode + state.currentAniModelCode

    if state.currentAniCode and state.currentAniModelCode and tag.startswith(combined_code):
        return state.currentAniCode, state.currentAniModelCode

    # ------------------------------------------------
    # Check previous animations
    # ------------------------------------------------

    for previous in state.previousAnimations.keys():

        if tag.startswith(previous):

            parts = previous.split(":")

            if len(parts) == 2:
                state.currentAniCode, state.currentAniModelCode = parts
                return state.currentAniCode, state.currentAniModelCode

    # ------------------------------------------------
    # Dummy string detection
    # ------------------------------------------------

    if state.currentAniCode:

        for dummy in dummy_strings:

            if tag.startswith(state.currentAniCode) and dummy in tag:
                return state.currentAniCode, state.currentAniModelCode

    # ------------------------------------------------
    # Character model handling
    # ------------------------------------------------

    if is_character:

        if tag.startswith(state.currentAniCode):

            if state.currentAniModelCode in character_suffixes:

                suffix_start_index = len(state.currentAniCode)

                for suffix in character_suffixes[state.currentAniModelCode]:

                    if tag[suffix_start_index:].startswith(suffix):
                        return state.currentAniCode, state.currentAniModelCode

        # Regex detection

        for i, pattern in enumerate(animation_patterns):

            if pattern.match(tag):

                if i == 0:
                    state.currentAniCode, state.currentAniModelCode = tag[:3], tag[3:6]

                elif i == 1:
                    state.currentAniCode, state.currentAniModelCode = tag[:3], tag[6:9]

                elif i == 2:
                    state.currentAniCode, state.currentAniModelCode = tag[:3], tag[7:10]

                elif i in [3, 4]:
                    state.currentAniCode, state.currentAniModelCode = tag[:3], tag[3:6]

                elif i == 5:
                    state.currentAniCode, state.currentAniModelCode = tag[:4], tag[4:7]

                elif i == 6:
                    state.currentAniCode, state.currentAniModelCode = tag[:4], tag[8:11]

                state.previousAnimations[f"{state.currentAniCode}:{state.currentAniModelCode}"] = True

                return state.currentAniCode, state.currentAniModelCode

        # fallback

        if len(tag) >= 6:
            state.currentAniCode, state.currentAniModelCode = tag[:3], tag[3:6]

            state.previousAnimations[f"{state.currentAniCode}:{state.currentAniModelCode}"] = True

            return state.currentAniCode, state.currentAniModelCode

    # ------------------------------------------------
    # Item model handling
    # ------------------------------------------------

    else:

        if tag.startswith(state.currentAniCode):

            if state.currentAniModelCode in item_suffixes:

                if any(tag[3:].startswith(s) for s in item_suffixes[state.currentAniModelCode]):
                    return state.currentAniCode, state.currentAniModelCode

        for pattern in item_patterns:

            if pattern.match(tag):

                ani_code = tag[:3]

                match = regexItemModel.search(tag)

                model_code = match.group(0) if match else None

                state.currentAniCode = ani_code
                state.currentAniModelCode = model_code

                state.previousAnimations[f"{ani_code}:{model_code}"] = True

                return ani_code, model_code

    return "", ""

def build_wld_animations():

    tracks = get_all_tracks()

    tracks_by_action = {}

    # -----------------------------------------
    # Create parser state (replaces globals)
    # -----------------------------------------

    state = TrackParseState()

    # -----------------------------------------
    # PASS 1 — group tracks into actions
    # -----------------------------------------

    for track in tracks:

        track_name = track.tag

        is_animation = bool(regexAniPrefix.match(track_name))

        if is_animation:

            ani_prefix, model_code = parse_track_tag(track_name, state)

            if not ani_prefix or not model_code:
                continue

            action_name = f"{ani_prefix}_{model_code}"

        else:
            # Pose / armature track
            model_code = track_name[:3]

            action_name = f"POS_{model_code}"

        tracks_by_action.setdefault(action_name, []).append(track)

    # -----------------------------------------
    # PASS 2 — build Blender actions
    # -----------------------------------------

    for action_name, action_tracks in tracks_by_action.items():

        ani_prefix, model_code = action_name.split("_", 1)

        armature_obj = None

        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE' and obj.name.startswith(model_code):
                armature_obj = obj
                break

        if not armature_obj or not armature_obj.pose.bones:
            continue

        action = bpy.data.actions.new(action_name)

        armature_obj.animation_data_create()
        armature_obj.animation_data.action = action

        print("\n=== ACTION:", action_name, "===")

        for track in action_tracks:

            track_name = track.tag
            base_name = track_name.replace("_TRACK", "")

            if ani_prefix and base_name.startswith(ani_prefix):
                base_name = base_name[len(ani_prefix):]

            bone_name = f"{base_name}_DAG"

            if bone_name not in armature_obj.pose.bones:
                continue

            pose_bone = armature_obj.pose.bones[bone_name]
            pose_bone.rotation_mode = 'QUATERNION'

            parent_name = pose_bone.parent.name if pose_bone.parent else None
            print(f"{track_name:25} -> {bone_name:25} parent: {parent_name}")

            # -----------------------------------------
            # Compute frame step from SLEEP
            # -----------------------------------------

            sleep = getattr(track, "sleep", None)

            if sleep:
                fps = bpy.context.scene.render.fps
                frame_step = max(1, (sleep / 1000.0) * fps)
            else:
                frame_step = 1

            current_frame = 1

            # -----------------------------------------
            # Get rest transform
            # -----------------------------------------

            bone = armature_obj.data.bones[bone_name]

            rest_matrix = bone.matrix_local.copy()

            if bone.parent:
                rest_matrix = bone.parent.matrix_local.inverted() @ rest_matrix

            rest_inv = rest_matrix.inverted()

            # -----------------------------------------
            # Frame loop
            # -----------------------------------------

            for frame in track.frames:

                loc = mathutils.Vector(frame["translation"])
                rot = frame["rotation"]
                scale = frame["scale"]

                T = mathutils.Matrix.Translation(loc)
                R = rot.to_matrix().to_4x4()

                local_anim = T @ R

                pose_matrix = rest_inv @ local_anim

                pose_bone.matrix_basis = pose_matrix

                pose_bone.scale = (scale, scale, scale)

                pose_bone.keyframe_insert("location", frame=current_frame)
                pose_bone.keyframe_insert("rotation_quaternion", frame=current_frame)
                pose_bone.keyframe_insert("scale", frame=current_frame)

                current_frame += frame_step
