import io
import pytest
from wce.wce import wce
import os

def read_file(path):
    with open("test/read/" + path, "r") as file_reader:
        data = file_reader.read()
    return io.StringIO(data)

@pytest.mark.parametrize("path", [
    "actordef.wce",
    "actorinst.wce",
    "ambientlight.wce",
    "blitspritedef.wce",
    "dmspritedef2.wce",
    "dmspritedefinition.wce",
    "dmtrackdef2.wce",
    "eqganidef.wce",
    "eqglayerdef.wce",
    "eqgmodeldef.wce",
    "eqgparticlepointdef.wce",
    "eqgparticlerenderdef.wce",
    "eqgskinnedmodeldef.wce",
    "eqgterdef.wce",
    "globalambientlightdef.wce",
    "hierarchicalspritedef.wce",
    "lightdefinition.wce",
    "materialdefinition.wce",
    "materialpalette.wce",
    "particleclouddef.wce",
    "pointlight.wce",
    "polyhedrondefinition.wce",
    "region.wce",
    "rgbdeformationtrackdef.wce",
    "simplespritedef.wce",
    "sprite2ddef.wce",
    "sprite3ddef.wce",
    "trackdefinition.wce",
    "trackinstance.wce",
    "worlddef.wce",
    "worldtree.wce",
    "zone.wce"
])
def test_individual_wce_reader(path):
    try:
        e = wce()
        data = read_file(path)
        e.parse_definitions(path, data)
        print(f"Done with {path}")
    except Exception as ex:
        print(f"Failed to process {path}: {ex}")
        raise ex


@pytest.mark.parametrize("path", [
    "actordef.wce",
    "actorinst.wce",
    "ambientlight.wce",
    "blitspritedef.wce",
    "dmspritedef2.wce",
    "dmspritedefinition.wce",
    "dmtrackdef2.wce",
    "eqganidef.wce",
    "eqglayerdef.wce",
    "eqgmodeldef.wce",
    "eqgparticlepointdef.wce",
    "eqgparticlerenderdef.wce",
    "eqgskinnedmodeldef.wce",
    "eqgterdef.wce",
    "globalambientlightdef.wce",
    "hierarchicalspritedef.wce",
    "lightdefinition.wce",
    "materialdefinition.wce",
    "materialpalette.wce",
    "particleclouddef.wce",
    "pointlight.wce",
    "polyhedrondefinition.wce",
    "region.wce",
    "rgbdeformationtrackdef.wce",
    "simplespritedef.wce",
    "sprite2ddef.wce",
    "sprite3ddef.wce",
    "trackdefinition.wce",
    "trackinstance.wce",
    "worlddef.wce",
    "worldtree.wce",
    "zone.wce"
])
def test_wce_writer(path):
    e = wce()
    data = read_file(path)
    e.parse_definitions(path, data)

    if not os.path.exists("test/write"):
        os.makedirs("test/write")

    w = io.StringIO()
    file_writer = open("test/write/"+path, "w")
    e.write_definitions(file_writer)

    #assert w.getvalue() == data.getvalue(), "Written data does not match the read data"
    print("Done")