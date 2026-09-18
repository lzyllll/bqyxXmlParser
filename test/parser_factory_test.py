import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import unittest

from lxml import etree

from bqyx_parser.parser import (
    AttribParser,
    DefaultAttribParser,
    ElementParser,
    EndWithArrAttribParser,
    EndWithBAttribParser,
    NameAttribParser,
    create_attrib_registry,
    create_factory,
    load_xml,
    parse_element_by_factory,
    parse_xml,
)
from bqyx_parser.parser.convert import auto_convert, parse_arr, safe_eval
from bqyx_parser.parser.element.defaults import NestedElementParser, ObjParser


def elem(xml: str):
    return etree.fromstring(xml)


class TestConvert(unittest.TestCase):
    def test_safe_eval_numbers_and_containers(self):
        self.assertEqual(safe_eval("42"), 42)
        self.assertEqual(safe_eval("3.14"), 3.14)
        self.assertEqual(safe_eval("[1, 2, 3]"), [1, 2, 3])
        self.assertEqual(safe_eval("{'key': 'value'}"), {"key": "value"})

    def test_safe_eval_keeps_plain_text(self):
        self.assertEqual(safe_eval("filter"), "filter")
        self.assertEqual(safe_eval("鬼目枪"), "鬼目枪")

    def test_auto_convert_bool_suffix(self):
        self.assertTrue(auto_convert("superB", "true"))
        self.assertTrue(auto_convert("enableB", "1"))
        self.assertFalse(auto_convert("disableB", "false"))
        self.assertFalse(auto_convert("offB", "0"))

    def test_auto_convert_arr_suffix(self):
        self.assertEqual(auto_convert("medelProArr", "specialPartsDropPro"), ["specialPartsDropPro"])
        self.assertEqual(auto_convert("skillArr", "a,b,c"), ["a", "b", "c"])
        self.assertEqual(auto_convert("medelProArr", ""), [])
        self.assertEqual(parse_arr("a,,b,"), ["a", "b"])
        self.assertEqual(parse_arr("76,84"), [76, 84])
        self.assertEqual(parse_arr("1,foo,0.5"), [1, "foo", 0.5])
        self.assertEqual(parse_arr("1,2,3", int), [1, 2, 3])
        self.assertEqual(parse_arr("a,b", str.upper), ["A", "B"])


class TestAttribRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = create_attrib_registry()

    def test_parse_mixed_attributes(self):
        element = elem('<item size="2" name="test" activeB="1" tags="[1, 2]"/>')
        result = {}
        self.registry.parse(element, result)
        self.assertEqual(result["size"], 2)
        self.assertEqual(result["name"], "test")
        self.assertTrue(result["activeB"])
        self.assertEqual(result["tags"], [1, 2])

    def test_arr_attributes(self):
        result = self.registry.parse(elem('<achieve medelProArr="specialPartsDropPro" skillArr="a,b,c"/>'))
        self.assertEqual(result["medelProArr"], ["specialPartsDropPro"])
        self.assertEqual(result["skillArr"], ["a", "b", "c"])

    def test_empty_arr_attribute(self):
        result = self.registry.parse(elem('<achieve medelProArr=""/>'))
        self.assertEqual(result["medelProArr"], [])

    def test_drop_level_arr_ints(self):
        result = self.registry.parse(elem('<item dropLevelArr="1,2,999"/>'))
        self.assertEqual(result["dropLevelArr"], [1, 2, 999])

    def test_arr_custom_item_parser(self):
        registry = create_attrib_registry()
        registry.register_name("colorArr", EndWithArrAttribParser(str.upper))
        result = registry.parse(elem('<item colorArr="red,blue"/>'))
        self.assertEqual(result["colorArr"], ["RED", "BLUE"])

    def test_empty_attributes(self):
        result = {}
        self.registry.parse(elem("<item/>"), result)
        self.assertEqual(result, {})

    def test_get_parser(self):
        element = elem('<item name="a" size="2" activeB="1" medelProArr="x"/>')
        self.assertIsInstance(self.registry.get_parser("size", "2", element), DefaultAttribParser)
        self.assertIsInstance(self.registry.get_parser("name", "a", element), NameAttribParser)
        self.assertIsInstance(self.registry.get_parser("activeB", "1", element), EndWithBAttribParser)
        self.assertIsInstance(self.registry.get_parser("medelProArr", "x", element), EndWithArrAttribParser)

    def test_register_name(self):
        class HexParser(AttribParser):
            def parse(self, key, value, element=None):
                return int(value, 16)

        registry = create_attrib_registry()
        registry.register_name("lightColor", HexParser())
        result = registry.parse(elem('<lineD lightColor="0xFFCC00" size="2"/>'))
        self.assertEqual(result["lightColor"], 0xFFCC00)
        self.assertEqual(result["size"], 2)

    def test_register_suffix(self):
        class UrlParser(AttribParser):
            def parse(self, key, value, element=None):
                return f"https://{value}"

        registry = create_attrib_registry()
        registry.register_suffix("Url", UrlParser())
        result = registry.parse(elem('<item iconUrl="img.png" name="a"/>'))
        self.assertEqual(result["iconUrl"], "https://img.png")
        self.assertEqual(result["name"], "a")

    def test_custom_parser_wins(self):
        class RangeParser(AttribParser):
            def can_parse(self, key, value, element=None):
                return key == "range"

            def parse(self, key, value, element=None):
                return [float(item) for item in value.split(",") if item != ""]

        registry = create_attrib_registry()
        registry.register(RangeParser(), 100)
        result = registry.parse(elem('<addD range="0.03,0.12"/>'))
        self.assertEqual(result["range"], [0.03, 0.12])


class TestDefaultParsers(unittest.TestCase):
    def setUp(self):
        self.factory = create_factory()

    def test_text_element(self):
        self.assertEqual(self.factory.parse(elem("<cnName>鬼目枪</cnName>")), "鬼目枪")
        self.assertEqual(self.factory.parse(elem("<cd>120</cd>")), 120)

    def test_attribute_element(self):
        result = self.factory.parse(elem('<lineD lightColor="0xFFCC00" size="2"/>'))
        self.assertEqual(result["size"], 2)
        self.assertEqual(result["lightColor"], 0xFFCC00)

    def test_parse_attribs_rename_keys(self):
        parser = self.factory.get_parser(elem('<item name="a" cnName="test" activeB="1"/>'))
        result = parser.parse_attribs(
            elem('<item name="a" cnName="test" activeB="1"/>'),
            rename_keys={"cnName": "nameCn", "activeB": "active"},
        )
        self.assertEqual(result["name"], "a")
        self.assertEqual(result["nameCn"], "test")
        self.assertTrue(result["active"])
        self.assertNotIn("cnName", result)
        self.assertNotIn("activeB", result)

    def test_factory_rename_maps(self):
        factory = create_factory(rename_maps={
            "attrib": {"cnName": "nameCn"},
            "element": {"addObjJson": "addObj"},
        })
        result = factory.parse(elem("""
            <item cnName="test">
                <addObjJson>"pro":1</addObjJson>
            </item>
        """))
        self.assertEqual(result["nameCn"], "test")
        self.assertNotIn("cnName", result)
        self.assertEqual(result["addObj"], {"pro": 1})
        self.assertNotIn("addObjJson", result)

    def test_parse_rename_override_factory_map(self):
        factory = create_factory(rename_maps={"attrib": {"cnName": "nameCn"}})
        parser = factory.get_parser(elem('<item cnName="test"/>'))
        result = parser.parse_attribs(
            elem('<item cnName="test"/>'),
            rename_keys={"cnName": "title"},
        )
        self.assertEqual(result["title"], "test")
        self.assertNotIn("nameCn", result)
        self.assertNotIn("cnName", result)

    def test_factory_force_list_for(self):
        factory = create_factory(force_list_for={"gift"})
        result = factory.parse(elem("""
            <item>
                <gift>things;demStone;25</gift>
                <name>single</name>
            </item>
        """))
        self.assertEqual(result["gift"], [{"type": "things", "name": "demStone", "num": 25}])
        self.assertEqual(result["name"], "single")

    def test_factory_add_force_list_for(self):
        factory = create_factory()
        factory.add_force_list_for("gift")
        result = factory.parse(elem("""
            <item>
                <gift>things;demStone;25</gift>
            </item>
        """))
        self.assertEqual(result["gift"], [{"type": "things", "name": "demStone", "num": 25}])

    def test_parse_children_merge_factory_and_local_force_list(self):
        factory = create_factory(force_list_for={"gift"})
        class CustomParser(ElementParser):
            def can_parse(self, element):
                return element.tag == "custom"
            def parse(self, element):
                return self.parse_children(element, force_list_for={"extra"})

        factory.register_parser(CustomParser(), 100)
        result = factory.parse(elem("""
            <custom>
                <gift>things;demStone;25</gift>
                <extra>123</extra>
                <single>456</single>
            </custom>
        """))
        self.assertEqual(result["gift"], [{"type": "things", "name": "demStone", "num": 25}])
        self.assertEqual(result["extra"], [123])
        self.assertEqual(result["single"], 456)

    def test_tag_and_attrib(self):
        result = self.factory.parse(elem('<addD pro="mul" range="0.03,0.12">1.5</addD>'))
        self.assertEqual(result["pro"], "mul")
        self.assertEqual(result["value"], 1.5)

    def test_obj_parser(self):
        self.assertEqual(self.factory.parse(elem('<obj>"pro":0.35</obj>')), {"pro": 0.35})
        self.assertIsInstance(self.factory.get_parser(elem('<obj>"pro":0.35</obj>')), ObjParser)

    def test_bool_and_arr_suffix(self):
        self.assertTrue(self.factory.parse(elem("<noBeClearB>1</noBeClearB>")))
        self.assertFalse(self.factory.parse(elem("<noBeClearB>0</noBeClearB>")))
        self.assertEqual(
            self.factory.parse(elem("<effectInfoArr>减少弹药消耗,增加伤害输出</effectInfoArr>")),
            ["减少弹药消耗", "增加伤害输出"],
        )
        self.assertEqual(self.factory.parse(elem("<dropLevelArr>76,84</dropLevelArr>")), [76, 84])

    def test_arr_attribute_via_element_factory(self):
        result = self.factory.parse(elem('<achieve name="endless10" medelProArr="specialPartsDropPro"/>'))
        self.assertEqual(result["name"], "endless10")
        self.assertEqual(result["medelProArr"], ["specialPartsDropPro"])

    def test_nested_and_repeated_tags(self):
        result = self.factory.parse(elem("""
            <skill name="狂暴">
                <cd>100</cd>
                <target>me</target>
                <obj>"pro":0.1</obj>
            </skill>
        """))
        self.assertEqual(result["name"], "狂暴")
        self.assertEqual(result["cd"], 100)
        self.assertEqual(result["target"], "me")
        self.assertEqual(result["obj"], {"pro": 0.1})
        self.assertIsInstance(self.factory.get_parser(elem("<skill><cd>1</cd></skill>")), NestedElementParser)

    def test_empty_element(self):
        self.assertIsNone(self.factory.parse(elem("<empty/>")))

    def test_comments_are_removed(self):
        root = load_xml(b"<data><!-- ignore --><name>ok</name></data>")
        self.assertEqual(parse_element_by_factory(root, self.factory), {"name": "ok"})


class TestFactoryOverride(unittest.TestCase):
    def test_custom_parser_wins(self):
        class TargetParser(ElementParser):
            def can_parse(self, element):
                return element.tag == "target"

            def parse(self, element):
                return (self.text(element) or "").split(",")

        factory = create_factory()
        factory.register(TargetParser(), 100)
        self.assertEqual(factory.parse(elem("<target>me,range,we</target>")), ["me", "range", "we"])




class TestXmlTools(unittest.TestCase):
    def test_load_xml_from_bytes(self):
        root = load_xml(b"<data><name>ok</name></data>")
        self.assertEqual(root.tag, "data")

    def test_parse_xml(self):
        result = parse_xml(b"<data><cd>9</cd><superB>1</superB></data>")
        self.assertEqual(result["cd"], 9)
        self.assertTrue(result["superB"])

    def test_xmlversion_declaration(self):
        root = load_xml(b'<?xmlversion="1.0" encoding="utf-8"?><data><n>1</n></data>')
        self.assertEqual(root.tag, "data")


if __name__ == "__main__":
    unittest.main()
