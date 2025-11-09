"""
XML解析器测试文件
测试各种类型的XML元素解析功能
"""
from pathlib import Path
from pprint import pprint
import xml.etree.ElementTree as ET
import json

from utils.json.save_json import save_to_json
from utils.xml_parse import direct_parse_xml, parse_element
from utils.tag_factory import ElementParserFactory
from utils.attrib_factory import AttribParserRegistry, DefaultAttribParser
from utils.parser.tag.default_parser import (
    TextElementParser, AttributeElementParser, 
    NestedElementParser, TagAttribElementParser, EmptyElementParser
)
from functools import partial





if __name__ == "__main__":
    # XML文件路径
    xml_path = Path(r"C:\Users\lzy\Desktop\dev-bqyx\python\py_bq_xml_to_json\3521_xml\activeTaskClass.xml")
    
    # 解析XML
    root = direct_parse_xml(xml_path)
    ele_dict = parse_element(root)
    
    # 保存为JSON文件
    json_path = save_to_json(ele_dict, xml_path)
    print(f"解析完成！结果已保存到: {json_path}")

