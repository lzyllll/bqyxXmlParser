from __future__ import annotations
import json
from pathlib import Path
from collections import Counter
from typing import Any

from bqyx_parser.parser.element.base import ElementParser

from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.xml import Element, has_children
from bqyx_parser.tools.compare import compare_data
from bqyx_parser.tools.gift_str import parse_gift_string
from bqyx_parser.tools.logger import get_logger

from bqyx_parser.parser import load_xml, parse_element_by_factory

logger = get_logger()


def create_blackMarketThings_factory():
    factory = create_factory()
    return factory
if __name__ == "__main__":
    xml_dir = Path(r"compiled\v3671\xml")
    out_put_dir = Path(r"output\v3671\json\blackMarket")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "blackMarketThings.xml"
    output_path = out_put_dir / "blackMarketThings.json"
    resource_path = Path(r"D:\bqyx\rs\resource\blackMarket\blackMarketThings.json")

    logger.info("解析 %s", xml_path)
    result = parse_element_by_factory(load_xml(xml_path), create_blackMarketThings_factory())
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s", output_path)

    if resource_path.is_file():
        with open(resource_path, "r", encoding="utf-8") as f:
            old = json.load(f)
        logger.info("对比 %s", resource_path)
        compare_data(old, result)
    else:
        logger.warning("资源文件不存在: %s", resource_path)
