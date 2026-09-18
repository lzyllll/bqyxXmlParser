"""元素工厂和属性工厂。"""
from __future__ import annotations

from typing import Any, Iterable

from bqyx_parser.parser.attrib.base import AttribParser
from bqyx_parser.parser.attrib.defaults import (
    DefaultAttribParser,
    EndWithArrAttribParser,
    EndWithBAttribParser,
    NameAttribParser,
    ParserArrAttribParser,
    addObjJsonAttribParser,
    lightColorParser
)
from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.element.defaults import (
    AttributeElementParser,
    EmptyElementParser,
    EndWithArrParser,
    EndWithBParser,
    EndWithList,
    GiftParser,
    HurtArrParser,
    NestedElementParser,
    ObjParser,
    ParserArrParser,
    TagAttribElementParser,
    TextElementParser,
    addObjJsonParser,
    hurtRectArrParser,
    EndWithRectParser
)
from bqyx_parser.parser.xml import Element, is_element


class AttribParserFactory:
    """
    属性解析工厂，按三条通道选解析器：

    1. register() 注册的自定义解析器
    2. 精确属性名 / 后缀规则
    3. 兜底：safe_eval
    """

    def __init__(self, default_parser: AttribParser | None = None):
        self._custom: list[tuple[int, AttribParser]] = []
        self._name_parsers: dict[str, AttribParser] = {}
        self._suffix_parsers: list[tuple[str, AttribParser]] = []
        self._fallbacks: list[tuple[int, AttribParser]] = []
        self._default = default_parser or DefaultAttribParser()

    def register(self, parser: AttribParser, priority: int = 0) -> AttribParserFactory:
        """注册自定义解析器，会先于属性名和后缀规则匹配。"""
        self._custom.append((priority, parser))
        self._custom.sort(key=lambda item: item[0], reverse=True)
        return self

    def register_parser(self, parser: AttribParser, priority: int = 0) -> AttribParserFactory:
        return self.register(parser, priority=priority)

    def register_name(self, name: str, parser: AttribParser) -> AttribParserFactory:
        """按精确属性名注册，例如 name。"""
        self._name_parsers[name] = parser
        return self

    def register_suffix(self, suffix: str, parser: AttribParser) -> AttribParserFactory:
        """按属性名后缀注册，例如 B、Arr。"""
        self._suffix_parsers.append((suffix, parser))
        return self

    def register_fallback(self, parser: AttribParser, priority: int = 0) -> AttribParserFactory:
        """注册兜底解析器。"""
        self._fallbacks.append((priority, parser))
        self._fallbacks.sort(key=lambda item: item[0], reverse=True)
        return self

    def parse(self, element: Element, result: dict[str, Any] | None = None) -> dict[str, Any]:
        """把属性解析结果写入 result。"""
        result = {} if result is None else result
        for key, value in element.attrib.items():
            result[key] = self.parse_attrib(key, value, element)
        return result

    def parse_attrib(self, key: str, value: str, element: Element | None = None) -> Any:
        return self.get_parser(key, value, element).parse(key, value, element)

    def get_parser(
        self,
        key: str,
        value: str = "",
        element: Element | None = None,
    ) -> AttribParser:
        for _, parser in self._custom:
            if parser.can_parse(key, value, element):
                return parser

        parser = self._name_parsers.get(key)
        if parser is not None and parser.can_parse(key, value, element):
            return parser

        for suffix, parser in self._suffix_parsers:
            if key.endswith(suffix) and parser.can_parse(key, value, element):
                return parser

        for _, parser in self._fallbacks:
            if parser.can_parse(key, value, element):
                return parser
        return self._default

    def unregister(self, parser_class: type) -> None:
        self._custom = [item for item in self._custom if not isinstance(item[1], parser_class)]
        self._fallbacks = [item for item in self._fallbacks if not isinstance(item[1], parser_class)]
        self._name_parsers = {
            name: parser for name, parser in self._name_parsers.items()
            if not isinstance(parser, parser_class)
        }
        self._suffix_parsers = [
            item for item in self._suffix_parsers if not isinstance(item[1], parser_class)
        ]

    def unregister_parser(self, parser_class: type) -> None:
        self.unregister(parser_class)

    def get_registered_parsers(self) -> list[tuple]:
        registered: list[tuple] = []
        registered.extend((priority, type(parser).__name__) for priority, parser in self._custom)
        registered.extend(("name", name, type(parser).__name__) for name, parser in self._name_parsers.items())
        registered.extend(("suffix", suffix, type(parser).__name__) for suffix, parser in self._suffix_parsers)
        registered.extend((priority, type(parser).__name__) for priority, parser in self._fallbacks)
        return registered


AttribParserRegistry = AttribParserFactory


class ElementParserFactory:
    """
    元素解析工厂，按三条通道选解析器：

    1. register() 注册的自定义解析器
    2. 精确标签 / 后缀规则
    3. 按形态兜底：纯文本、纯属性、嵌套、空元素
    """

    def __init__(
        self,
        attrib_registry: AttribParserFactory | None = None,
        rename_maps: dict[str, dict[str, str]] | None = None,
        force_list_for: Iterable[str] | str | None = None,
    ):
        self.attrib_registry = attrib_registry or AttribParserFactory()
        maps = rename_maps or {}
        self.rename_maps: dict[str, dict[str, str]] = {
            "attrib": dict(maps.get("attrib") or {}),
            "element": dict(maps.get("element") or {}),
        }
        if isinstance(force_list_for, str):
            self.force_list_for: set[str] = {force_list_for}
        else:
            self.force_list_for: set[str] = set(force_list_for or ())
        self._custom: list[tuple[int, ElementParser]] = []
        self._tag_parsers: dict[str, ElementParser] = {}
        self._suffix_parsers: list[tuple[str, ElementParser]] = []
        self._fallbacks: list[tuple[int, ElementParser]] = []
        self._empty = EmptyElementParser()
        self._bind(self._empty)

    def add_force_list_for(self, *tags: str | Iterable[str]) -> ElementParserFactory:
        """追加全局强制转换为列表的标签。可传集合、列表或单个/多个标签名。"""
        for item in tags:
            if isinstance(item, str):
                self.force_list_for.add(item)
            else:
                self.force_list_for.update(item)
        return self

    def add_rename_maps(
        self,
        attrib: dict[str, str] | None = None,
        element: dict[str, str] | None = None,
    ) -> ElementParserFactory:
        """追加 attrib / element 改名映射。"""
        if attrib:
            self.rename_maps["attrib"].update(attrib)
        if element:
            self.rename_maps["element"].update(element)
        return self

    def set_attrib_registry(self, attrib_registry: AttribParserFactory) -> None:
        self.attrib_registry = attrib_registry
        for parser in self._all_parsers():
            parser.set_attrib_registry(attrib_registry)

    def register(self, parser: ElementParser, priority: int = 0) -> ElementParserFactory:
        """注册自定义解析器，会先于标签和形态规则匹配。"""
        self._bind(parser)
        self._custom.append((priority, parser))
        self._custom.sort(key=lambda item: item[0], reverse=True)
        return self

    def register_parser(self, parser: ElementParser, priority: int = 10) -> ElementParserFactory:
        return self.register(parser, priority=priority)

    def register_tag(self, tag: str, parser: ElementParser) -> ElementParserFactory:
        """按精确标签注册，例如 obj。"""
        self._bind(parser)
        self._tag_parsers[tag] = parser
        return self

    def register_suffix(self, suffix: str, parser: ElementParser) -> ElementParserFactory:
        """按标签后缀注册，例如 B、Arr、Url。"""
        self._bind(parser)
        self._suffix_parsers.append((suffix, parser))
        return self

    def register_fallback(self, parser: ElementParser, priority: int = 0) -> ElementParserFactory:
        """注册形态兜底解析器。"""
        self._bind(parser)
        self._fallbacks.append((priority, parser))
        self._fallbacks.sort(key=lambda item: item[0], reverse=True)
        return self

    def parse(self, element: Element) -> Any:
        return self.get_parser(element).parse(element)

    def parse_element(self, element: Element) -> Any:
        return self.parse(element)

    def get_parser(self, element: Element) -> ElementParser:
        if not is_element(element):
            return self._empty

        for _, parser in self._custom:
            if parser.can_parse(element):
                return parser

        tag = element.tag
        parser = self._tag_parsers.get(tag)
        if parser is not None and parser.can_parse(element):
            return parser

        for suffix, parser in self._suffix_parsers:
            if tag.endswith(suffix) and parser.can_parse(element):
                return parser

        for _, parser in self._fallbacks:
            if parser.can_parse(element):
                return parser
        return self._empty

    def unregister(self, parser_class: type) -> None:
        self._custom = [item for item in self._custom if not isinstance(item[1], parser_class)]
        self._fallbacks = [item for item in self._fallbacks if not isinstance(item[1], parser_class)]
        self._tag_parsers = {
            tag: parser for tag, parser in self._tag_parsers.items()
            if not isinstance(parser, parser_class)
        }
        self._suffix_parsers = [
            item for item in self._suffix_parsers if not isinstance(item[1], parser_class)
        ]

    def unregister_parser(self, parser_class: type) -> None:
        self.unregister(parser_class)

    def get_registered_parsers(self) -> list[tuple]:
        registered: list[tuple] = []
        registered.extend((priority, type(parser).__name__) for priority, parser in self._custom)
        registered.extend(("tag", tag, type(parser).__name__) for tag, parser in self._tag_parsers.items())
        registered.extend(("suffix", suffix, type(parser).__name__) for suffix, parser in self._suffix_parsers)
        registered.extend((priority, type(parser).__name__) for priority, parser in self._fallbacks)
        return registered

    def _bind(self, parser: ElementParser) -> None:
        parser.set_factory(self)
        parser.set_attrib_registry(self.attrib_registry)

    def _all_parsers(self) -> Iterable[ElementParser]:
        yield self._empty
        for _, parser in self._custom:
            yield parser
        yield from self._tag_parsers.values()
        for _, parser in self._suffix_parsers:
            yield parser
        for _, parser in self._fallbacks:
            yield parser


def create_attrib_registry() -> AttribParserFactory:
    """创建带默认规则的属性工厂，每次都是独立实例。"""
    factory = AttribParserFactory()
    factory.register_name("addObjJson", addObjJsonAttribParser())
    factory.register_name('lightColor',lightColorParser())
    factory.register_name("name", NameAttribParser())
    factory.register_suffix("B", EndWithBAttribParser())
    factory.register_suffix("Arr", EndWithArrAttribParser())
    factory.register_suffix("ArrCn", EndWithArrAttribParser())
    factory.register_fallback(ParserArrAttribParser(), 1)
    factory.register_fallback(DefaultAttribParser(), 0)
    return factory


create_attrib_factory = create_attrib_registry


def create_factory(
    attrib_registry: AttribParserFactory | None = None,
    rename_maps: dict[str, dict[str, str]] | None = None,
    force_list_for: Iterable[str] | str | None = None,
) -> ElementParserFactory:
    """创建带默认规则的新工厂，每次都是独立实例。"""
    factory = ElementParserFactory(
        attrib_registry or create_attrib_registry(),
        rename_maps=rename_maps,
        force_list_for=force_list_for,
    )
    factory.register_tag("hurtArr", HurtArrParser())
    factory.register_tag("obj", ObjParser())
    factory.register_tag("hurtRectArr", hurtRectArrParser())
    factory.register_tag("addObjJson", addObjJsonParser())
    factory.register_suffix("Rect", EndWithRectParser())
    factory.register_suffix("B", EndWithBParser())
    factory.register_suffix("Arr", EndWithArrParser())
    factory.register_suffix("ArrCn", EndWithArrParser())
    factory.register_suffix("List", EndWithList())
    factory.register_fallback(GiftParser(), 6)
    factory.register_fallback(ObjParser(), 5)
    factory.register_fallback(ParserArrParser(), 4)
    factory.register_fallback(TextElementParser(), 3)
    factory.register_fallback(AttributeElementParser(), 2)
    factory.register_fallback(TagAttribElementParser(), 1)
    factory.register_fallback(NestedElementParser(), 0)
    return factory
