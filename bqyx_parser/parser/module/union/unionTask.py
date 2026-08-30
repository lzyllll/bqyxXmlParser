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

def create_unionTask_factory():
    """union 类 XML（father 下是同名事物列表）专用工厂。"""
    factory = create_factory()
    return factory
if __name__ == "__main__":
    xml_dir = Path(r"compiled\v3671\xml")
    out_put_dir = Path(r"output\v3671\json\union")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "unionTask.xml"
    output_path = out_put_dir / "unionTask.json"
    unionTask_result = parse_element(load_xml(xml_path), create_unionTask_factory())
    unionTask_result = unionTask_result.get('task')
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(unionTask_result, ensure_ascii=False, indent=2))
