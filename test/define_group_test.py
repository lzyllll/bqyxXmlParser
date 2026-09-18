import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import json
import tempfile
import unittest

from bqyx_parser.extractor.as3 import BqAS3Parser
from bqyx_parser.extractor.define_group import (
    extract_define_modules,
    save_define_modules_json,
)

SAMPLE_DEFINE_GROUP = """
package dataAll._data
{
   public class DefineGroup
   {
      public function init() : *
      {
         this.imageUrl.inData_byXML(out0.imageUrl);
         this.imageUrl.inData_byXML(out0.imageUrlNew);
         this.food.raw.inData_byXML(out0.foodRaw);
         this.body.inData_byXML(out0["hero"], BodySystemType.DEFINE_HERO);
         this.body.inData_byXML(out0["enemy"], BodySystemType.DEFINE_NORMAL);
         this.inBodyXml(out0.XiaoHu, BodySystemType.DEFINE_HERO);
         this.bullet.inData_byXML(out0["bullet"]);
         this.bullet.inArmsRangeData_byXML(out0.pistol);
         this.inArmsXml(out0.laser1);
         this.inArmsXml(out0.pistolFox, true);
         this.skill.inData_byXML(out0["skill"]);
         this.union.inXml(out0["military"], out0["unionData"], out0.unionTask);
         this.vehicle.inData_byXML(out0.vehicle);
         this.inVehicleXml(out0._00_DesertTank);
         this.inDeviceXml(out0.hammerMine);
         this.inCraftXml(out0._00_SilverShip);
         this.device.inData_byXML(out0.device);
         BCardPKCreator.inXml(out0.bcardPK);
         this.equipCreator.propertyCtreator.inData_byXML(out0["equipRange"]);
      }
   }
}
"""


class TestExtractDefineModules(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.as_path = Path(self.tmp.name) / "DefineGroup.as"
        self.as_path.write_text(SAMPLE_DEFINE_GROUP, encoding="utf-8")
        self.data = extract_define_modules(self.as_path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_module_keys_order_starts_with_core(self):
        keys = list(self.data)
        self.assertEqual(keys[:4], ["body", "bullet", "skill", "vehicle"])

    def test_direct_modules(self):
        self.assertEqual(self.data["imageUrl"], ["imageUrl", "imageUrlNew"])
        self.assertEqual(self.data["food"], ["foodRaw"])
        self.assertEqual(self.data["device"], ["hammerMine", "device"])
        self.assertEqual(self.data["union"], ["military", "unionData", "unionTask"])
        self.assertEqual(self.data["BCardPKCreator"], ["bcardPK"])
        self.assertEqual(self.data["equipCreator"], ["equipRange"])

    def test_body_includes_direct_and_dispatch(self):
        self.assertEqual(
            self.data["body"],
            [
                "hero",
                "enemy",
                "XiaoHu",
                "_00_DesertTank",
                "hammerMine",
                "_00_SilverShip",
            ],
        )

    def test_bullet_includes_arms_and_dispatch(self):
        self.assertIn("bullet", self.data["bullet"])
        self.assertIn("pistol", self.data["bullet"])
        self.assertIn("laser1", self.data["bullet"])
        self.assertIn("pistolFox", self.data["bullet"])
        self.assertIn("XiaoHu", self.data["bullet"])
        self.assertIn("_00_DesertTank", self.data["bullet"])
        self.assertIn("hammerMine", self.data["bullet"])
        self.assertIn("_00_SilverShip", self.data["bullet"])

    def test_skill_includes_direct_and_dispatch(self):
        self.assertIn("skill", self.data["skill"])
        self.assertIn("XiaoHu", self.data["skill"])
        self.assertIn("laser1", self.data["skill"])
        self.assertIn("pistolFox", self.data["skill"])
        self.assertIn("_00_DesertTank", self.data["skill"])
        self.assertIn("hammerMine", self.data["skill"])
        self.assertIn("_00_SilverShip", self.data["skill"])

    def test_vehicle_and_craft(self):
        self.assertEqual(self.data["vehicle"], ["vehicle", "_00_DesertTank"])
        self.assertEqual(self.data["craft"], ["_00_SilverShip"])
        self.assertIn("_00_SilverShip", self.data["peakPro"])

    def test_save_json(self):
        out = Path(self.tmp.name) / "define_modules.json"
        saved = save_define_modules_json(self.data, out)
        self.assertTrue(saved.exists())
        loaded = json.loads(saved.read_text(encoding="utf-8"))
        self.assertEqual(loaded["body"], self.data["body"])
        self.assertEqual(loaded["union"], self.data["union"])


class TestBqAS3ParserDefineModules(unittest.TestCase):
    def test_missing_file_returns_empty(self):
        parser = BqAS3Parser()
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(parser.extract_define_modules(Path(tmp)), {})

    def test_extract_from_project_scripts(self):
        parser = BqAS3Parser()
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            as_path = project / "dataAll" / "_data" / "DefineGroup.as"
            as_path.parent.mkdir(parents=True)
            as_path.write_text(SAMPLE_DEFINE_GROUP, encoding="utf-8")
            data = parser.extract_define_modules(project)
            self.assertIn("body", data)
            self.assertIn("hero", data["body"])
            self.assertIn("XiaoHu", data["body"])


if __name__ == "__main__":
    unittest.main()
