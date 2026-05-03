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
from .actorinst import encode_actorinst
from .actordef import encode_actordef
from .hierarchicalspritedef import encode_hierarchicalspritedef
from .track import encode_track
from .dmspritedef2 import encode_dmspritedef2
from .rgbdeformationtrackdef import encode_rgbdeformationtrackdef
from .polyhedrondefinition import encode_polyhedrondefinition
from .materialpalette import encode_materialpalette
from .materialdefinition import encode_materialdefinition
from .simplespritedef import encode_simplespritedef
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
        print("CHECK:", tag, "->", tag in parser.variationmaterialtags)

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

def write_model_folder(parser, root_obj, export_objects, root_path):

    model_name = get_model_name(root_obj)
    model_dir = os.path.join(root_path, model_name)

    os.makedirs(model_dir, exist_ok=True)

    # ----------------------------------------
    # Build LOCAL parser (important!)
    # ----------------------------------------
    local_parser = wce(model_dir)
    local_parser.variationmaterialtags = set(parser.variationmaterialtags)

    # Gather ONLY dependencies for this root
    local_objects = gather_export_objects([root_obj], parser)
    local_actions = gather_export_tracks(local_objects)

    # Encode ONLY this model
    encode_actordef(local_parser, root_obj)

    for obj in local_objects:
        qdef = obj.get("quaildef")

        if qdef == "hierarchicalspritedef":
            encode_hierarchicalspritedef(local_parser, obj)

        elif qdef == "dmspritedef2":
            encode_dmspritedef2(local_parser, obj)

        elif qdef == "polyhedrondefinition":
            encode_polyhedrondefinition(local_parser, obj)

        elif qdef == "materialpalette":
            encode_materialpalette(local_parser, obj)

        elif qdef == "materialdefinition":
            encode_materialdefinition(local_parser, obj)

        elif qdef == "simplespritedef":
            encode_simplespritedef(local_parser, obj)

    encode_track(local_parser, local_actions, bpy.context)

    # ----------------------------------------
    # Write MODEL WCE
    # ----------------------------------------
    model_wce_path = os.path.join(model_dir, f"{model_name}.wce")

    with open(model_wce_path, "w") as w:
        w.write("// wcemu v0.0.1\n\n")

        wrote_material_sets = write_materials_and_sprites(local_parser, w, model_dir)

        for obj in local_parser.materialpalettes.values():
            obj.write(w)
            w.write("\n")

        for obj in local_parser.polyhedrondefinitions.values():
            obj.write(w)
            w.write("\n")

        for obj in local_parser.dmspritedef2s.values():
            obj.write(w)
            w.write("\n")

        for t in parser.tracks.values():
            if t.is_pose:
                t.write(w)
                w.write("\n")

        for obj in local_parser.hierarchicalspritedefs.values():
            obj.write(w)
            w.write("\n")

        for obj in local_parser.actordefs.values():
            obj.write(w)
            w.write("\n")

    # ----------------------------------------
    # Animations
    # ----------------------------------------
    wrote_animations = write_animation_folder(local_parser, model_dir)

    # ----------------------------------------
    # Model _root.wce
    # ----------------------------------------
    root_file = os.path.join(model_dir, "_root.wce")

    with open(root_file, "w") as w:

        if wrote_animations:
            w.write("INCLUDE \"ANIMATIONS/_ROOT.WCE\"\n")

        if wrote_material_sets:
            w.write("INCLUDE \"MATERIAL_SETS/_ROOT.WCE\"\n")

        w.write(f"INCLUDE \"{model_name.upper()}.WCE\"\n")

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

def export_simplesprite_images(export_objects, assets_dir):

    written = set()

    for obj in export_objects:

        if not hasattr(obj, "get"):
            continue

        if obj.get("quaildef") != "simplespritedef":
            continue

        tree = obj
        props = tree.quail_simplesprite

        for frame in props.frames:
            for file in frame.files:

                if not file.image_name or not file.file_name:
                    continue

                # ----------------------------------------
                # Normalize filename to lowercase
                # ----------------------------------------
                filename = file.file_name.lower()

                # Deduplicate
                if filename in written:
                    continue

                written.add(filename)

                img = bpy.data.images.get(file.image_name)
                if not img:
                    print(f"WARNING: Missing image {file.image_name}")
                    continue

                dst_path = os.path.join(assets_dir, filename)

                try:
                    if img.packed_file:
                        img.unpack(method='USE_ORIGINAL')

                    src = bpy.path.abspath(img.filepath)

                    if src and os.path.exists(src):
                        shutil.copy2(src, dst_path)
                    else:
                        print(f"Fallback saving image (no source): {filename}")
                        img.save_render(dst_path)

                except Exception as e:
                    print(f"ERROR exporting image {filename}: {e}")

def write_zone_folder(parser, export_objects, root_path):

    print("Writing ZONE structure:", root_path)

    os.makedirs(root_path, exist_ok=True)

    # ----------------------------------------
    # ASSETS
    # ----------------------------------------
    assets_dir = os.path.join(root_path, "assets")
    os.makedirs(assets_dir, exist_ok=True)
    export_simplesprite_images(export_objects, assets_dir)

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

def write_quail_folder(parser, export_objects, root_path):

    print("Writing quail folder:", root_path)

    if parser.worlddef and parser.worlddef.zone:
        return write_zone_folder(parser, export_objects, root_path)

    os.makedirs(root_path, exist_ok=True)

    # ----------------------------------------
    # ASSETS folder (placeholder)
    # ----------------------------------------
    assets_dir = os.path.join(root_path, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    # ----------------------------------------
    # EXPORT TEXTURES
    # ----------------------------------------
    export_simplesprite_images(export_objects, assets_dir)

    # ----------------------------------------
    # WORLD.WCE
    # ----------------------------------------
    write_world_wce(parser, root_path)

    # ----------------------------------------
    # ROOT OBJECTS
    # ----------------------------------------
    roots = get_root_objects(export_objects)
    print("\n=== ROOT OBJECTS ===")
    for r in roots:
        if isinstance(r, bpy.types.Collection):
            print(f"[COLLECTION] {r.name} ({r.get('quaildef')})")
        elif isinstance(r, bpy.types.Object):
            print(f"[OBJECT] {r.name} ({r.get('quaildef')})")
        else:
            print(f"[UNKNOWN] {r}")
    print("====================\n")

    model_dirs = []

    for root in roots:
        name = get_model_name(root)
        write_model_folder(parser, root, export_objects, root_path)
        model_dirs.append(name)

    # ----------------------------------------
    # MAIN _root.wce
    # ----------------------------------------
    root_file = os.path.join(root_path, "_root.wce")

    with open(root_file, "w") as w:

        w.write("INCLUDE \"WORLD.WCE\"\n")

        for name in model_dirs:
            w.write(f"INCLUDE \"{name.upper()}/_ROOT.WCE\"\n")

    return ""

def get_root_objects(export_objects):
    roots = []

    # ----------------------------------------
    # FIRST: collect DMSPRITEDEFs used by regions
    # ----------------------------------------
    region_sprite_tags = set()

    for obj in export_objects:
        if not isinstance(obj, bpy.types.Object):
            continue

        if obj.get("quaildef") != "region":
            continue

        props = obj.quail_region
        if props.sprite:
            region_sprite_tags.add(props.sprite)

    # ----------------------------------------
    # MAIN ROOT LOGIC
    # ----------------------------------------
    for obj in export_objects:

        # ----------------------------------------
        # ACTORDEF collections → ROOT
        # ----------------------------------------
        if isinstance(obj, bpy.types.Collection):
            if obj.get("quaildef") == "actordef":
                roots.append(obj)
            continue

        if not isinstance(obj, bpy.types.Object):
            continue

        qdef = obj.get("quaildef")

        # ----------------------------------------
        # SKIP world structure (always)
        # ----------------------------------------
        if qdef in {"worldnode", "region"}:
            continue

        # ----------------------------------------
        # SKIP DMSPRITEDEFs ONLY if used by regions
        # ----------------------------------------
        if qdef in {"dmspritedef2", "dmspritedefinition"}:
            if obj.name in region_sprite_tags:
                continue

        # ----------------------------------------
        # Skip palettes
        # ----------------------------------------
        if qdef == "materialpalette":
            continue

        # ----------------------------------------
        # Root condition
        # ----------------------------------------
        if obj.parent is None:
            roots.append(obj)

    return roots

def get_model_name(obj):
    name = obj.name.lower()

    if "_" in name:
        return name.split("_")[0]

    return name

def gather_export_tracks(export_objects):

    actions = set()

    # ----------------------------------------
    # Find HS_DEF armatures
    # ----------------------------------------
    for obj in export_objects:

        if not isinstance(obj, bpy.types.Object):
            continue

        if obj.type != 'ARMATURE':
            continue

        if obj.get("quaildef") != "hierarchicalspritedef":
            continue

        model_code = obj.name.replace("_HS_DEF", "")

        # ----------------------------------------
        # Direct action on armature (strongest link)
        # ----------------------------------------
        if obj.animation_data and obj.animation_data.action:
            actions.add(obj.animation_data.action)

        # ----------------------------------------
        # Also gather matching actions by name
        # ----------------------------------------
        for action in bpy.data.actions:
            if action.get("quaildef") != "track":
                continue

            # Match "_AVI", "_HUM", etc
            if action.name.endswith(f"_{model_code}"):
                actions.add(action)

    return actions

def gather_export_objects(root_objects, parser):
    visited = set()
    stack = list(root_objects)

    if any(obj.get("quaildef") == "worldnode" for obj in root_objects if hasattr(obj, "get")):
        for col in bpy.data.collections:
            if col.name == "WORLDTREE":
                for obj in col.objects:
                    if obj.get("quaildef") == "worldnode":
                        stack.append(obj)

    palette_material_tags = set()
    parser.variationmaterialtags.clear()

    def add(obj):
        if obj and obj not in visited:
            stack.append(obj)

    while stack:
        obj = stack.pop()

        if obj in visited:
            continue

        visited.add(obj)

        # ----------------------------------------
        # COLLECTION → expand into objects + subcollections
        # ----------------------------------------
        if isinstance(obj, bpy.types.Collection):
            for child_obj in obj.objects:
                add(child_obj)

            for child_col in obj.children:
                add(child_col)

            continue

        # ----------------------------------------
        # Children (ONLY for Blender Objects)
        # ----------------------------------------
        if isinstance(obj, bpy.types.Object):
            for child in obj.children:
                add(child)

        # ----------------------------------------
        # Safe quaildef access
        # ----------------------------------------
        qdef = obj.get("quaildef") if hasattr(obj, "get") else None

        # ========================================
        # WORLDNODE → REGION
        # ========================================
        if qdef == "worldnode":
            props = obj.quail_worldnode

            if props.region_tag:
                region_obj = bpy.data.objects.get(props.region_tag)

                if region_obj:
                    add(region_obj)

        # ========================================
        # REGION → DMSPRITE
        # ========================================
        elif qdef == "region":
            props = obj.quail_region

            if props.sprite:
                sprite_obj = bpy.data.objects.get(props.sprite)

                if sprite_obj:
                    add(sprite_obj)

        # ----------------------------------------
        # DMSPRITE → MATERIALPALETTE
        # ----------------------------------------
        if qdef == "dmspritedef2":
            props = obj.quail_dmspritedef2
            if props.materialpalette:
                add(props.materialpalette)

        elif qdef == "dmspritedefinition":
            props = obj.quail_dmspritedefinition
            if props.materialpalette:
                add(props.materialpalette)

        # ----------------------------------------
        # MATERIALPALETTE → MATERIALDEFINITION → SIMPLESPRITEDEF
        # ----------------------------------------
        elif qdef == "materialpalette":
            props = obj.quail_materialpalette

            for item in props.materials:
                mat = item.material
                if not mat:
                    continue

                # Add Blender Material
                add(mat)

                # ----------------------------------------
                # MATERIALDEFINITION
                # ----------------------------------------
                if mat.get("quaildef") == "materialdefinition":
                    palette_material_tags.add(mat.name)

                    mprops = mat.quail_materialdefinition
                    sprite_tag = mprops.simplespritetag

                    # ----------------------------------------
                    # SIMPLESPRITEDEF (NodeTree)
                    # ----------------------------------------
                    if sprite_tag and sprite_tag != "NONE":
                        sprite = bpy.data.node_groups.get(sprite_tag)

                        if sprite:
                            add(sprite)
                        else:
                            print(
                                f"WARNING: Missing SimpleSpriteDef '{sprite_tag}' "
                                f"for material '{mat.name}'"
                            )
            # ----------------------------------------
            # SECOND: detect AND ADD variation materials
            # ----------------------------------------
            for mat in bpy.data.materials:

                if mat.get("quaildef") != "materialdefinition":
                    continue

                tag = mat.name

                # skip palette materials
                if tag in palette_material_tags:
                    continue

                if tag in parser.variationmaterialtags:
                    continue

                prefix = material_tag_parse(tag)
                if not prefix:
                    continue

                # match against palette materials
                for palette_tag in palette_material_tags:
                    if palette_tag.startswith(prefix):

                        if mat in visited:
                            continue

                        parser.variationmaterialtags.add(tag)

                        add(mat)

                        # add its sprite too (same as normal path)
                        mprops = mat.quail_materialdefinition
                        sprite_tag = mprops.simplespritetag

                        if sprite_tag and sprite_tag != "NONE":
                            sprite = bpy.data.node_groups.get(sprite_tag)

                            if sprite:
                                add(sprite)
                            else:
                                print(
                                    f"WARNING: Missing SimpleSpriteDef '{sprite_tag}' "
                                    f"for variation material '{mat.name}'"
                                )

                        break

    return visited

def wce_encode(folder_path: str, context, selected_only: bool) -> str:

    # ------------------------------------------------
    # Setup parser (same class as decode)
    # ------------------------------------------------
    parser = wce(folder_path)

    errors = []

    # ------------------------------------------------
    # Build root set
    # ------------------------------------------------
    root_objects = []

    col = context.collection

    # ------------------------------------------------
    # SELECTED EXPORT
    # ------------------------------------------------
    if selected_only:

        # ----------------------------------------
        # Case 1: Active collection is WORLDDEF
        # ----------------------------------------
        if col and col.get("quaildef") == "worlddef":
            root_objects = list(col.objects) + list(col.children)

        # ----------------------------------------
        # Case 2: Active collection is ACTORDEF
        # ----------------------------------------
        elif col and col.get("quaildef") == "actordef":
            root_objects = [col]

        # ----------------------------------------
        # Case 3: Objects selected (normal case)
        # ----------------------------------------
        elif context.selected_objects:
            root_objects = list(context.selected_objects)

        # ----------------------------------------
        # Fallback
        # ----------------------------------------
        else:
            if col:
                root_objects = list(col.objects) + list(col.children)
            else:
                root_objects = []

    # ------------------------------------------------
    # FULL EXPORT (no selection)
    # ------------------------------------------------
    else:
        if col:
            root_objects = list(col.objects) + list(col.children)
        else:
            root_objects = []

    # ------------------------------------------------
    # Gather dependency graph
    # ------------------------------------------------
    export_objects = gather_export_objects(root_objects, parser)
    export_actions = gather_export_tracks(export_objects)

    print("Export set:")
    for obj in export_objects:
        print("  ", obj.name, obj.get("quaildef"))

    # ------------------------------------------------
    # Find WORLDDEF collection
    # ------------------------------------------------
    world_collection = None

    if context.collection and context.collection.get("quaildef") == "worlddef":
        world_collection = context.collection

    else:
        for col in bpy.data.collections:
            if col.get("quaildef") != "worlddef":
                continue

            # skip subfolders like _objects/_lights
            if col.name.lower().startswith("_"):
                continue

            world_collection = col
            break

    if world_collection:
        err = encode_worlddef(parser, world_collection)
        if err:
            errors.append(err)

    # ------------------------------------------------
    # Find WORLDTREE
    # ------------------------------------------------

    worldtree_collection = None

    # check active collection first
    if context.collection and context.collection.name == "WORLDTREE":
        worldtree_collection = context.collection

    # otherwise search children of selected collection
    elif context.collection:
        for child in context.collection.children:
            if child.name == "WORLDTREE":
                worldtree_collection = child
                break

    worldtrees = []

    if worldtree_collection:

        worldnodes = [
            obj for obj in worldtree_collection.objects
            if obj.get("quaildef") == "worldnode"
        ]

        if worldnodes:
            worldtrees.append((worldtree_collection, worldnodes))

    # ------------------------------------------------
    # Gather Blender objects by type (FILTERED SET)
    # ------------------------------------------------
    actorinsts = []
    actordefs = []
    simplesprites = []
    materialdefs = []
    materialpalettes = []
    polyhedrons = []
    dmsprite_defs = []
    dmsprite2_defs = []
    rgbdeformationtrackdefs = []
    lights = []
    regions = []
    tracks = []
    hierarchicalsprites = []
    eqgmodels = []
    eqgters = []
    eqganis = []

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

        if qdef == "actordef":
            actordefs.append(obj)

        elif qdef == "hierarchicalspritedef":
            hierarchicalsprites.append(obj)

        elif qdef == "light":
            lights.append(obj)

        elif qdef == "region":
            regions.append(obj)

        elif qdef == "dmspritedefinition":
            dmsprite_defs.append(obj)

        elif qdef == "dmspritedef2":
            dmsprite2_defs.append(obj)

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

        elif qdef == "eqgterdef":
            eqgters.append(obj)

        elif qdef == "eqganidef":
            eqganis.append(obj)

    # ------------------------------------------------
    # Encode (order matters!)
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

    err = encode_track(parser, export_actions, context)
    if err:
        errors.append(err)

    for obj in lights:
        err = encode_light(parser, obj)
        if err:
            errors.append(err)

    for col, nodes in worldtrees:
        err = encode_worldtree(parser, col, nodes)
        if err:
            errors.append(err)

    for obj in regions:
        err = encode_region(parser, obj)
        if err:
            errors.append(err)


    # for obj in dmsprite_defs:
    #     err = encode_dmspritedefinition(parser, obj)
    #     if err:
    #         errors.append(err)

    for obj in dmsprite2_defs:
        err = encode_dmspritedef2(parser, obj)
        if err:
            errors.append(err)

    for obj in rgbdeformationtrackdefs:
        err = encode_rgbdeformationtrackdef(parser, obj)
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

    # for obj in eqgters:
    #     err = encode_eqgterdef(parser, obj)
    #     if err:
    #         errors.append(err)

    # for obj in eqgmodels:
    #     err = encode_eqgmodeldef(parser, obj)
    #     if err:
    #         errors.append(err)

    # for obj in eqganis:
    #     err = encode_eqganidef(parser, obj)
    #     if err:
    #         errors.append(err)

    # ------------------------------------------------
    # Write full quail folder structure
    # ------------------------------------------------

    if os.path.basename(folder_path).lower().startswith("_objects"):
        return write_objects_folder(parser, export_objects, folder_path)

    if os.path.basename(folder_path).lower().startswith("_lights"):
        return write_lights_folder(parser, export_objects, folder_path)

    err = write_quail_folder(parser, export_objects, folder_path)

    if err:
        return err

    # ------------------------------------------------
    # Return errors if any
    # ------------------------------------------------
    if errors:
        return "\n".join(errors)

    return ""