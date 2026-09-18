"""元素解析器基类。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import TYPE_CHECKING, Any, Iterable, Optional, Set

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

    def _resolve_rename_map(
        self,
        kind: str,
        extra: Optional[dict[str, str]] = None,
    ) -> dict[str, str]:
        merged: dict[str, str] = {}
        if self.factory is not None:
            merged.update(self.factory.rename_maps.get(kind) or {})
        if extra:
            merged.update(extra)
        return merged

    def _resolve_force_list_for(
        self,
        extra: Optional[Iterable[str] | str] = None,
    ) -> set[str]:
        merged: set[str] = set()
        if self.factory is not None:
            factory_force = getattr(self.factory, "force_list_for", None)
            if factory_force:
                merged.update(factory_force)
        if extra:
            if isinstance(extra, str):
                merged.add(extra)
            else:
                merged.update(extra)
        return merged

    def parse_attribs(
        self,
        element: Element,
        result: dict[str, Any] | None = None,
        rename_keys: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        解析当前元素属性。可通过 rename_keys 把原 key 改成新 key。
        工厂 rename_maps["attrib"] 会自动生效，调用方传入的 rename_keys 优先。
        """
        result = {} if result is None else result
        rename_keys = self._resolve_rename_map("attrib", rename_keys)
        if self.attrib_registry is not None:
            for key, value in element.attrib.items():
                result[rename_keys.get(key, key)] = self.attrib_registry.parse_attrib(
                    key, value, element
                )
        return result

    def parser_element(self, element: Element) -> Any:
        """解析当前元素，返回 Python 值。"""
        if self.factory is None:
            raise RuntimeError("ElementParser.factory 尚未绑定")
        return self.factory.parse(element)

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
        force_list_for: Optional[Set[str] | Iterable[str] | str] = None,
        rename_tags: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        解析子元素，同名多个变为列表，单个默认取单值。
        
        Args:
            element: 要解析的父元素
            force_list_for: 强制转换为列表的标签集合（即使只有一个孩子也返回列表）。
                工厂 force_list_for 会自动生效，调用方传入的 force_list_for 优先合并。
            rename_tags: 标签改名映射，例如 {'addObjJson': 'addObj'}。
                工厂 rename_maps["element"] 会自动生效，调用方传入的 rename_tags 优先。
        
        Returns:
            字典，键为标签名（可被改名），值为解析结果（单值或列表）
        """
        if self.factory is None:
            raise RuntimeError("ElementParser.factory 尚未绑定")

        resolved_force_list = self._resolve_force_list_for(force_list_for)
        rename_tags = self._resolve_rename_map("element", rename_tags)

        result: dict[str, Any] = {}
        for tag, children in self.group_children(element).items():
            key = rename_tags.get(tag, tag)
            parsed = [self.factory.parse(child) for child in children]
            force_list = tag in resolved_force_list or key in resolved_force_list

            if key in result:
                existing = result[key]
                if not isinstance(existing, list):
                    existing = [existing]
                existing.extend(parsed)
                result[key] = existing
            elif force_list or len(parsed) != 1:
                result[key] = parsed
            else:
                result[key] = parsed[0]
        return result



    def can_parse(self, element: Element) -> bool:
        """是否由当前解析器处理。默认 True，标签/后缀通道可省略。"""
        return True

    @abstractmethod
    def parse(self, element: Element) -> Any:
        """把元素转成 Python 值。"""
