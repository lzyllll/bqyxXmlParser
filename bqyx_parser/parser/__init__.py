"""lxml XML 解析框架。"""

from bqyx_parser.parser.attrib.base import AttribParser
from bqyx_parser.parser.attrib.defaults import (
    DefaultAttribParser,
    EndWithArrAttribParser,
    EndWithBAttribParser,
    NameAttribParser,
)
from bqyx_parser.parser.convert import auto_convert, parse_arr, parse_bool_flag, safe_eval
from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.element.defaults import (
    AttributeElementParser,
    EmptyElementParser,
    EndWithArrParser,
    EndWithBParser,
    NestedElementParser,
    ObjParser,
    TagAttribElementParser,
    TextElementParser,
)
from bqyx_parser.parser.factory import (
    AttribParserFactory,
    AttribParserRegistry,
    ElementParserFactory,
    create_attrib_factory,
    create_attrib_registry,
    create_factory,
)
from bqyx_parser.parser.xml import (
    Element,
    load_xml,
    load_xml_files,
    parse_element,
    parse_xml,
)

__all__ = [
    "AttribParser",
    "AttribParserFactory",
    "AttribParserRegistry",
    "AttributeElementParser",
    "DefaultAttribParser",
    "Element",
    "ElementParser",
    "ElementParserFactory",
    "EmptyElementParser",
    "EndWithArrAttribParser",
    "EndWithArrParser",
    "EndWithBAttribParser",
    "EndWithBParser",
    "NameAttribParser",
    "NestedElementParser",
    "ObjParser",
    "TagAttribElementParser",
    "TextElementParser",
    "auto_convert",
    "create_attrib_factory",
    "create_attrib_registry",
    "create_factory",
    "load_xml",
    "load_xml_files",
    "parse_arr",
    "parse_bool_flag",
    "parse_element",
    "parse_xml",
    "safe_eval",
]
