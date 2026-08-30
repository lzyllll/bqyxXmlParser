"""属性解析器。"""
from bqyx_parser.parser.attrib.base import AttribParser
from bqyx_parser.parser.attrib.defaults import (
    DefaultAttribParser,
    EndWithArrAttribParser,
    EndWithBAttribParser,
    NameAttribParser,
)

__all__ = [
    "AttribParser",
    "DefaultAttribParser",
    "EndWithArrAttribParser",
    "EndWithBAttribParser",
    "NameAttribParser",
]
