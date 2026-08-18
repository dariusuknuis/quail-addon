# pyright: basic, reportGeneralTypeIssues=false, reportOptionalSubscript=false

import bpy
import mathutils
from ..wce.wce import wce
from typing import Optional
from ..common import base_tag
from ..common.s3dmaterial import material_tag_parse
from .worlddef import encode_worlddef
from .globalambientlightdef import encode_globalambientlightdef
from .worldtree import encode_worldtree
from .light import encode_light
from .region import encode_region
from .zone import encode_zone
from .actorinst import encode_actorinst
from .actordef import encode_actordef
from .hierarchicalspritedef import encode_hierarchicalspritedef
from .track import encode_track
from .particleclouddef import encode_particleclouddef
from .blitspritedef import encode_blitspritedef
from .dmspritedef2 import encode_dmspritedef2
from .dmspritedefinition import encode_dmspritedefinition
from .sprite3ddef import encode_sprite3ddef
from .rgbdeformationtrackdef import encode_rgbdeformationtrackdef
from .polyhedrondefinition import encode_polyhedrondefinition
from .materialpalette import encode_materialpalette
from .materialdefinition import encode_materialdefinition
from .simplespritedef import encode_simplespritedef
from .eqgmodeldef import encode_eqgmodeldef
from .eqganidef import encode_eqganidef
from ..logger.error import error
from .context import Context
import os, shutil, re

def extract_r_index(tag: str):
    m = re.match(r"R(\d+)", tag.upper())
    return int(m.group(1)) if m else 0

def write_animation_folder(parser, root_path):
    # ----------------------------------------
    # Group tracks by animation
    # ----------------------------------------
    anim_groups = {}

    for t in parser.tracks.values():
        if t.is_pose:
            continue

        anim_groups.setdefault(t.animation, []).append(t)

    if not anim_groups:
        return False

    anim_dir = os.path.join(root_path, "animations")
    os.makedirs(anim_dir, exist_ok=True)

    # ----------------------------------------
    # Write animation files (ALL TRACKS per anim)
    # ----------------------------------------
    for anim_name, tracks in anim_groups.items():

        filepath = os.path.join(anim_dir, f"{anim_name.lower()}.wce")

        with open(filepath, "w") as w:

            w.write("// wcemu v0.0.1\n")
            w.write("// Animation file\n\n")

            for t in tracks:
                t.write(w)
                w.write("\n")

    # ----------------------------------------
    # Write animations/_root.wce (DEDUPED)
    # ----------------------------------------
    root_file = os.path.join(anim_dir, "_root.wce")

    with open(root_file, "w") as w:
        for anim_name in sorted(anim_groups.keys()):
            w.write(f"INCLUDE \"{anim_name.upper()}.WCE\"\n")

    return True

def write_material_sets(parser, material_sets, model_dir):

    if not material_sets:
        return False

    root_lines = []

    for filepath, entries in material_sets.items():

        with open(filepath, "w") as w:

            written_sprites = set()

            for mat, sprite_tag in entries:

                # write sprite first
                if sprite_tag:
                    sprite = parser.simplespritedefs.get(sprite_tag)

                    if sprite and sprite_tag not in written_sprites:
                        sprite.write(w)
                        w.write("\n")
                        written_sprites.add(sprite_tag)

                mat.write(w)
                w.write("\n")

        # track for _root.wce
        filename = os.path.basename(filepath)
        root_lines.append(f'INCLUDE "{filename.upper()}"\n')

    # ----------------------------------------
    # Write material_sets/_root.wce
    # ----------------------------------------
    if root_lines:
        root_path = os.path.join(model_dir, "material_sets", "_root.wce")

        with open(root_path, "w") as w:
            for line in sorted(root_lines):
                w.write(line)

    return True

def get_material_set_filename(tag: str, model_dir: str) -> str:

    tag_upper = tag.upper()

    material_sets_dir = os.path.join(model_dir, "material_sets")
    os.makedirs(material_sets_dir, exist_ok=True)

    if tag_upper.startswith("CHR_EYE"):
        return os.path.join(material_sets_dir, "chr_eye.wce")

    elif tag_upper.startswith("CLK") and len(tag_upper) >= 5:
        return os.path.join(material_sets_dir, tag_upper[:5].lower() + ".wce")

    elif len(tag_upper) >= 8:
        index = tag_upper[5:8]
        base = tag_upper[:3].lower()

        return os.path.join(material_sets_dir, f"{base}_alt{index}.wce")

    else:
        return os.path.join(material_sets_dir, "other_mats.wce")

def write_materials_and_sprites(parser, w, model_dir):

    written_sprites = set()

    # ----------------------------------------
    # Collect variation material groups
    # ----------------------------------------
    material_sets = {}

    for tag, mat in parser.materialdefinitions.items():

        sprite_tag = mat.simplespriteinst.simplespritetag

        is_variation = tag in parser.variationmaterialtags
        # print("CHECK:", tag, "->", tag in parser.variationmaterialtags)

        # ----------------------------------------
        # Handle VARIATION materials
        # ----------------------------------------
        if is_variation:

            filename = get_material_set_filename(tag, model_dir)

            if filename not in material_sets:
                material_sets[filename] = []

            material_sets[filename].append((mat, sprite_tag))
            continue

        # ----------------------------------------
        # NORMAL MATERIAL PATH
        # ----------------------------------------
        if sprite_tag:
            sprite = parser.simplespritedefs.get(sprite_tag)

            if sprite and sprite_tag not in written_sprites:
                sprite.write(w)
                w.write("\n")
                written_sprites.add(sprite_tag)

        mat.write(w)
        w.write("\n")

    # ----------------------------------------
    # Write MATERIAL SET FILES
    # ----------------------------------------
    wrote_material_sets = write_material_sets(parser, material_sets, model_dir)
    return wrote_material_sets

def write_eqg_model_files(parser, model_name, model_dir):

    model_wce_path = os.path.join(
        model_dir,
        f"{model_name}.wce",
    )

    with open(model_wce_path, "w") as w:
        w.write("// wcemu v0.0.1\n\n")

        for tag in sorted(
            parser.eqgmodeldefs.keys(),
            key=str.casefold,
        ):
            parser.eqgmodeldefs[tag].write(w)
            w.write("\n")

    wrote_animations = False
    animations = getattr(parser, "eqganidefs", {})

    if animations:
        animation_filename = f"{model_name}_ani.wce"
        animation_path = os.path.join(
            model_dir,
            animation_filename,
        )

        with open(animation_path, "w") as w:
            w.write("// wcemu v0.0.1\n\n")

            for tag in sorted(
                animations.keys(),
                key=str.casefold,
            ):
                animations[tag].write(w)
                w.write("\n")

        wrote_animations = True

    root_file = os.path.join(
        model_dir,
        "_root.wce",
    )

    with open(root_file, "w") as w:
        w.write(
            f'INCLUDE "{model_name.upper()}.WCE"\n'
        )

        if wrote_animations:
            w.write(
                f'INCLUDE "{model_name.upper()}_ANI.WCE"\n'
            )

    return ""

def write_model_folder(parser, root_obj, export_objects, root_path, use_eqg):
    model_name = get_model_name(root_obj)
    model_dir = os.path.join(root_path, model_name)
    os.makedirs(model_dir, exist_ok=True)

    local_parser = wce(model_dir)
    local_parser.variationmaterialtags = set(parser.variationmaterialtags)

    local_objects = _gather_export_objects([root_obj], parser)
    local_actions = _gather_export_actions(local_objects)

    # ----------------------------------------
    # Copy an ACTORDEF root
    # ----------------------------------------
    if root_obj.name in parser.actordefs:
        local_parser.actordefs[root_obj.name] = parser.actordefs[root_obj.name]

    # ----------------------------------------
    # Definitions copied directly by object name
    # ----------------------------------------
    definition_collections = {
        "hierarchicalspritedef": "hierarchicalspritedefs",
        "particleclouddef": "particleclouddefs",
        "blitspritedef": "blitspritedefs",
        "dmspritedef2": "dmspritedef2s",
        "dmspritedefinition": "dmspritedefinitions",
        "eqgmodeldef": "eqgmodeldefs",
        "eqgskinnedmodeldef": "eqgskinnedmodeldefs",
        "eqgterdef": "eqgterdefs",
        "polyhedrondefinition": "polyhedrondefinitions",
        "materialpalette": "materialpalettes",
        "materialdefinition": "materialdefinitions",
        "simplespritedef": "simplespritedefs",
    }

    for obj in local_objects:
        if not hasattr(obj, "get"):
            continue

        qdef = obj.get("quaildef")
        collection_name = definition_collections.get(qdef)

        if not collection_name:
            continue

        source_collection = getattr(parser, collection_name, None)
        destination_collection = getattr(local_parser, collection_name, None)

        if source_collection is None or destination_collection is None:
            continue

        if obj.name not in source_collection:
            continue

        definition = source_collection[obj.name]
        destination_collection[obj.name] = definition

        # DMSPRITEDEF2 can reference a separately encoded DMTRACKDEF2.
        if qdef == "dmspritedef2":
            dmtrack_tag = getattr(definition, "dmtrackinst", "")

            if dmtrack_tag and dmtrack_tag in parser.dmtrackdef2s:
                local_parser.dmtrackdef2s[dmtrack_tag] = parser.dmtrackdef2s[dmtrack_tag]

    # ----------------------------------------
    # Copy locally owned Actions
    # ----------------------------------------
    for action in local_actions:
        action_type = action.get("quaildef")

        if action_type == "track":
            for track in parser.tracks.values():
                animation_name = getattr(track, "animation", "")

                if animation_name.casefold() != action.name.casefold():
                    continue

                local_parser.tracks[track.tag] = track

                if track.trackdef in parser.trackdefinitions:
                    local_parser.trackdefinitions[track.trackdef] = (
                        parser.trackdefinitions[track.trackdef]
                    )

        elif action_type == "eqganidef":
            animation = parser.eqganidefs.get(action.name)

            if animation:
                local_parser.eqganidefs[action.name] = animation

    # ----------------------------------------
    # EQG output layout
    # ----------------------------------------
    if use_eqg:
        err = write_eqg_model_files(local_parser, model_name, model_dir)

        if err:
            return err

        return ""

    # ----------------------------------------
    # S3D model file
    # ----------------------------------------
    model_wce_path = os.path.join(model_dir, f"{model_name}.wce")

    with open(model_wce_path, "w") as w:
        w.write("// wcemu v0.0.1\n\n")

        wrote_material_sets = write_materials_and_sprites(
            local_parser,
            w,
            model_dir,
        )

        for definition in local_parser.materialpalettes.values():
            definition.write(w)
            w.write("\n")

        for definition in local_parser.polyhedrondefinitions.values():
            definition.write(w)
            w.write("\n")

        for definition in local_parser.dmtrackdef2s.values():
            definition.write(w)
            w.write("\n")

        for definition in local_parser.dmspritedef2s.values():
            definition.write(w)
            w.write("\n")

        for definition in local_parser.dmspritedefinitions.values():
            definition.write(w)
            w.write("\n")

        write_blitsprites_and_sprites(local_parser, w)

        for definition in local_parser.particleclouddefs.values():
            definition.write(w)
            w.write("\n")

        for track in local_parser.tracks.values():
            if track.is_pose:
                track.write(w)
                w.write("\n")

        for definition in local_parser.hierarchicalspritedefs.values():
            definition.write(w)
            w.write("\n")

        for definition in local_parser.actordefs.values():
            definition.write(w)
            w.write("\n")

    # ----------------------------------------
    # S3D animation files
    # ----------------------------------------
    wrote_animations = write_animation_folder(local_parser, model_dir)

    # ----------------------------------------
    # Model _root.wce
    # ----------------------------------------
    root_file = os.path.join(model_dir, "_root.wce")

    with open(root_file, "w") as w:
        if wrote_animations:
            w.write('INCLUDE "ANIMATIONS/_ROOT.WCE"\n')

        if wrote_material_sets:
            w.write('INCLUDE "MATERIAL_SETS/_ROOT.WCE"\n')

        w.write(f'INCLUDE "{model_name.upper()}.WCE"\n')

    return ""

def write_blitsprites_and_sprites(parser, w):

    written_sprites = set()

    for tag in parser.simplespritedefs.keys():

        if tag in written_sprites:
            continue

    # ----------------------------------------
    # BLITSPRITEDEFS
    # ----------------------------------------

    for tag, blit in parser.blitspritedefs.items():

        sprite_tag = blit.sprite

        # ----------------------------------------
        # SIMPLESPRITEDEF
        # ----------------------------------------

        if sprite_tag:

            sprite = parser.simplespritedefs.get(
                sprite_tag
            )

            if (
                sprite and
                sprite_tag not in written_sprites
            ):

                sprite.write(w)
                w.write("\n")

                written_sprites.add(
                    sprite_tag
                )

        blit.write(w)
        w.write("\n")

def write_ambientlightdef(w, parser):

    regions = sorted(
        parser.regions.values(),
        key=lambda x: extract_r_index(x.tag)
    )

    count = len(regions)

    region_indices = " ".join(str(i) for i in range(count))

    w.write('AMBIENTLIGHT "DEFAULT_AMBIENTLIGHT"\n')
    w.write('\tLIGHT "DEFAULT_LIGHTDEF"\n')
    w.write('\t// LIGHTFLAGS 0\n')
    w.write(f'\tREGIONLIST {count} {region_indices}\n\n')

    w.write('LIGHTDEFINITION "DEFAULT_LIGHTDEF"\n')
    w.write('\tCURRENTFRAME? NULL\n')
    w.write('\tNUMFRAMES 1\n')
    w.write('\t\tLIGHTLEVELS 1.00000000e+00\n')
    w.write('\tSLEEP? NULL\n')
    w.write('\tHAVESKIPFRAMES 1\n')
    w.write('\tSKIPFRAMES 0\n')
    w.write('\tNUMCOLORS 0\n\n')

def write_world_wce(parser, root_path):

    world_path = os.path.join(root_path, "world.wce")

    with open(world_path, "w") as w:
        w.write("// wcemu v0.0.1\n")
        w.write("// Generated by exporter\n\n")

        if parser.worlddef:
            parser.worlddef.write(w)
        else:
            # fallback (optional)
            w.write("WORLDDEF\n")
            w.write("\tNEWWORLD 0\n")
            w.write("\tZONE 0\n")
            w.write("\tEQGVERSION? NULL\n")

def export_asset_images(export_objects, assets_dir):
    written = set()

    def source_material(material):
        if not material or not material.get("quail_layer_preview", False):
            return material

        source_name = material.get("quail_layer_source", "")
        return bpy.data.materials.get(source_name) or material

    def eqg_image_filename(image):
        source_name = image.get("quail_source_name", "")

        if source_name:
            return os.path.basename(str(source_name)).lower()

        if image.filepath:
            return os.path.basename(bpy.path.abspath(image.filepath)).lower()

        return os.path.basename(image.name).lower()

    def export_image(image, filename):
        if not image or not filename:
            return

        filename = os.path.basename(filename).lower()

        if filename in written:
            return

        written.add(filename)
        destination = os.path.join(assets_dir, filename)

        try:
            if image.packed_file:
                image.unpack(method='USE_ORIGINAL')

            source = bpy.path.abspath(image.filepath)

            if source and os.path.exists(source):
                shutil.copy2(source, destination)
            else:
                print(f"Fallback saving image (no source): {filename}")
                image.save_render(destination)

        except Exception as exception:
            print(f"ERROR exporting image {filename}: {exception}")

    for item in export_objects:
        if not hasattr(item, "get"):
            continue

        qdef = item.get("quaildef")

        # ----------------------------------------
        # S3D SimpleSprite images
        # ----------------------------------------
        if qdef == "simplespritedef":
            props = item.quail_simplesprite

            for frame in props.frames:
                for file in frame.files:
                    if not file.image_name or not file.file_name:
                        continue

                    image = bpy.data.images.get(file.image_name)

                    if not image:
                        print(f"WARNING: Missing image {file.image_name}")
                        continue

                    export_image(image, file.file_name)

            continue

        # ----------------------------------------
        # EQG model materials
        # ----------------------------------------
        if qdef not in {
            "eqgmodeldef",
            "eqgskinnedmodeldef",
            "eqgterdef",
        }:
            continue

        if not isinstance(item, bpy.types.Object) or item.type != 'MESH':
            continue

        for assigned_material in item.data.materials:
            material = source_material(assigned_material)

            if not material or material.get("quaildef") != "eqgmaterialdef":
                continue

            props = material.quail_eqgmaterialdef

            for row in props.property_rows:
                property_name = row.property_name

                if not property_name or not hasattr(props, property_name):
                    continue

                rna_property = props.bl_rna.properties.get(property_name)

                if (
                    not rna_property
                    or rna_property.type != 'POINTER'
                    or rna_property.fixed_type.identifier != "Image"
                ):
                    continue

                image = getattr(props, property_name)

                if image:
                    export_image(image, eqg_image_filename(image))

def write_zone_folder(parser, export_objects, root_path):

    print("Writing ZONE structure:", root_path)

    os.makedirs(root_path, exist_ok=True)

    # ----------------------------------------
    # ASSETS
    # ----------------------------------------
    assets_dir = os.path.join(root_path, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    export_asset_images(export_objects, assets_dir)

    # ----------------------------------------
    # WORLD.WCE
    # ----------------------------------------
    write_world_wce(parser, root_path)

    # ----------------------------------------
    # ZONE FOLDER
    # ----------------------------------------
    zone_dir = os.path.join(root_path, "zone")
    os.makedirs(zone_dir, exist_ok=True)

    zone_path = os.path.join(zone_dir, "zone.wce")

    with open(zone_path, "w") as w:
        w.write("// ZONE\n\n")

        if parser.globalambientlightdef:
            parser.globalambientlightdef.write(w)
            w.write("\n")

        write_ambientlightdef(w, parser)

        for wt in parser.worldtrees.values():
            wt.write(w)
            w.write("\n")

        sprite = parser.sprite3ddefs.get("CAMERA_DUMMY")

        if sprite:
            sprite.write(w)
            w.write("\n")

            matched_actordef = None

            for actordef in parser.actordefs.values():
                for action in actordef.actions:
                    for lod in action.action.levelsofdetails:
                        if lod.levelofdetail.sprite == sprite.tag:
                            matched_actordef = actordef
                            break
                    if matched_actordef:
                        break
                if matched_actordef:
                    break

            if matched_actordef:
                matched_actordef.write(w)
                w.write("\n")

                for actorinst in parser.actorinsts.values():
                    if actorinst.sprite == matched_actordef.tag:
                        actorinst.write(w)
                        w.write("\n")

        for zone in parser.zones.values():
            zone.write(w)
            w.write("\n")

    with open(os.path.join(zone_dir, "_root.wce"), "w") as w:
        w.write('INCLUDE "ZONE.WCE"\n')

    # ----------------------------------------
    # REGION FOLDER
    # ----------------------------------------
    region_dir = os.path.join(root_path, "region")
    os.makedirs(region_dir, exist_ok=True)

    region_path = os.path.join(region_dir, "region.wce")

    with open(region_path, "w") as w:
        w.write("// REGION\n\n")

        write_materials_and_sprites(parser, w, region_dir)

        for obj in parser.materialpalettes.values():
            obj.write(w)
            w.write("\n")

        regions_sorted = sorted(
            parser.regions.values(),
            key=lambda x: extract_r_index(x.tag)
        )

        for obj in regions_sorted:
            obj.write(w)
            w.write("\n")

    # ----------------------------------------
    # Rxxxx FILES (chunked DMSPRITEDEFs)
    # ----------------------------------------
    dms = sorted(
        list(parser.dmspritedef2s.values()) +
        list(parser.dmspritedefinitions.values()),
        key=lambda x: extract_r_index(x.tag)
    )

    chunk_size = 1000
    r_files = []

    for i in range(0, len(dms), chunk_size):
        chunk = dms[i:i + chunk_size]

        index = i + chunk_size
        filename = f"r{index}.wce"
        filepath = os.path.join(region_dir, filename)

        with open(filepath, "w") as w:
            w.write("// DMSPRITES\n\n")

            for obj in chunk:
                obj.write(w)
                w.write("\n")

        r_files.append(filename)

    # ----------------------------------------
    # region/_root.wce
    # ----------------------------------------
    with open(os.path.join(region_dir, "_root.wce"), "w") as w:
        w.write('INCLUDE "REGION.WCE"\n')

        for f in sorted(r_files):
            w.write(f'INCLUDE "{f.upper()}"\n')

    # ----------------------------------------
    # ROOT _root.wce
    # ----------------------------------------
    root_file = os.path.join(root_path, "_root.wce")

    with open(root_file, "w") as w:

        w.write('INCLUDE "WORLD.WCE"\n')
        w.write('INCLUDE "ZONE/_ROOT.WCE"\n')
        w.write('INCLUDE "REGION/_ROOT.WCE"\n')

    return ""

def write_objects_folder(parser, export_objects, root_path):

    os.makedirs(root_path, exist_ok=True)

    world_path = os.path.join(root_path, "world.wce")

    with open(world_path, "w") as w:
        w.write("// wcemu v0.0.1\n\n")

        if parser.worlddef:
            parser.worlddef.write(w)
            w.write("\n")
        else:
            w.write("WORLDDEF\n")
            w.write("\tNEWWORLD 0\n")
            w.write("\tZONE 0\n")
            w.write("\tEQGVERSION? NULL\n\n")

        for inst in parser.actorinsts.values():

            if inst.sprite == "PLAYER_1":
                continue

            if inst.dmrgbtrack:
                track = parser.rgbdeformationtrackdefs.get(inst.dmrgbtrack)
                if track:
                    track.write(w)
                    w.write("\n")

            inst.write(w)
            w.write("\n")

    # ----------------------------------------
    # _root.wce
    # ----------------------------------------
    with open(os.path.join(root_path, "_root.wce"), "w") as w:
        w.write('INCLUDE "WORLD.WCE"\n')

    return ""

def write_lights_folder(parser, export_objects, root_path):

    os.makedirs(root_path, exist_ok=True)

    # ========================================
    # WORLD.WCE (POINTLIGHTS)
    # ========================================
    world_path = os.path.join(root_path, "world.wce")

    with open(world_path, "w") as w:
        w.write("// wcemu v0.0.1\n\n")

        # WORLDDEF
        if parser.worlddef:
            parser.worlddef.write(w)
            w.write("\n")
        else:
            w.write("WORLDDEF\n")
            w.write("\tNEWWORLD 0\n")
            w.write("\tZONE 0\n")
            w.write("\tEQGVERSION? NULL\n\n")

        # POINTLIGHTS
        for inst in parser.pointlights.values():
            inst.write(w)
            w.write("\n")

    # ========================================
    # ZONE FOLDER (LIGHTDEFINITIONS)
    # ========================================
    zone_dir = os.path.join(root_path, "zone")
    os.makedirs(zone_dir, exist_ok=True)

    zone_path = os.path.join(zone_dir, "zone.wce")

    with open(zone_path, "w") as w:
        w.write("// ZONE\n\n")

        for ldef in parser.lightdefinitions.values():
            ldef.write(w)
            w.write("\n")

    # zone/_root.wce
    with open(os.path.join(zone_dir, "_root.wce"), "w") as w:
        w.write('INCLUDE "ZONE.WCE"\n')

    # ========================================
    # ROOT _root.wce
    # ========================================
    with open(os.path.join(root_path, "_root.wce"), "w") as w:
        w.write('INCLUDE "WORLD.WCE"\n')
        w.write('INCLUDE "ZONE/_ROOT.WCE"\n')

    return ""

def find_child_collections(parent_col):
    objects_col = None
    lights_col = None

    if not parent_col:
        return objects_col, lights_col

    for child in parent_col.children:
        name = child.name.lower()

        if name == "_objects":
            objects_col = child

        elif name == "_lights":
            lights_col = child

    return objects_col, lights_col

def write_quail_folder(parser, export_objects, root_path, context, use_eqg):
    print("Writing quail folder:", root_path)

    # ----------------------------------------
    # Zone archive
    # ----------------------------------------
    if parser.worlddef and parser.worlddef.zone:
        collection = context.collection if context else None
        objects_col, lights_col = find_child_collections(collection)

        err = write_zone_folder(parser, export_objects, root_path)

        if err:
            return err

        if objects_col:
            objects_path = os.path.join(root_path, "_objects")
            object_exports = _gather_export_objects([objects_col], parser)
            err = write_objects_folder(parser, object_exports, objects_path)

            if err:
                return err

        if lights_col:
            lights_path = os.path.join(root_path, "_lights")
            light_exports = _gather_export_objects([lights_col], parser)
            err = write_lights_folder(parser, light_exports, lights_path)

            if err:
                return err

        return ""

    # ----------------------------------------
    # Model archive
    # ----------------------------------------
    os.makedirs(root_path, exist_ok=True)

    assets_dir = os.path.join(root_path, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # This currently exports S3D SimpleSprite images. EQG image copying
    # will need to be added to this function or unified with it later.
    export_asset_images(export_objects, assets_dir)

    write_world_wce(parser, root_path)

    roots = get_root_objects(export_objects)
    model_dirs = []

    for root in roots:
        model_name = get_model_name(root)

        if model_name in model_dirs:
            continue

        err = write_model_folder(
            parser,
            root,
            export_objects,
            root_path,
            use_eqg,
        )

        if err:
            return err

        model_dirs.append(model_name)

    root_file = os.path.join(root_path, "_root.wce")

    with open(root_file, "w") as w:
        w.write('INCLUDE "WORLD.WCE"\n')

        for model_name in model_dirs:
            w.write(f'INCLUDE "{model_name.upper()}/_ROOT.WCE"\n')

    return ""

def get_root_objects(export_objects):
    roots = []
    root_set = set()

    def add_root(obj):
        if obj not in root_set:
            root_set.add(obj)
            roots.append(obj)

    # Objects owned by ACTORDEF collections
    actordef_owned = set()
    particle_render_owned = set()
    for item in export_objects:
        if not isinstance(item, bpy.types.Collection):
            continue

        if item.get("quaildef") == "actordef":
            for child in item.all_objects:
                actordef_owned.add(child)

        elif item.get("quaildef") == "eqgparticlerenderdef":
            for child in item.all_objects:
                particle_render_owned.add(child)

    # DMSPRITEDEFs used directly by regions
    region_sprite_tags = set()
    for item in export_objects:
        if not isinstance(item, bpy.types.Object):
            continue

        if item.get("quaildef") != "region":
            continue

        if item.quail_region.sprite:
            region_sprite_tags.add(item.quail_region.sprite)

    # Root detection
    for item in export_objects:
        if isinstance(item, bpy.types.Collection):
            if item.get("quaildef") == "actordef":
                add_root(item)

            continue

        if not isinstance(item, bpy.types.Object):
            continue

        qdef = item.get("quaildef")
        if not qdef:
            continue

        if qdef in {"worldnode", "region", "materialpalette"}:
            continue

        if item in actordef_owned or item in particle_render_owned:
            continue

        if (
            qdef in {"dmspritedef2", "dmspritedefinition"}
            and item.name in region_sprite_tags
        ):
            continue

        if item.parent is None:
            add_root(item)

    roots.sort(key=lambda item: item.name.casefold())
    return roots

def get_model_name(obj):
    name = obj.name.lower()

    if "_" in name:
        return name.split("_")[0]

    return name

def _gather_export_actions(export_objects):
    actions = {}

    for obj in export_objects:
        if not isinstance(obj, bpy.types.Object) or obj.type != 'ARMATURE':
            continue

        armature_type = obj.get("quaildef")

        if armature_type == "hierarchicalspritedef":
            expected_action_type = "track"
            model_code = obj.name[:-7] if obj.name.upper().endswith("_HS_DEF") else obj.name

        elif armature_type == "eqgmodarmature":
            expected_action_type = "eqganidef"
            model_code = obj.name[:-9] if obj.name.lower().endswith("_armature") else obj.name

        else:
            continue

        if obj.animation_data and obj.animation_data.action:
            action = obj.animation_data.action

            if action.get("quaildef") == expected_action_type:
                actions.setdefault(action, obj)

        model_suffix = "_" + model_code.casefold()

        for action in bpy.data.actions:
            if action.get("quaildef") != expected_action_type:
                continue

            if action.name.casefold().endswith(model_suffix):
                actions.setdefault(action, obj)

    return actions

def _gather_export_objects(root_objects, parser):
    visited = set()
    stack = list(root_objects)
    palette_material_tags = set()

    parser.variationmaterialtags.clear()

    def add(item):
        if item is not None and item not in visited:
            stack.append(item)

    def add_simple_sprite(sprite_tag, owner_name):
        if not sprite_tag or sprite_tag == "NONE":
            return

        sprite = bpy.data.node_groups.get(sprite_tag)
        if sprite:
            add(sprite)
        else:
            print(f"WARNING: Missing SimpleSpriteDef '{sprite_tag}' for '{owner_name}'")

    # Selecting one world node means exporting the complete WORLDTREE.
    if any(
        item.get("quaildef") == "worldnode"
        for item in root_objects
        if hasattr(item, "get")
    ):
        for collection in bpy.data.collections:
            if collection.name != "WORLDTREE":
                continue

            for obj in collection.objects:
                if obj.get("quaildef") == "worldnode":
                    add(obj)

    while stack:
        item = stack.pop()
        if item in visited:
            continue

        visited.add(item)

        # ----------------------------------------
        # Collection contents
        # ----------------------------------------
        if isinstance(item, bpy.types.Collection):
            for child_obj in item.objects:
                add(child_obj)

            for child_collection in item.children:
                add(child_collection)

            continue

        # Materials and node groups can be dependencies, but only
        # Blender Objects have children, modifiers, and parents.
        if isinstance(item, bpy.types.Object):
            for child in item.children:
                add(child)

        qdef = item.get("quaildef") if hasattr(item, "get") else None

        # ----------------------------------------
        # Mesh → owning armature
        # ----------------------------------------
        if (
            isinstance(item, bpy.types.Object)
            and qdef in {
                "dmspritedef2",
                "dmspritedefinition",
                "eqgmodeldef",
                "eqgskinnedmodeldef",
            }
        ):
            if (
                item.parent
                and item.parent.type == 'ARMATURE'
                and item.parent.get("quaildef") in {
                    "hierarchicalspritedef",
                    "eqgmodarmature",
                }
            ):
                add(item.parent)

            for modifier in item.modifiers:
                if modifier.type == 'ARMATURE' and modifier.object:
                    add(modifier.object)

        # ----------------------------------------
        # WORLDNODE → REGION
        # ----------------------------------------
        if qdef == "worldnode":
            region_tag = item.quail_worldnode.region_tag

            if region_tag:
                add(bpy.data.objects.get(region_tag))

        # ----------------------------------------
        # REGION → DMSPRITE
        # ----------------------------------------
        elif qdef == "region":
            sprite_tag = item.quail_region.sprite

            if sprite_tag:
                add(bpy.data.objects.get(sprite_tag))

        # ----------------------------------------
        # DMSPRITE → MATERIALPALETTE
        # ----------------------------------------
        elif qdef == "dmspritedef2":
            add(item.quail_dmspritedef2.materialpalette)

        elif qdef == "dmspritedefinition":
            add(item.quail_dmspritedefinition.materialpalette)

        # ----------------------------------------
        # BLITSPRITEDEF → SIMPLESPRITEDEF
        # ----------------------------------------
        elif qdef == "blitspritedef":
            if not item.data or not item.data.materials:
                continue

            material = item.data.materials[0]

            if not material or material.get("quaildef") != "blitspritematerial":
                continue

            add_simple_sprite(
                item.quail_blitspritedef.simplespritetag,
                item.name,
            )

        # ----------------------------------------
        # MATERIALPALETTE dependencies
        # ----------------------------------------
        elif qdef == "materialpalette":
            props = item.quail_materialpalette
            for entry in props.materials:
                material = entry.material
                if not material:
                    continue

                add(material)
                if material.get("quaildef") != "materialdefinition":
                    continue

                palette_material_tags.add(material.name)
                add_simple_sprite(
                    material.quail_materialdefinition.simplespritetag,
                    material.name,
                )

            # ----------------------------------------
            # Find external S3D material variations
            # ----------------------------------------
            for material in bpy.data.materials:
                if material.get("quaildef") != "materialdefinition":
                    continue

                tag = material.name

                if tag in palette_material_tags:
                    continue

                prefix = material_tag_parse(tag)

                if not prefix:
                    continue

                if not any(
                    palette_tag.startswith(prefix)
                    for palette_tag in palette_material_tags
                ):
                    continue

                parser.variationmaterialtags.add(tag)
                material.quail_materialdefinition.variation = True
                add(material)
                sprite_tag = material.quail_materialdefinition.simplespritetag
                if sprite_tag and sprite_tag != "NONE":
                    sprite = bpy.data.node_groups.get(sprite_tag)
                    if sprite:
                        sprite.quail_simplesprite.variation = True
                        add(sprite)
                    else:
                        print(
                            f"WARNING: Missing SimpleSpriteDef "
                            f"'{sprite_tag}' for variation material '{tag}'"
                        )

    return visited

def wce_encode(folder_path: str, context, selected_only: bool) -> str:

    parser = wce(folder_path)
    errors = []

    # Resolve the active/export WORLDDEF
    active_collection = context.collection
    world_collection = None

    if (
        active_collection
        and active_collection.get("quaildef") == "worlddef"
    ):
        world_collection = active_collection

    else:
        for candidate in bpy.data.collections:
            if candidate.get("quaildef") != "worlddef":
                continue

            # Skip structural subfolders.
            if candidate.name.lower().startswith("_"):
                continue

            world_collection = candidate
            break

    use_eqg = bool(
        world_collection
        and world_collection.quail_worlddef.use_eqg
    )

    # ------------------------------------------------
    # Build initial root set
    # ------------------------------------------------

    if selected_only:

        if (
            active_collection
            and active_collection.get("quaildef")
            == "worlddef"
        ):
            root_objects = (
                list(active_collection.objects)
                + list(active_collection.children)
            )

        elif (
            active_collection
            and active_collection.get("quaildef")
            == "actordef"
        ):
            root_objects = [active_collection]

        elif context.selected_objects:
            root_objects = list(
                context.selected_objects
            )

        elif active_collection:
            root_objects = (
                list(active_collection.objects)
                + list(active_collection.children)
            )

        else:
            root_objects = []

    elif active_collection:
        root_objects = (
            list(active_collection.objects)
            + list(active_collection.children)
        )

    else:
        root_objects = []

    # ------------------------------------------------
    # Gather the shared dependency graph
    export_objects = _gather_export_objects(root_objects, parser)
    export_actions = _gather_export_actions(export_objects)

    print("Export set:")

    for obj in export_objects:
        print("  ", obj.name, obj.get("quaildef"))

    # Encode WORLDDEF
    if world_collection:
        err = encode_worlddef(parser, world_collection)
        if err:
            errors.append(err)

    # Find WORLDTREE
    worldtree_collection = None

    if (
        active_collection
        and active_collection.name == "WORLDTREE"
    ):
        worldtree_collection = active_collection

    elif active_collection:
        for child in active_collection.children:
            if child.name == "WORLDTREE":
                worldtree_collection = child
                break

    worldtrees = []

    if worldtree_collection:
        worldnodes = [
            obj
            for obj in worldtree_collection.objects
            if obj.get("quaildef") == "worldnode"
        ]

        if worldnodes:
            worldtrees.append((worldtree_collection, worldnodes))

    # Group gathered objects by definition type
    actorinsts = []
    actordefs = []
    simplesprites = []
    materialdefs = []
    materialpalettes = []
    particleclouddefs = []
    blitspritedefs = []
    polyhedrons = []
    sprite3ddefs = []
    dmsprite_defs = []
    dmsprite2_defs = []
    rgbdeformationtrackdefs = []
    lights = []
    regions = []
    zones = []
    hierarchicalsprites = []
    eqgmodels = []
    eqgskinnedmodels = []
    eqgters = []

    for obj in export_objects:
        if isinstance(obj, bpy.types.Collection):
            if obj.get("quaildef") == "actordef":
                actordefs.append(obj)

            continue

        qdef = obj.get("quaildef")

        if not qdef:
            continue

        if qdef == "actorinst":
            actorinsts.append(obj)

        elif qdef == "actordef":
            actordefs.append(obj)

        elif qdef == "hierarchicalspritedef":
            hierarchicalsprites.append(obj)

        elif qdef == "particleclouddef":
            particleclouddefs.append(obj)

        elif qdef == "blitspritedef":
            blitspritedefs.append(obj)

        elif qdef == "light":
            lights.append(obj)

        elif qdef == "zone":
            zones.append(obj)

        elif qdef == "region":
            regions.append(obj)

        elif qdef == "dmspritedefinition":
            dmsprite_defs.append(obj)

        elif qdef == "dmspritedef2":
            dmsprite2_defs.append(obj)

        elif qdef == "sprite3ddef":
            sprite3ddefs.append(obj)

        elif qdef == "rgbdeformationtrackdef":
            rgbdeformationtrackdefs.append(obj)

        elif qdef == "polyhedrondefinition":
            polyhedrons.append(obj)

        elif qdef == "materialpalette":
            materialpalettes.append(obj)

        elif qdef == "materialdefinition":
            materialdefs.append(obj)

        elif qdef == "simplespritedef":
            simplesprites.append(obj)

        elif qdef == "eqgmodeldef":
            eqgmodels.append(obj)

        elif qdef == "eqgskinnedmodeldef":
            eqgskinnedmodels.append(obj)

        elif qdef == "eqgterdef":
            eqgters.append(obj)

    # ------------------------------------------------
    # Encode shared/S3D definitions
    # ------------------------------------------------

    err = encode_globalambientlightdef(parser)
    if err:
        errors.append(err)

    for obj in actorinsts:
        err = encode_actorinst(parser, obj)
        if err:
            errors.append(err)

    for obj in actordefs:
        err = encode_actordef(parser, obj)
        if err:
            errors.append(err)

    for obj in hierarchicalsprites:
        err = encode_hierarchicalspritedef(parser, obj)

        if err:
            errors.append(err)

    # ------------------------------------------------
    # Encode S3D Actions
    # ------------------------------------------------

    s3d_actions = {action for action in export_actions if action.get("quaildef") == "track"}
    if s3d_actions:
        err = encode_track(parser, s3d_actions, context)
        if err:
            errors.append(err)

    for obj in particleclouddefs:
        err = encode_particleclouddef(parser, obj)
        if err:
            errors.append(err)

    for obj in blitspritedefs:
        err = encode_blitspritedef(parser, obj)
        if err:
            errors.append(err)

    for obj in lights:
        err = encode_light(parser, obj)
        if err:
            errors.append(err)

    for obj in zones:
        err = encode_zone(parser, obj)
        if err:
            errors.append(err)

    for collection, nodes in worldtrees:
        err = encode_worldtree(parser, collection, nodes)
        if err:
            errors.append(err)

    for obj in regions:
        err = encode_region(parser, obj)
        if err:
            errors.append(err)

    for obj in dmsprite_defs:
        err = encode_dmspritedefinition(parser, obj)
        if err:
            errors.append(err)

    for obj in dmsprite2_defs:
        err = encode_dmspritedef2(parser, obj)
        if err:
            errors.append(err)

    for obj in rgbdeformationtrackdefs:
        err = encode_rgbdeformationtrackdef(parser, obj)
        if err:
            errors.append(err)

    for obj in sprite3ddefs:
        err = encode_sprite3ddef(parser, obj)
        if err:
            errors.append(err)

    for obj in polyhedrons:
        err = encode_polyhedrondefinition(parser, obj)
        if err:
            errors.append(err)

    for obj in materialpalettes:
        err = encode_materialpalette(parser, obj)
        if err:
            errors.append(err)

    for obj in materialdefs:
        err = encode_materialdefinition(parser, obj)
        if err:
            errors.append(err)

    for obj in simplesprites:
        err = encode_simplespritedef(parser, obj)
        if err:
            errors.append(err)

    # Encode EQG Actions
    # This must happen before EQGMODELDEF because the
    # model encoder reads its encoded POS_* animation.
    for action, armature_obj in export_actions.items():
        if action.get("quaildef") != "eqganidef":
            continue

        err = encode_eqganidef(parser, action, armature_obj)
        if err:
            errors.append(err)

    # ------------------------------------------------
    # Encode EQG models
    # ------------------------------------------------

    for obj in eqgmodels:
        err = encode_eqgmodeldef(parser, obj)
        if err:
            errors.append(err)

    # Add when these encoders are implemented:
    #
    # for obj in eqgskinnedmodels:
    #     err = encode_eqgskinnedmodeldef(parser, obj)
    #
    #     if err:
    #         errors.append(err)
    #
    # for obj in eqgters:
    #     err = encode_eqgterdef(parser, obj)
    #
    #     if err:
    #         errors.append(err)

    # ------------------------------------------------
    # Stop before writing if encoding failed
    # ------------------------------------------------

    if errors:
        return "\n".join(errors)

    # ------------------------------------------------
    # Write Quail folder structure
    # ------------------------------------------------

    folder_name = os.path.basename(folder_path).lower()

    if folder_name.startswith("_objects"):
        err = write_objects_folder(parser, export_objects, folder_path)

    elif folder_name.startswith("_lights"):
        err = write_lights_folder(parser, export_objects, folder_path)

    else:
        err = write_quail_folder(
            parser,
            export_objects,
            folder_path,
            context,
            use_eqg,
        )

    if err:
        return err

    return ""