from __future__ import annotations
import json
from pathlib import Path
from collections import Counter
from typing import Any

from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.xml import Element, get_father_name, has_children
from bqyx_parser.tools.gift_str import parse_gift_string
from bqyx_parser.tools.logger import get_logger

from bqyx_parser.parser import load_xml, parse_element_by_factory

logger = get_logger()


class DataRootParser(ElementParser):
    """
    <data> 获取所有 <father>，把每个 father 的列表扁平合并。
    """

    def can_parse(self, element: Element) -> bool:
        if element.tag != "data":
            return False

        return True

    def parse(self, element: Element) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        for child in element:
            parsed = self.parser_element(child)
            merged.extend(parsed)
        return [m for m in merged]


class FatherParser(ElementParser):
    """<father> 获取所有body 并且，忽视所有非body元素"""
    def can_parse(self, element: Element) -> bool:
        if element.tag != "father":
            return False
        return True

    def parse(self, element: Element) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        for child in element:
            if child.tag == "body":
                parsed = self.parser_element(child)
                parsed['father'] = get_father_name(element)
                parsed['fatherCnName'] = element.attrib.get('cnName')

                merged.append(parsed)

        return merged

def create_hero_factory():
    factory = create_factory()
    factory.register_parser(DataRootParser(factory))
    factory.register_parser(FatherParser(factory))
    return factory
def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\resource\body")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "hero.xml"
    output_path = out_put_dir / "hero.json"

    logger.info("解析 %s", xml_path)
    result = parse_element_by_factory(load_xml(xml_path), create_hero_factory())
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s", output_path)


if __name__ == "__main__":
    run()
