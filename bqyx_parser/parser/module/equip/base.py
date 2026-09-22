"""装备模块通用基础：扫描目录下全部 XML，根据 fatherName 提取并解析 equip。"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from bqyx_parser.parser import load_xml, parse_element_by_factory
from bqyx_parser.parser.attrib.base import AttribParser
from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.xml import Element
from bqyx_parser.tools.logger import get_logger

logger = get_logger()


class DescriptionAttribParser(AttribParser):
    """转换富文本描述：清理空白字符，替换换行符与HTML标签占位符。"""

    def parse(self, key: str, value: str, element: Element | None = None) -> str:
        if not value:
            return value
        for c in ("\f", "\n", "\r", "\t"):
            value = value.replace(c, "")
        return value.replace("[n]", "\n").replace("{", "<").replace("}", ">")


class EquipParser(ElementParser):
    """<equip> 通用属性与子节点解析器。"""

    def can_parse(self, element: Element) -> bool:
        return element.tag == "equip"

    def parse(self, element: Element) -> dict[str, Any]:
        item = self.parse_attribs(element)
        children = self.parse_children(element)
        if children:
            item.update(children)
        return item


def scan_father_equips(
    xml_dir: str | Path,
    father_names: str | Iterable[str],
    factory,
    *,
    inject_father_name: bool = True,
    primary_file: str | None = None,
) -> list[dict[str, Any]]:
    """扫描目录下所有 XML 文件，通过指定 fatherName 过滤并解析其中的 equip 节点。"""
    target_names = {father_names} if isinstance(father_names, str) else set(father_names)
    xml_dir = Path(xml_dir)

    def sort_key(p: Path) -> tuple[int, str]:
        if primary_file and p.name == primary_file:
            return (0, p.name)
        return (1, p.name)

    xml_files = sorted(xml_dir.glob("*.xml"), key=sort_key)
    equips: list[dict[str, Any]] = []

    for xml_file in xml_files:
        try:
            root = load_xml(xml_file)
        except Exception as e:
            logger.warning("解析 XML 文件 %s 失败: %s", xml_file.name, e)
            continue

        for father in root.findall(".//father"):
            fname = father.attrib.get("name") or father.attrib.get("type")
            if fname in target_names:
                for eq in father.findall("./equip"):
                    parsed = parse_element_by_factory(eq, factory)
                    if inject_father_name:
                        item = {"fatherName": fname}
                        item.update(parsed)
                        equips.append(item)
                    else:
                        equips.append(parsed)

    return equips

