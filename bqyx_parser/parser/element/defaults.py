"""默认元素解析器。"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from bqyx_parser.parser.convert import parse_arr, safe_eval
from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.xml import Element, has_attrib, has_children, has_text, is_element
from bqyx_parser.tools.gift_str import parse_gift_string
from bqyx_parser.tools.split import clean_split_text


class HurtArrParser(ElementParser):
    """
    <hurtArr>
        <hurt>
            <imgLabel>normalAttack1</imgLabel>
            <hurtRatio>0.15</hurtRatio>
            <shakeValue>4</shakeValue>
            <attackType>direct</attackType>
            <hitImgUrl con="add" raNum="30" soundUrl="Striker/hit1">bladeHitEffect/blood</hitImgUrl>
        </hurt>
    <hurtArr>
    
    """

    def can_parse(self, element: Element) -> bool:
        return element.tag == "hurtArr" and has_children(element)

    def parse(self, element: Element) -> dict[str, Any]:
        return [self.parser_element(child) for child in element]



class EndWithRectParser(ElementParser):
    """标签以 Rect 结尾时，按逗号拆成字典。"""

    def can_parse(self, element: Element) -> bool:
        return isinstance(element.tag, str) and element.tag.endswith("Rect") and has_text(element)

    def parse(self, element: Element) -> dict[str, Any]:
        key = ["x", "y", "width", "height"]
        value = [float(a) for a in clean_split_text(element.text, ",")]
        return dict(zip(key, value))

class hurtRectArrParser(ElementParser):
    """<hurtRectArr>-12.0,-50.0,24.0,50.0</hurtRectArr> -> {'x': -12.0, 'y': -50.0, 'width': 24.0, 'height': 50.0}"""

    def parse(self, element):
        key = ['x', 'y', 'width', 'height']
        value = [float(a) for a in clean_split_text(element.text, ',')]
        return dict(zip(key, value))



class ParserArrParser(ElementParser):
    """<xxx>1,2,3</xxx> -> [1, 2, 3]"""

    def can_parse(self, element: Element) -> bool:
        if has_text(element):
            if ',' in element.text:
                return True
        return False

    def parse(self, element: Element) -> list[Any]:
        return [safe_eval(a) for a in clean_split_text(element.text, ',')]

class addObjJsonParser(ElementParser):
    def parse(self, element):
        text = self.text(element)
        if not text:
            return {}
        payload = text if text.startswith("{") else f"{{{text}}}"
        return self.safe_eval(payload)
    
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
    """只有属性的空标签。属性名走工厂 rename_maps["attrib"]。"""

    def can_parse(self, element: Element) -> bool:
        return has_attrib(element) and not has_text(element) and not has_children(element)

    def parse(self, element: Element) -> dict[str, Any]:
        return self.parse_attribs(element)


class NestedElementParser(ElementParser):
    """有子元素时：属性 + 子元素组成字典。改名走工厂 rename_maps。"""

    def can_parse(self, element: Element) -> bool:
        return has_children(element)

    def parse(self, element: Element) -> dict[str, Any]:
        result = self.parse_attribs(element)
        result.update(self.parse_children(element))
        return result


class TagAttribElementParser(ElementParser):
    """同时有文本和属性、没有子元素。属性名走工厂 rename_maps["attrib"]。"""

    def can_parse(self, element: Element) -> bool:
        return has_text(element) and has_attrib(element) and not has_children(element)

    def parse(self, element: Element) -> dict[str, Any]:
        result = self.parse_attribs(element)
        result["_text"] = self.eval_text(element)
        return result


class EndWithArrParser(ElementParser):
    """
    标签以 Arr或ArrCn 结尾时，按逗号拆成列表。并且需要有text
    例
        如：<xxxArr>1,2,3</xxxArr> -> [1, 2, 3]
        过滤掉以下
        <xxxArr>
            <child></child>
        </xxxArr>
    """

    def __init__(self, item_parser: Callable[[str], Any] = safe_eval, factory=None, attrib_registry=None):
        super().__init__(factory, attrib_registry)
        self.item_parser = item_parser
    def can_parse(self, element: Element) -> bool:
        return has_text(element)

    def parse(self, element: Element) -> list[Any]:
        return parse_arr(self.text(element), self.item_parser)


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
