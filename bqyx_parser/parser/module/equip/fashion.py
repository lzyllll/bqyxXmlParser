from __future__ import annotations

import json
from pathlib import Path

from bqyx_parser.parser import load_xml, parse_element_by_factory
from bqyx_parser.parser.attrib.defaults import EndWithArrAttribParser, NameAttribParser
from bqyx_parser.parser.factory import create_factory
from bqyx_parser.tools.logger import get_logger

logger = get_logger()


def create_fashion_factory():
    factory = create_factory()
    factory.attrib_registry.register_name("onlyRole", NameAttribParser())
    factory.attrib_registry.register_name("composeMustNum", NameAttribParser())
    factory.attrib_registry.register_name("life", NameAttribParser())
    factory.attrib_registry.register_name("hd", NameAttribParser())
    factory.attrib_registry.register_name("fashionPartShow", EndWithArrAttribParser())
    return factory


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\json\equip")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "fashion.xml"
    output_path = out_put_dir / "fashionData.json"


if __name__ == "__main__":
    run()
