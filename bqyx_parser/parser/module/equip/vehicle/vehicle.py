from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bqyx_parser.parser import load_xml, parse_element_by_factory
from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.element.defaults import TextElementParser
from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.xml import Element
from bqyx_parser.tools.logger import get_logger

logger = get_logger()


class RawAttribParser(ElementParser):
    """保持 main / sub 属性为原始字符串字典。"""

    def can_parse(self, element: Element) -> bool:
        return element.tag in ("main", "sub")

    def parse(self, element: Element) -> dict[str, str]:
        return dict(element.attrib)


def create_vehicle_factory():
    factory = create_factory()
    factory.register_parser(RawAttribParser(), priority=100)
    factory.register_tag("specialInfoArr", TextElementParser())
    return factory


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\json\equip\vehicle")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    output_path = out_put_dir / "vehicleData.json"


if __name__ == "__main__":
    run()
