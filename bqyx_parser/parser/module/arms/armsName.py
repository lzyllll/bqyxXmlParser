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

from lxml import etree
import json

def parse_element_to_dict(element) -> dict:
    """
    解析 XML，生成与期望 JSON 完全一致的字典。
    """

    result = {}

    for type_elem in element.xpath('//type'):
        type_name = type_elem.get('name')
        if not type_name:
            continue

        text = type_elem.text
        if text is None:
            continue

        # 按分号分割记录
        lines = text.split(';')
        data = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if ':' not in line:
                continue

            key, val_str = line.split(':', 1)
            key = key.strip()

            # 关键修正：按逗号分割，保留所有元素（不做 strip，不过滤空）
            values = val_str.split(',')

            # 对 texture 类型的键添加前缀
            if type_name == 'texture':
                key = 'texture/' + key

            data[key] = values

        result[type_name] = data

    return result



def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\json\arms")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "armsName.xml"
    output_path = out_put_dir / "armsName.json"

    logger.info("解析 %s", xml_path)
    result = parse_element_to_dict(load_xml(xml_path))
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s", output_path)


if __name__ == "__main__":
    run()
