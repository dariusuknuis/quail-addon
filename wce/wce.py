import shlex
import io, os

from wce.data.actordef import actordef
from wce.data.actorinst import actorinst
from wce.data.ambientlight import ambientlight
from wce.data.blitspritedef import blitspritedef
from wce.data.dmspritedef2 import dmspritedef2
from wce.data.dmspritedefinition import dmspritedefinition
from wce.data.dmtrackdef2 import dmtrackdef2
from wce.data.eqganidef import eqganidef
from wce.data.eqglayerdef import eqglayerdef
from wce.data.eqgmodeldef import eqgmodeldef
from wce.data.eqgskinnedmodeldef import eqgskinnedmodeldef
from wce.data.eqgterdef import eqgterdef
from wce.data.eqgparticlepointdef import eqgparticlepointdef
from wce.data.eqgparticlerenderdef import eqgparticlerenderdef
from wce.data.globalambientlightdef import globalambientlightdef
from wce.data.hierarchicalspritedef import hierarchicalspritedef
from wce.data.lightdefinition import lightdefinition
from wce.data.materialdefinition import materialdefinition
from wce.data.materialpalette import materialpalette
from wce.data.particleclouddef import particleclouddef
from wce.data.pointlight import pointlight
from wce.data.polyhedrondefinition import polyhedrondefinition
from wce.data.region import region
from wce.data.rgbdeformationtrackdef import rgbdeformationtrackdef
from wce.data.simplespritedef import simplespritedef
from wce.data.sprite2ddef import sprite2ddef
from wce.data.sprite3ddef import sprite3ddef
from wce.data.trackdefinition import trackdefinition
from wce.data.trackinstance import trackinstance
from wce.data.worlddef import worlddef
from wce.data.worldtree import worldtree
from wce.data.zone import zone

class wce:
    actordefs:dict[str, actordef]
    actorinsts:dict[str, actorinst]
    ambientlights:dict[str, ambientlight]
    blitspritedefs:dict[str, blitspritedef]
    dmspritedef2s:dict[str, dmspritedef2]
    dmspritedefinitions:dict[str, dmspritedefinition]
    dmtrackdef2s:dict[str, dmtrackdef2]
    eqganidefs:dict[str, eqganidef]
    eqglayerdefs:dict[str, eqglayerdef]
    eqgmodeldefs:dict[str, eqgmodeldef]
    eqgskinnedmodeldefs:dict[str, eqgskinnedmodeldef]
    eqgterdefs:dict[str, eqgterdef]
    eqgparticlepointdefs:dict[str, eqgparticlepointdef]
    eqgparticlerenderdefs:dict[str, eqgparticlerenderdef]
    globalambientlightdefs:dict[str, globalambientlightdef]
    hierarchicalspritedefs:dict[str, hierarchicalspritedef]
    lightdefinitions:dict[str, lightdefinition]
    materialdefinitions:dict[str, materialdefinition]
    materialpalettes:dict[str, materialpalette]
    particleclouddefs:dict[str, particleclouddef]
    pointlights:dict[str, pointlight]
    polyhedrondefinitions:dict[str, polyhedrondefinition]
    regions:dict[str, region]
    rgbdeformationtrackdefs:dict[str, rgbdeformationtrackdef]
    simplespritedefs:dict[str, simplespritedef]
    sprite2ddefs:dict[str, sprite2ddef]
    sprite3ddefs:dict[str, sprite3ddef]
    trackdefinitions:dict[str, trackdefinition]
    trackinstances:dict[str, trackinstance]
    worlddefs:dict[str, worlddef]
    worldtrees:dict[str, worldtree]
    zones:dict[str, zone]

    def __init__(self):

        self.actordefs = {}
        self.actorinsts = {}
        self.ambientlights = {}
        self.blitspritedefs = {}
        self.dmspritedef2s = {}
        self.dmspritedefinitions = {}
        self.dmtrackdef2s = {}
        self.eqganidefs = {}
        self.eqglayerdefs = {}
        self.eqgmodeldefs = {}
        self.eqgskinnedmodeldefs = {}
        self.eqgterdefs = {}
        self.eqgparticlepointdefs = {}
        self.eqgparticlerenderdefs = {}
        self.globalambientlightdefs = {}
        self.hierarchicalspritedefs = {}
        self.lightdefinitions = {}
        self.materialdefinitions = {}
        self.materialpalettes = {}
        self.particleclouddefs = {}
        self.pointlights = {}
        self.polyhedrondefinitions = {}
        self.regions = {}
        self.rgbdeformationtrackdefs = {}
        self.simplespritedefs = {}
        self.sprite2ddefs = {}
        self.sprite3ddefs = {}
        self.trackdefinitions = {}
        self.trackinstances = {}
        self.worlddefs = {}
        self.worldtrees = {}
        self.zones = {}

    def parse_definitions(self, current_path:str, r:io.TextIOWrapper):
        current_dir = os.path.dirname(current_path)

        defs = {}

        line_number = 0
        for line in r:
            line_number += 1
            line = line.strip()
            records = shlex.split(line)
            if len(records) == 0:
                continue

            path_cursor = f"{current_path}:{line_number}"

            if line.startswith("//"):
                continue
            if line.startswith("INCLUDE"):
                if len(records) != 2:
                    raise Exception(f"{path_cursor} INCLUDE: expected 1 argument, got {len(records)-1}")
                new_path = f"{current_dir}/{records[1].lower()}"
                file_reader = open(new_path, "r")
                data = file_reader.read()
                r = io.StringIO(data)
                self.parse_definitions(new_path, r)
                continue

            tag = ""
            if len(records) > 1:
                tag = records[1]

            if line.startswith(actordef.definition()):
                try:
                    self.actordefs[tag] = actordef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} actordef: {e}")
                continue

            if line.startswith(actorinst.definition()):
                try:
                    self.actorinsts[tag] = actorinst(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} actorinst: {e}")
                continue

            if line.startswith(ambientlight.definition()):
                try:
                    self.ambientlights[tag] = ambientlight(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} ambientlight: {e}")
                continue

            if line.startswith(blitspritedef.definition()):
                try:
                    self.blitspritedefs[tag] = blitspritedef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} blitspritedef: {e}")
                continue

            if line.startswith(dmspritedef2.definition()):
                try:
                    self.dmspritedef2s[tag] = dmspritedef2(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} dmspritedef2: {e}")
                continue

            if line.startswith(dmspritedefinition.definition()):
                try:
                    self.dmspritedefinitions[tag] = dmspritedefinition(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} dmspritedefinition: {e}")
                continue

            if line.startswith(dmtrackdef2.definition()):
                try:
                    self.dmtrackdef2s[tag] = dmtrackdef2(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} dmtrackdef2: {e}")
                continue

            if line.startswith(eqganidef.definition()):
                try:
                    self.eqganidefs[tag] = eqganidef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} eqganidef: {e}")
                continue

            if line.startswith(eqglayerdef.definition()):
                try:
                    self.eqglayerdefs[tag] = eqglayerdef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} eqglayerdef: {e}")
                continue

            if line.startswith(eqgmodeldef.definition()):
                try:
                    self.eqgmodeldefs[tag] = eqgmodeldef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} eqgmodeldef: {e}")
                continue

            if line.startswith(eqgskinnedmodeldef.definition()):
                try:
                    self.eqgskinnedmodeldefs[tag] = eqgskinnedmodeldef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} eqgskinnedmodeldef: {e}")
                continue

            if line.startswith(eqgterdef.definition()):
                try:
                    self.eqgterdefs[tag] = eqgterdef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} eqgterdef: {e}")
                continue

            if line.startswith(eqgparticlepointdef.definition()):
                try:
                    self.eqgterdefs[tag] = eqgparticlepointdef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} eqgparticlepointdef: {e}")
                continue

            if line.startswith(eqgparticlerenderdef.definition()):
                try:
                    self.eqgterdefs[tag] = eqgparticlerenderdef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} eqgparticlerenderdef: {e}")
                continue

            if line.startswith(globalambientlightdef.definition()):
                try:
                    self.globalambientlightdefs[tag] = globalambientlightdef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} globalambientlightdef: {e}")
                continue

            if line.startswith(hierarchicalspritedef.definition()):
                try:
                    self.hierarchicalspritedefs[tag] = hierarchicalspritedef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} hierarchicalspritedef: {e}")
                continue

            if line.startswith(lightdefinition.definition()):
                try:
                    self.lightdefinitions[tag] = lightdefinition(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} lightdefinition: {e}")
                continue

            if line.startswith(materialdefinition.definition()):
                try:
                    self.materialdefinitions[tag] = materialdefinition(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} materialdefinition: {e}")
                continue

            if line.startswith(materialpalette.definition()):
                try:
                    self.materialpalettes[tag] = materialpalette(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} materialpalette: {e}")
                continue

            if line.startswith(particleclouddef.definition()):
                try:
                    self.particleclouddefs[tag] = particleclouddef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} particleclouddef: {e}")
                continue

            if line.startswith(pointlight.definition()):
                try:
                    self.pointlights[tag] = pointlight(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} pointlight: {e}")
                continue

            if line.startswith(polyhedrondefinition.definition()):
                try:
                    self.polyhedrondefinitions[tag] = polyhedrondefinition(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} polyhedrondefinition: {e}")
                continue

            if line.startswith(region.definition()):
                try:
                    self.regions[tag] = region(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} region: {e}")
                continue

            if line.startswith(rgbdeformationtrackdef.definition()):
                try:
                    self.rgbdeformationtrackdefs[tag] = rgbdeformationtrackdef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} rgbdeformationtrackdef: {e}")
                continue

            if line.startswith(simplespritedef.definition()):
                try:
                    self.simplespritedefs[tag] = simplespritedef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} simplespritedef: {e}")
                continue

            if line.startswith(sprite2ddef.definition()):
                try:
                    self.sprite2ddefs[tag] = sprite2ddef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} sprite2ddef: {e}")
                continue

            if line.startswith(sprite3ddef.definition()):
                try:
                    self.sprite3ddefs[tag] = sprite3ddef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} sprite3ddef: {e}")
                continue

            if line.startswith(trackdefinition.definition()):
                try:
                    self.trackdefinitions[tag] = trackdefinition(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} trackdefinition: {e}")
                continue

            if line.startswith(trackinstance.definition()):
                try:
                    self.trackinstances[tag] = trackinstance(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} trackinstance: {e}")
                continue

            if line.startswith(worlddef.definition()):
                try:
                    self.worlddefs[tag] = worlddef(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} worlddef: {e}")
                continue

            if line.startswith(worldtree.definition()):
                try:
                    self.worldtrees[tag] = worldtree(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} worldtree: {e}")
                continue

            if line.startswith(zone.definition()):
                try:
                    self.zones[tag] = zone(tag, r)
                except Exception as e:
                    raise Exception(f"{path_cursor} zone: {e}")
                continue

            raise Exception(f"{path_cursor} unknown tag: {line}")

    def write_definitions(self, w:io.TextIOWrapper):
        for tag, actordefs in self.actordefs.items(): actordefs.write(w)
        for tag, actorinsts in self.actorinsts.items(): actorinsts.write(w)
        for tag, ambientlights in self.ambientlights.items(): ambientlights.write(w)
        for tag, blitspritedefs in self.blitspritedefs.items(): blitspritedefs.write(w)
        for tag, dmspritedef2s in self.dmspritedef2s.items(): dmspritedef2s.write(w)
        for tag, dmspritedefinitions in self.dmspritedefinitions.items(): dmspritedefinitions.write(w)
        for tag, dmtrackdef2s in self.dmtrackdef2s.items(): dmtrackdef2s.write(w)
        for tag, eqganidefs in self.eqganidefs.items(): eqganidefs.write(w)
        for tag, eqglayerdefs in self.eqglayerdefs.items(): eqglayerdefs.write(w)
        for tag, eqgmodeldefs in self.eqgmodeldefs.items(): eqgmodeldefs.write(w)
        for tag, eqgskinnedmodeldefs in self.eqgskinnedmodeldefs.items(): eqgskinnedmodeldefs.write(w)
        for tag, eqgterdefs in self.eqgterdefs.items(): eqgterdefs.write(w)
        for tag, eqgparticlepointdefs in self.eqgparticlepointdefs.items(): eqgparticlepointdefs.write(w)
        for tag, eqgparticlerenderdefs in self.eqgparticlerenderdefs.items(): eqgparticlerenderdefs.write(w)
        for tag, globalambientlightdefs in self.globalambientlightdefs.items(): globalambientlightdefs.write(w)
        for tag, hierarchicalspritedefs in self.hierarchicalspritedefs.items(): hierarchicalspritedefs.write(w)
        for tag, lightdefinitions in self.lightdefinitions.items(): lightdefinitions.write(w)
        for tag, materialdefinitions in self.materialdefinitions.items(): materialdefinitions.write(w)
        for tag, materialpalettes in self.materialpalettes.items(): materialpalettes.write(w)
        for tag, particleclouddefs in self.particleclouddefs.items(): particleclouddefs.write(w)
        for tag, pointlights in self.pointlights.items(): pointlights.write(w)
        for tag, polyhedrondefinitions in self.polyhedrondefinitions.items(): polyhedrondefinitions.write(w)
        for tag, regions in self.regions.items(): regions.write(w)
        for tag, rgbdeformationtrackdefs in self.rgbdeformationtrackdefs.items(): rgbdeformationtrackdefs.write(w)
        for tag, simplespritedefs in self.simplespritedefs.items(): simplespritedefs.write(w)
        for tag, sprite2ddefs in self.sprite2ddefs.items(): sprite2ddefs.write(w)
        for tag, sprite3ddefs in self.sprite3ddefs.items(): sprite3ddefs.write(w)
        for tag, trackdefinitions in self.trackdefinitions.items(): trackdefinitions.write(w)
        for tag, trackinstances in self.trackinstances.items(): trackinstances.write(w)
        for tag, worlddefs in self.worlddefs.items(): worlddefs.write(w)
        for tag, worldtrees in self.worldtrees.items(): worldtrees.write(w)
        for tag, zones in self.zones.items(): zones.write(w)
