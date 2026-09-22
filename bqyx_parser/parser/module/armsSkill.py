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


'''
为完善的模块，暂时未想好怎么生成

'''
logger = get_logger()




def create_armsSkill_factory():
    factory = create_factory()
    return factory
def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\resource")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "armsSkill.xml"
    output_path = out_put_dir / "armsSkillClass.json"

    logger.info("解析 %s", xml_path)
    result = parse_element_by_factory(load_xml(xml_path), create_armsSkill_factory())
    result = {v.get('name'): v for v in result.get('father')}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s", output_path)


if __name__ == "__main__":
    run()
