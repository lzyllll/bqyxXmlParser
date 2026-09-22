from __future__ import annotations
import json
from pathlib import Path
from collections import Counter
from typing import Any

from bqyx_parser.parser.element.base import ElementParser

from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.xml import Element, has_children
from bqyx_parser.tools.gift_str import parse_gift_string

from bqyx_parser.parser import load_xml, parse_element_by_factory
from bqyx_parser.tools.logger import get_logger

logger = get_logger()

class LevelParser(ElementParser):
    """
    <level>
        <gift>things;demStone;25,things;demStone;30</gift> 
        <gift>things;demStone;25,things;demStone;30</gift> 
    </level>
    gift 强制解析为列表
    """
    def can_parse(self, element: Element) -> bool:
        return element.tag == 'level'
    def parse(self, element: Element) -> dict[str, Any]:
        result = self.parse_attribs(element)
        
        result.update(
            self.parse_children(element,force_list_for={'gift'})
        )
        return result


def create_military_factory():
    """union 类 XML（father 下是同名事物列表）专用工厂。"""
    factory = create_factory()
    factory.register_parser(LevelParser(factory),100)
    return factory


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\resource\union")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "military.xml"
    output_path = out_put_dir / "military.json"
    military_result = parse_element_by_factory(load_xml(xml_path), create_military_factory())
    military_result = military_result.get('level', [])


    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(military_result, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s", output_path)


if __name__ == "__main__":
    run()
