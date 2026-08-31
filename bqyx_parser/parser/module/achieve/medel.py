from pathlib import Path
from typing import Any

import json

from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.xml import Element, load_xml, parse_element
from bqyx_parser.tools.compare import compare_data
from bqyx_parser.tools.logger import get_logger

logger = get_logger()

class DataRootParser(ElementParser):
    """<data> 全是 <pro>，"""

    def can_parse(self, element: Element) -> bool:
        if element.tag != "data":
            return False
        return all(isinstance(child.tag, str) and child.tag == "pro" for child in element)

    def parse(self, element: Element) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        for pro in element:
            if isinstance(pro.tag, str) and pro.tag == "pro":
                merged.append(self.factory.parse(pro))
        #转字典
        merged_dict = {achieve['name']: achieve for achieve in merged}
        return merged_dict

def create_medel_property_factory():
    """medelProperty 类 XML 专用工厂。"""
    factory = create_factory()
    factory.register_parser(DataRootParser(factory))
    return factory

if __name__ == "__main__":
    xml_dir = Path(r"compiled\v3671\xml")
    out_put_dir = Path(r"output\v3671\json\achieve")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    medel_property_path = xml_dir / "medelProperty.xml"
    output_medel_property_path = out_put_dir / "medelProperty.json"

    loaded_xml = load_xml(medel_property_path)

    medel_result = parse_element(
        load_xml(medel_property_path),
        create_medel_property_factory()
    )
    with open(output_medel_property_path, "w", encoding="utf-8") as f:
        json.dump(medel_result, f, ensure_ascii=False, indent=4)
    logger.info("已保存 %s", output_medel_property_path)
    resource_path = Path(r"D:\bqyx\rs\resource\achieve\medelPropertyClass.json")
    with open(resource_path, "r", encoding="utf-8") as f:
        old = json.load(f)
    logger.info("对比 %s", resource_path)
    compare_data(old, medel_result)
