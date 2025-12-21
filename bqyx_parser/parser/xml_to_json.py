from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

from bqyx_parser.parser.factory.attrib_factory import AttribParserRegistry, DefaultAttribParser

from bqyx_parser.parser.element.default_parser import AttributeElementParser, EmptyElementParser, ObjParser, TagAttribElementParser, \
    NestedElementParser, TextElementParser, EndWithArrParser, EndWithBParser
from bqyx_parser.parser.factory.element_factory import ElementParserFactory
from lxml import etree


# 创建默认属性解析器注册表
_default_attrib_registry = AttribParserRegistry()
_default_attrib_registry.register_parser(DefaultAttribParser(), priority=0)
# 创建默认工厂
_default_factory = ElementParserFactory(_default_attrib_registry)
_default_factory.register_parser(ObjParser(), priority=7)
#将 <superB>1<superB>   => superB:true
_default_factory.register_parser(EndWithBParser(), priority=6)
#对arr解析成list '1,2,3,4'  => [1,2,3,4]
_default_factory.register_parser(EndWithArrParser(),priority=5)
#  仅仅有 文本内容 child.text
_default_factory.register_parser(TextElementParser(), priority=4)
#  仅仅有 属性attrib
_default_factory.register_parser(AttributeElementParser(), priority=3)
#  有文本、属性、没有子元素
_default_factory.register_parser(TagAttribElementParser(), priority=2)
#  # 有子元素 和 属性 没有文本内容
_default_factory.register_parser(NestedElementParser(), priority=1)
#  啥也没有空情况
_default_factory.register_parser(EmptyElementParser(), priority=0)

import copy
def get_default_factory():
    return copy.deepcopy(_default_factory)
def get_default_attrib_registr():
    return copy.deepcopy(_default_attrib_registry)


def parse_element(child: ET.Element|ET.ElementTree,element_factory=_default_factory) -> Any:
    """
    解析子元素，返回处理后的值
    支持嵌套元素和列表
    使用工厂模式根据元素特征选择合适的解析策略：
    1. <cnName>鬼目枪</cnName>   => "鬼目枪" (TextElementParser)
    2. <lineD lightColor="0xFFCC00" size="2" /> => {"size": 2, "lightColor": "0xFFCC00"} (AttributeElementParser)
    3. 嵌套元素 => {"child1": value1, "child2": value2} (NestedElementParser)
    4. 混合元素 => {"value": text, "attr": value, "child": value} (MixedElementParser)
    """
    return element_factory.parse_element(child)


def parser_xml_root(input_file:Path) -> etree._Element:
    '''
    通过文件名，转为ET Tree 忽略注释
    '''
    # tree = ET.parse(input_file)

    # root = tree.getroot()

    parser = etree.XMLParser(remove_comments=True)
    tree = etree.parse(input_file,parser=parser)
    root = tree.getroot()
    return root


def parse_xml_by_files(input_files: list[Path]) -> list[etree._Element]:
    """
    解析目录及其子目录中的所有XML文件
    
    Args:
        input_files: XML文件路径列表
        
    Returns:
        result 包含所有改所有文件的根
    """
    result = []
    
    for file_path in input_files:
        if file_path.is_file() and file_path.suffix.lower() == '.xml':
            root_element = parser_xml_root(file_path)
            result.append(root_element)
    return result