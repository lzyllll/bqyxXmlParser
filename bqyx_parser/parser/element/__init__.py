"""元素解析器。"""
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

__all__ = [
    "ElementParser",
    "AttributeElementParser",
    "EmptyElementParser",
    "EndWithArrParser",
    "EndWithBParser",
    "NestedElementParser",
    "ObjParser",
    "TagAttribElementParser",
    "TextElementParser",
]
