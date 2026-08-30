"""XML 读写工具：加载文件、解析元素。"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from lxml import etree

from bqyx_parser.parser.convert import safe_eval

Element = etree._Element
_DEFAULT_FACTORY = None


def element_text(element: Element) -> str | None:
    """返回去掉首尾空白的文本，空则 None。"""
    if element.text is None:
        return None
    text = element.text.strip()
    return text or None


def has_text(element: Element) -> bool:
    return element_text(element) is not None


def has_children(element: Element) -> bool:
    return len(element) > 0


def has_attrib(element: Element) -> bool:
    return bool(element.attrib)


def eval_text(element: Element) -> Any:
    text = element_text(element)
    return None if text is None else safe_eval(text)


def is_element(node: object) -> bool:
    """排除注释、处理指令等非元素节点。"""
    return isinstance(node, etree._Element) and isinstance(getattr(node, "tag", None), str)


def xml_parser(
    *,
    remove_comments: bool = True,
    remove_blank_text: bool = True,
    strip_cdata: bool = True,
    recover: bool = False,
) -> etree.XMLParser:
    return etree.XMLParser(
        remove_comments=remove_comments,
        remove_blank_text=remove_blank_text,
        strip_cdata=strip_cdata,
        recover=recover,
        huge_tree=True,
    )


def _normalize_declaration(data: bytes) -> bytes:
    # 反编译产物里偶尔会出现 <?xmlversion
    stripped = data.lstrip()
    if stripped.startswith(b"<?xmlversion"):
        return data.replace(b"<?xmlversion", b"<?xml version", 1)
    return data


def load_xml(
    source: str | Path | bytes,
    *,
    remove_comments: bool = True,
    remove_blank_text: bool = True,
    strip_cdata: bool = True,
    recover: bool = False,
) -> Element:
    """读取 XML，返回根元素。默认去掉注释和空白文本。"""
    parser = xml_parser(
        remove_comments=remove_comments,
        remove_blank_text=remove_blank_text,
        strip_cdata=strip_cdata,
        recover=recover,
    )
    data = source if isinstance(source, bytes) else Path(source).read_bytes()
    return etree.fromstring(_normalize_declaration(data), parser=parser)


def load_xml_files(paths: Iterable[str | Path], **kwargs: Any) -> list[Element]:
    """批量加载 XML 文件的根元素。"""
    roots: list[Element] = []
    for path in paths:
        file_path = Path(path)
        if file_path.is_file() and file_path.suffix.lower() == ".xml":
            roots.append(load_xml(file_path, **kwargs))
    return roots


def parse_element(element: Element, factory=None) -> Any:
    """用指定工厂解析一个元素；未传工厂时复用默认工厂。"""
    global _DEFAULT_FACTORY
    if factory is None:
        if _DEFAULT_FACTORY is None:
            from bqyx_parser.parser.factory import create_factory

            _DEFAULT_FACTORY = create_factory()
        factory = _DEFAULT_FACTORY
    return factory.parse(element)


def parse_xml(source: str | Path | bytes, factory=None, **kwargs: Any) -> Any:
    """加载 XML 并解析根元素。"""
    return parse_element(load_xml(source, **kwargs), factory=factory)
