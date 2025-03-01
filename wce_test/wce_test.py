import io
import os
import unittest
from wce.wce import wce

def read_file(path):
    with open("test/read/" + path, "r") as file_reader:
        data = file_reader.read()
    return io.StringIO(data)


class TestWCE(unittest.TestCase):
    def setUp(self):
        self.e = wce()

    def run_test(self, path):
        try:
            data = read_file(path)
            self.e.parse_definitions(path, data)
            #print(f"Done reading {path}")

            if not os.path.exists("test/write"):
                os.makedirs("test/write")

            with open("test/write/" + path, "w") as file_writer:
                self.e.write_definitions(file_writer)
            #print(f"Done writing {path}")
        except Exception as ex:
            print(f"Failed to process {path}: {ex}")
            self.fail(f"Exception raised for {path}: {ex}")

    def test_actordef_wce(self):
        self.run_test("actordef.wce")

    def test_actorinst_wce(self):
        self.run_test("actorinst.wce")

    def test_ambientlight_wce(self):
        self.run_test("ambientlight.wce")

    def test_blitspritedef_wce(self):
        self.run_test("blitspritedef.wce")

    def test_dmspritedef2_wce(self):
        self.run_test("dmspritedef2.wce")

    def test_dmspritedefinition_wce(self):
        self.run_test("dmspritedefinition.wce")

    def test_dmtrackdef2_wce(self):
        self.run_test("dmtrackdef2.wce")

    def test_eqganidef_wce(self):
        self.run_test("eqganidef.wce")

    def test_eqglayerdef_wce(self):
        self.run_test("eqglayerdef.wce")

    def test_eqgmodeldef_wce(self):
        self.run_test("eqgmodeldef.wce")

    def test_eqgparticlepointdef_wce(self):
        self.run_test("eqgparticlepointdef.wce")

    def test_eqgparticlerenderdef_wce(self):
        self.run_test("eqgparticlerenderdef.wce")

    def test_eqgskinnedmodeldef_wce(self):
        self.run_test("eqgskinnedmodeldef.wce")

    def test_eqgterdef_wce(self):
        self.run_test("eqgterdef.wce")

    def test_globalambientlightdef_wce(self):
        self.run_test("globalambientlightdef.wce")

    def test_hierarchicalspritedef_wce(self):
        self.run_test("hierarchicalspritedef.wce")

    def test_lightdefinition_wce(self):
        self.run_test("lightdefinition.wce")

    def test_materialdefinition_wce(self):
        self.run_test("materialdefinition.wce")

    def test_materialpalette_wce(self):
        self.run_test("materialpalette.wce")

    def test_particleclouddef_wce(self):
        self.run_test("particleclouddef.wce")

    def test_pointlight_wce(self):
        self.run_test("pointlight.wce")

    def test_polyhedrondefinition_wce(self):
        self.run_test("polyhedrondefinition.wce")

    def test_region_wce(self):
        self.run_test("region.wce")

    def test_rgbdeformationtrackdef_wce(self):
        self.run_test("rgbdeformationtrackdef.wce")

    def test_simplespritedef_wce(self):
        self.run_test("simplespritedef.wce")

    def test_sprite2ddef_wce(self):
        self.run_test("sprite2ddef.wce")

    def test_sprite3ddef_wce(self):
        self.run_test("sprite3ddef.wce")

    def test_trackdefinition_wce(self):
        self.run_test("trackdefinition.wce")

    def test_trackinstance_wce(self):
        self.run_test("trackinstance.wce")

    def test_worlddef_wce(self):
        self.run_test("worlddef.wce")

    def test_worldtree_wce(self):
        self.run_test("worldtree.wce")

    def test_zone_wce(self):
        self.run_test("zone.wce")


if __name__ == '__main__':
    unittest.main()