"""默认属性解析器。"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bqyx_parser.parser.attrib.base import AttribParser
from bqyx_parser.parser.convert import parse_arr, parse_bool_flag, safe_eval
from bqyx_parser.parser.xml import Element, has_text
from bqyx_parser.tools.split import clean_split_text

class addObjJsonAttribParser(AttribParser):
    def parse(self, key: str, value: str, element: Element | None = None) -> str:
        if not value:
            return {}
        payload = value if value.startswith("{") else f"{{{value}}}"
        return safe_eval(payload)
    
class NameAttribParser(AttribParser):
    """name 保持字符串，避免被转成数字。"""

    def parse(self, key: str, value: str, element: Element | None = None) -> str:
        return str(value)


class EndWithBAttribParser(AttribParser):
    """属性名以 B 结尾时，true/1 为 True，其它为 False。"""

    def parse(self, key: str, value: str, element: Element | None = None) -> bool:
        return parse_bool_flag(value)


class EndWithArrAttribParser(AttribParser):
    """
    属性名以 Arr 结尾时，按逗号拆成列表。
    """

    def __init__(self, item_parser: Callable[[str], Any] = safe_eval):
        self.item_parser = item_parser

    def parse(self, key: str, value: str, element: Element | None = None) -> list[Any]:

        return parse_arr(value, self.item_parser)


class DefaultAttribParser(AttribParser):
    """数字、列表、字典自动转换。"""

    def parse(self, key: str, value: str, element: Element | None = None) -> Any:
        return safe_eval(value)


class lightColorParser(AttribParser):
    '''将lineD解析为str 为颜色'''
    def parse(self, key: str, value: str, element: Element | None = None) -> Any:
        return str(value)
    
class ParserArrAttribParser(AttribParser):
    """<xxx>1,2,3</xxx> -> [1, 2, 3]"""
    def can_parse(self, key: str, value: str, element: Element | None = None) -> bool:
        if element is not None and key is not None and value is not None:
            if ',' in value:
                return True
        return False

    def parse(self, key: str, value: str, element: Element | None = None) -> Any:
        return parse_arr(value,)