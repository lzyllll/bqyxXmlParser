"""默认元素解析器。"""
from __future__ import annotations

from typing import Any

from bqyx_parser.parser.convert import parse_arr
from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.xml import Element, has_attrib, has_children, has_text
from bqyx_parser.tools.gift_str import parse_gift_string


class ObjParser(ElementParser):
    """<obj>"pro":0.35</obj> -> {"pro": 0.35}"""

    def can_parse(self, element: Element) -> bool:
        return element.tag == "obj"

    def parse(self, element: Element) -> Any:
        text = self.text(element)
        if not text:
            return {}
        payload = text if text.startswith("{") else f"{{{text}}}"
        return self.safe_eval(payload)


class EmptyElementParser(ElementParser):
    """空标签 -> None。"""

    def can_parse(self, element: Element) -> bool:
        return not has_text(element) and not has_attrib(element) and not has_children(element)

    def parse(self, element: Element) -> Any:
        return None


class TextElementParser(ElementParser):
    """纯文本标签，例如 <cnName>鬼目枪</cnName>。"""

    def can_parse(self, element: Element) -> bool:
        return has_text(element) and not has_attrib(element) and not has_children(element)

    def parse(self, element: Element) -> Any:
        return self.eval_text(element)


class AttributeElementParser(ElementParser):
    """只有属性的空标签。"""

    def can_parse(self, element: Element) -> bool:
        return has_attrib(element) and not has_text(element) and not has_children(element)

    def parse(self, element: Element) -> dict[str, Any]:
        return self.parse_attribs(element)


class NestedElementParser(ElementParser):
    """有子元素时：属性 + 子元素组成字典。"""

    def can_parse(self, element: Element) -> bool:
        return has_children(element)

    def parse(self, element: Element) -> dict[str, Any]:
        result = self.parse_attribs(element)
        result.update(self.parse_children(element))
        return result


class TagAttribElementParser(ElementParser):
    """同时有文本和属性、没有子元素。"""

    def can_parse(self, element: Element) -> bool:
        return has_text(element) and has_attrib(element) and not has_children(element)

    def parse(self, element: Element) -> dict[str, Any]:
        result = self.parse_attribs(element)
        result["value"] = self.eval_text(element)
        return result


class EndWithArrParser(ElementParser):
    """标签以 Arr 结尾时，按逗号拆成列表。"""

    def parse(self, element: Element) -> list[Any]:
        return parse_arr(self.text(element))


class EndWithBParser(ElementParser):
    """标签以 B 结尾时，1 为 True，其它为 False。"""

    def can_parse(self, element: Element) -> bool:
        return isinstance(element.tag, str) and element.tag.endswith("B") and has_text(element)

    def parse(self, element: Element) -> bool:
        return self.text(element) == "1"


class GiftParser(ElementParser):
    """<gift>things;demStone;25</gift> """
    def can_parse(self, element: Element) -> bool:
        return element.tag == "gift" and self.text(element) is not None
    def parse(self, element: Element) -> list[str]:
        return parse_gift_string(self.text(element))
