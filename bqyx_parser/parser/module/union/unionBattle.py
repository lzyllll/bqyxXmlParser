from __future__ import annotations
import json
from pathlib import Path
from collections import Counter
from typing import Any

from bqyx_parser.parser.element.base import ElementParser

from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.xml import Element, has_children
from bqyx_parser.tools.gift_str import parse_gift_string

from bqyx_parser.parser import load_xml, parse_element


from bqyx_parser.tools.compare import compare_data
from bqyx_parser.tools.logger import get_logger

logger = get_logger()

def create_unionBattle_factory():
    """union 类 XML（father 下是同名事物列表）专用工厂。"""
    factory = create_factory()
    return factory
if __name__ == "__main__":
    xml_dir = Path(r"compiled\v3671\xml")
    out_put_dir = Path(r"output\v3671\json\union")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "unionBattle.xml"
    output_path = out_put_dir / "unionBattle.json"
    union_battle_result = parse_element(load_xml(xml_path), create_unionBattle_factory())
    union_battle_result = union_battle_result.get('mapAll', {}).get('map', [])

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(union_battle_result, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s", output_path)
    resource_path = Path(r"D:\bqyx\rs\resource\union\unionBattle.json")
    with open(resource_path, "r", encoding="utf-8") as f:
        old = json.load(f)
    logger.info("对比 %s", resource_path)
    compare_data(old, union_battle_result)
