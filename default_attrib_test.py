import unittest
import xml.etree.ElementTree as ET
from typing import Dict, Any

from utils.xml_parse import get_default_attrib_registr
from utils.attrib_factory import AttribParserRegistry
from utils.parser.attrib.default_parser import DefaultAttribParser


class TestDefaultAttribRegistry(unittest.TestCase):
    """测试默认属性解析器注册表"""
    
    def setUp(self):
        """每个测试方法执行前的准备工作"""
        self.attrib_registr = get_default_attrib_registr()
    
    def test_get_default_attrib_registr(self):
        """测试获取默认属性注册表"""
        self.assertIsNotNone(self.attrib_registr)
        self.assertIsInstance(self.attrib_registr, AttribParserRegistry)
    
    def test_parse_simple_attributes(self):
        """测试解析简单属性"""
        # 创建测试元素: <element size="2" name="test" />
        element = ET.Element("element")
        element.set("size", "2")
        element.set("name", "test")
        
        result = {}
        self.attrib_registr.parse(element, result)
        
        self.assertEqual(result["size"], 2)  # 应该转换为整数
        self.assertEqual(result["name"], "test")  # 字符串保持不变
    
    def test_parse_numeric_attributes(self):
        """测试解析数字属性"""
        element = ET.Element("element")
        element.set("int_val", "42")
        element.set("float_val", "3.14")
        element.set("list_val", "[1, 2, 3]")
        
        result = {}
        self.attrib_registr.parse(element, result)
        
        self.assertEqual(result["int_val"], 42)
        self.assertEqual(result["float_val"], 3.14)
        self.assertEqual(result["list_val"], [1, 2, 3])
    
    def test_parse_boolean_attributes(self):
        """测试解析布尔属性（以B结尾的属性）"""
        element = ET.Element("element")
        element.set("superB", "true")
        element.set("enableB", "1")
        element.set("disableB", "false")
        element.set("offB", "0")
        
        result = {}
        self.attrib_registr.parse(element, result)
        
        self.assertEqual(result["superB"], True)
        self.assertEqual(result["enableB"], True)
        self.assertEqual(result["disableB"], False)
        self.assertEqual(result["offB"], False)
    
    def test_parse_keyword_attributes(self):
        """测试解析关键字属性（如filter）"""
        element = ET.Element("element")
        element.set("filter", "filter")
        element.set("if_val", "if")
        
        result = {}
        self.attrib_registr.parse(element, result)
        
        self.assertEqual(result["filter"], "filter")
        self.assertEqual(result["if_val"], "if")
    
    def test_parse_dict_attributes(self):
        """测试解析字典属性"""
        element = ET.Element("element")
        element.set("config", "{'key': 'value', 'num': 123}")
        
        result = {}
        self.attrib_registr.parse(element, result)
        
        self.assertIsInstance(result["config"], dict)
        self.assertEqual(result["config"]["key"], "value")
        self.assertEqual(result["config"]["num"], 123)
    
    def test_parse_empty_attributes(self):
        """测试解析空属性"""
        element = ET.Element("element")
        
        result = {}
        self.attrib_registr.parse(element, result)
        
        # 没有属性时，result应该为空
        self.assertEqual(len(result), 0)
    
    def test_parse_mixed_attributes(self):
        """测试解析混合类型的属性"""
        element = ET.Element("element")
        element.set("name", "test")
        element.set("count", "10")
        element.set("price", "99.99")
        element.set("activeB", "true")
        element.set("tags", "['tag1', 'tag2']")
        
        result = {}
        self.attrib_registr.parse(element, result)
        
        self.assertEqual(result["name"], "test")
        self.assertEqual(result["count"], 10)
        self.assertEqual(result["price"], 99.99)
        self.assertEqual(result["activeB"], True)
        self.assertEqual(result["tags"], ['tag1', 'tag2'])
    
    def test_get_parser(self):
        """测试获取解析器"""
        element = ET.Element("element")
        element.set("test", "value")
        
        parser = self.attrib_registr.get_parser(element)
        self.assertIsNotNone(parser)
        self.assertIsInstance(parser, DefaultAttribParser)
    
    def test_get_registered_parsers(self):
        """测试获取已注册的解析器列表"""
        parsers = self.attrib_registr.get_registered_parsers()
        self.assertIsInstance(parsers, list)
        self.assertGreater(len(parsers), 0)


if __name__ == '__main__':
    unittest.main()