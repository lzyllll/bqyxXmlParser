from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bqyx_parser.parser import load_xml, parse_element_by_factory
from bqyx_parser.parser.attrib.defaults import DefaultAttribParser
from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.xml import Element
from bqyx_parser.tools.logger import get_logger

logger = get_logger()


def create_device_factory():
    factory = create_factory()
    return factory


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\json\equip\device")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    output_path = out_put_dir / "deviceData.json"


if __name__ == "__main__":
    run()
