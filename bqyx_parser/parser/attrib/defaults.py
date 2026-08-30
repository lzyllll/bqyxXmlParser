"""默认属性解析器。"""
from __future__ import annotations

from typing import Any

from bqyx_parser.parser.attrib.base import AttribParser
from bqyx_parser.parser.convert import parse_arr, parse_bool_flag, safe_eval
from bqyx_parser.parser.xml import Element


class NameAttribParser(AttribParser):
    """name 保持字符串，避免被转成数字。"""

    def parse(self, key: str, value: str, element: Element | None = None) -> str:
        return str(value)


class EndWithBAttribParser(AttribParser):
    """属性名以 B 结尾时，true/1 为 True，其它为 False。"""

    def parse(self, key: str, value: str, element: Element | None = None) -> bool:
        return parse_bool_flag(value)


class EndWithArrAttribParser(AttribParser):
    """属性名以 Arr 结尾时，按逗号拆成列表。"""

    def parse(self, key: str, value: str, element: Element | None = None) -> list[Any]:
        return parse_arr(value)


class DefaultAttribParser(AttribParser):
    """数字、列表、字典自动转换。"""

    def parse(self, key: str, value: str, element: Element | None = None) -> Any:
        return safe_eval(value)
