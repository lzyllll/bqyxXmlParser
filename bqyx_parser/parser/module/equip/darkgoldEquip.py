from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bqyx_parser.parser import load_xml, parse_element_by_factory
from bqyx_parser.parser.attrib.base import AttribParser
from bqyx_parser.parser.attrib.defaults import NameAttribParser
from bqyx_parser.parser.element.defaults import addObjJsonParser
from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.xml import Element
from bqyx_parser.tools.logger import get_logger

logger = get_logger()


class ColonSuitProAttribParser(AttribParser):
    """解析以逗号分隔的 suitPro 属性，每项格式为 name:value。"""

    def parse(self, key: str, value: str, element: Element | None = None) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        for part in value.split(","):
            part = part.strip()
            if not part:
                continue
            if ":" in part:
                name, val = part.split(":", 1)
                items.append({"name": name, "value": float(val) if "." in val else int(val)})
            else:
                items.append({"name": part})
        return items


def create_darkgoldEquip_factory():
    factory = create_factory(force_list_for=["gather", "father", "image"])
    factory.register_tag("otherObjJson", addObjJsonParser())
    factory.attrib_registry.register_name("suitPro", ColonSuitProAttribParser())
    factory.attrib_registry.register_name("evoB", NameAttribParser())
    return factory


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\resource\equip")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "darkgoldEquip.xml"
    output_path = out_put_dir / "darkgoldEquip.json"


if __name__ == "__main__":
    run()
