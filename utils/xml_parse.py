from typing import Any
import xml.etree.ElementTree as ET

from utils.attrib_factory import AttribParserRegistry, DefaultAttribParser

from utils.parser.tag.default_parser import  AttributeElementParser,  EmptyElementParser, TagAttribElementParser, NestedElementParser, TextElementParser
from utils.tag_factory import ElementParserFactory



# 创建默认属性解析器注册表
_default_attrib_registry = AttribParserRegistry()
_default_attrib_registry.register_parser(DefaultAttribParser(), priority=0)
# 创建默认工厂
_default_factory = ElementParserFactory(_default_attrib_registry)

#  仅仅有 文本内容 child.text
_default_factory.register_parser(TextElementParser(), priority=40)
#  仅仅有 属性attrib
_default_factory.register_parser(AttributeElementParser(), priority=35)
#  有文本、属性、没有子元素
_default_factory.register_parser(TagAttribElementParser(), priority=30)
#  # 有子元素 和 属性 没有文本内容
_default_factory.register_parser(NestedElementParser(), priority=20)
#  啥也没有空情况
_default_factory.register_parser(EmptyElementParser(), priority=0)

import copy
def get_default_factory():
    return copy.deepcopy(_default_factory)
def get_default_attrib_registr():
    return copy.deepcopy(_default_attrib_registry)


def parse_element(child: ET.Element,element_factory=_default_factory) -> Any:
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


def direct_parse_xml(name) ->  ET.ElementTree:
    '''
    通过文件名，转为ET Tree
    '''
    tree = ET.parse(name)

    root = tree.getroot()
    
    return root
