"""元素解析器基类。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Optional, Set

from lxml import etree

from bqyx_parser.parser.convert import safe_eval
from bqyx_parser.parser.xml import Element, element_text, eval_text

if TYPE_CHECKING:
    from bqyx_parser.parser.factory import AttribParserRegistry, ElementParserFactory


class ElementParser(ABC):
    """自定义解析器基类。注册到工厂时会注入 factory 和 attrib_registry。"""

    def __init__(self, factory=None, attrib_registry=None):
        self.factory: ElementParserFactory | None = factory
        self.attrib_registry: AttribParserRegistry | None = attrib_registry

    def set_factory(self, factory) -> None:
        self.factory = factory

    def set_attrib_registry(self, registry) -> None:
        self.attrib_registry = registry

    def safe_eval(self, value: Any) -> Any:
        return safe_eval(value)

    def text(self, element: Element) -> str | None:
        return element_text(element)

    def eval_text(self, element: Element) -> Any:
        return eval_text(element)

    def parse_attribs(self, element: Element, result: dict[str, Any] | None = None) -> dict[str, Any]:
        """解析当前元素属性。"""
        result = {} if result is None else result
        if self.attrib_registry is not None:
            self.attrib_registry.parse(element, result)
        return result

    def group_children(self, element: Element) -> dict[str, list[Element]]:
        """按标签把子元素分组。"""
        groups: dict[str, list[Element]] = defaultdict(list)
        for child in element:
            if isinstance(child.tag, str):
                groups[child.tag].append(child)
        return dict(groups)

    def parse_children(
        self,
        element: Element,
        force_list_for: Optional[Set[str]] = None
    ) -> dict[str, Any]:
        """
        解析子元素，同名多个变为列表，单个默认取单值。
        
        Args:
            element: 要解析的父元素
            force_list_for: 强制转换为列表的标签集合（即使只有一个孩子也返回列表）
        
        Returns:
            字典，键为标签名，值为解析结果（单值或列表）
        """
        if self.factory is None:
            raise RuntimeError("ElementParser.factory 尚未绑定")

        if force_list_for is None:
            force_list_for = set()  # 默认空集合，行为与原逻辑一致

        result: dict[str, Any] = {}
        for tag, children in self.group_children(element).items():
            # 先判断是否强制列表
            if tag in force_list_for:
                # 总是返回列表，即使 children 为空也返回空列表
                result[tag] = [self.factory.parse(child) for child in children]
            else:
                # 原有规则：单个取单值，多个取列表
                if len(children) == 1:
                    result[tag] = self.factory.parse(children[0])
                else:
                    result[tag] = [self.factory.parse(child) for child in children]
        return result

    def parse_child_list(self, element: Element, child_tag: str | None = None) -> list[Any]:
        """把子元素解析成列表，可按标签过滤。"""
        if self.factory is None:
            raise RuntimeError("ElementParser.factory 尚未绑定")
        values: list[Any] = []
        for child in element:
            if not isinstance(child.tag, str):
                continue
            if child_tag is not None and child.tag != child_tag:
                continue
            parsed = self.factory.parse(child)
            if parsed is not None:
                values.append(parsed)
        return values

    def parse_named_map(
        self,
        element: Element,
        result_key: str,
        *,
        name_field: str = "name",
        child_tag: str | None = None,
    ) -> dict[str, Any]:
        """把带 name 的子元素收成 result[result_key][name] = 解析结果。"""
        if self.factory is None:
            raise RuntimeError("ElementParser.factory 尚未绑定")
        result = self.parse_attribs(element)
        mapping: dict[str, Any] = {}
        for child in element:
            if not isinstance(child.tag, str):
                continue
            if child_tag is not None and child.tag != child_tag:
                continue
            parsed = self.factory.parse(child)
            if isinstance(parsed, dict):
                name = parsed.get(name_field)
                if name is not None:
                    mapping[name] = parsed
        result[result_key] = mapping
        return result

    def tag_counter(self, element: etree._Element) -> dict[str, list[Element]]:
        return self.group_children(element)

    def can_parse(self, element: Element) -> bool:
        """是否由当前解析器处理。默认 True，标签/后缀通道可省略。"""
        return True

    @abstractmethod
    def parse(self, element: Element) -> Any:
        """把元素转成 Python 值。"""
