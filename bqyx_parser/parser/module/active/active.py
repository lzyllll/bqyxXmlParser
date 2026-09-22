from __future__ import annotations
import json
from pathlib import Path
from collections import Counter
from typing import Any

from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.xml import Element, has_children
from bqyx_parser.tools.gift_str import parse_gift_string
from bqyx_parser.tools.logger import get_logger

from bqyx_parser.parser import load_xml, parse_element_by_factory

logger = get_logger()


class TaskGiftParser(ElementParser):
    """
    <task>
		<one name="dailySign" 			cnName="签到礼包" 	num="1" 		active="5" />
		
		<one name="endlessLevel" 	cnName="进行无尽模式" 	num="1" 		active="20"/>
    <task>
    """

    def can_parse(self, element: Element) -> bool:
        return element.tag == "task" or element.tag == "gift"

    def parse(self, element: Element) -> dict[str, Any]:
        return [self.parser_element(child) for child in element]
class OneParser(ElementParser):
    """<one> -> dict"""
    def can_parse(self, element: Element) -> bool:
        return element.tag == "one"

    def parse(self, element: Element) -> dict[str, Any]:
        return self.parse_attribs(element)

def create_active_factory():
    factory = create_factory()
    factory.add_rename_maps(
        element={
            "task": "tasks",
            "gift": "gifts"
        }
    )
    factory.register_parser(TaskGiftParser())
    factory.register_parser(OneParser())
    return factory
def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\resource\active")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "active.xml"
    output_path = out_put_dir / "activeClass.json"

    logger.info("解析 %s", xml_path)
    result = parse_element_by_factory(load_xml(xml_path), create_active_factory())

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s", output_path)


if __name__ == "__main__":
    run()
