from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bqyx_parser.parser import load_xml, parse_element_by_factory
from bqyx_parser.parser.attrib.base import AttribParser
from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.factory import create_factory
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


class DataRootParser(ElementParser):
    """<data> 解析所有 <father> 并展平为列表。"""

    def can_parse(self, element: Element) -> bool:
        return element.tag == "data"

    def parse(self, element: Element) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for child in element:
            if isinstance(child.tag, str) and child.tag == "father":
                result.extend(self.parser_element(child))
        return result


class FatherParser(ElementParser):
    """<father> 提取所有 <equip>，注入 fatherName 并忽略其他非 equip 子元素。"""

    def can_parse(self, element: Element) -> bool:
        return element.tag == "father"

    def parse(self, element: Element) -> list[dict[str, Any]]:
        father_name = element.attrib.get("name")
        equips: list[dict[str, Any]] = []
        for child in element:
            if isinstance(child.tag, str) and child.tag == "equip":
                item = {"fatherName": father_name}
                item.update(self.parser_element(child))
                equips.append(item)
        return equips


def create_weapon_factory():
    factory = create_factory()
    factory.attrib_registry.register_name("description", DescriptionAttribParser())
    factory.register_parser(DataRootParser(factory), priority=100)
    factory.register_parser(FatherParser(factory), priority=90)
    return factory


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\json\equip\weapon")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "weapon.xml"
    output_path = out_put_dir / "weaponData.json"


if __name__ == "__main__":
    run()
