from __future__ import annotations
import json
from pathlib import Path
from collections import Counter
from typing import Any

from bqyx_parser.parser.element.base import ElementParser

from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.module.union.military import create_military_factory
from bqyx_parser.parser.xml import Element, has_children
from bqyx_parser.tools.gift_str import parse_gift_string

from bqyx_parser.parser import load_xml, parse_element


def create_unionBuilding_factory():
    """union 类 XML（father 下是同名事物列表）专用工厂。"""
    factory = create_factory()
    return factory
if __name__ == "__main__":
    xml_dir = Path(r"compiled\v3671\xml")
    out_put_dir = Path(r"output\v3671\json\union")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "unionBuilding.xml"
    output_path = out_put_dir / "unionBuilding.json"
    union_building_result = parse_element(load_xml(xml_path), create_unionBuilding_factory())

    union_building_result['building'] = union_building_result['building']['bu']
    union_building_result['cooking'] = union_building_result['cooking']['co']
    union_building_result['watchmen'] = union_building_result['watchmen']['wa']
    union_building_result['geology']['arr'] = union_building_result['geology'].pop('things')
    union_building_result['sendTask'] = union_building_result['sendTask']['task']
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(union_building_result, ensure_ascii=False, indent=2))
