from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bqyx_parser.parser import load_xml, parse_element_by_factory
from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.xml import Element
from bqyx_parser.tools.logger import get_logger

logger = get_logger()


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
    """<father> 提取所有 <equip>，注入 fatherName 并忽略 <skill>。"""

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


def create_jewelry_factory():
    factory = create_factory()
    factory.register_parser(DataRootParser(factory), priority=100)
    factory.register_parser(FatherParser(factory), priority=90)
    return factory


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\json\equip\jewelry")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "jewelry.xml"
    output_path = out_put_dir / "jewelryData.json"


if __name__ == "__main__":
    run()
