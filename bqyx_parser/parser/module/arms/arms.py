from __future__ import annotations
import json
from pathlib import Path
from collections import Counter
from typing import Any

from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.element.config import CATEGORY_MAP
from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.xml import Element, has_children
from bqyx_parser.tools.gift_str import parse_gift_string
from bqyx_parser.tools.logger import get_logger

from bqyx_parser.parser import load_xml, parse_element_by_factory

logger = get_logger()

class DataRootParser(ElementParser):
    """
    <data> 获取所有 <father>，把每个 father 的列表扁平合并。
    并只解析 <father> 下的 <bullet>，忽视其他元素。
    
    
    """

    def can_parse(self, element: Element) -> bool:
        if element.tag != "data":
            return False

        return True

    def parse(self, element: Element) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        for child in element.findall(".//father"):
            parsed = self.parser_element(child)
            merged.extend(parsed)

        return [m for m in merged]

class FatherParser(ElementParser):
    """<father> 获取所有bullet 并且，忽视所有非bullet元素"""

    def can_parse(self, element: Element) -> bool:
        if element.tag != "father":
            return False
        return True

    def parse(self, element: Element) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        for child in element:
            if isinstance(child.tag, str) and child.tag == "bullet":

                # bullet可做成 arms 和 bullet，arms extends bullet 
                # 这样可以排除bulletDefine
                if child.find('bodyImgRange') is None and child.find('allImgRange') is None: 
                    continue
    
                parsed = self.parser_element(child)
                # 加个手动维护的类别
                if parsed["name"] in CATEGORY_MAP:
                    parsed["category"] = CATEGORY_MAP[parsed["name"]]
              
                parsed["armsType"] = element.attrib.get("type", "unknown")
                merged.append(parsed)

        return merged

def create_arms_factory():
    factory = create_factory()
    factory.register_parser(DataRootParser(factory),101)
    factory.register_parser(FatherParser(factory),100)
    return factory
def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\json\arms")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    weapon_paths = [file for file in xml_dir.iterdir() if file.is_file() and file.suffix == ".xml"]
    output_path = out_put_dir / "armsClass.json"

    logger.info("解析 arms (全部武器XML)...")
    result = []
    factory = create_arms_factory()
    for weapon_path in weapon_paths:
        result.extend(parse_element_by_factory(load_xml(weapon_path), factory))

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2, sort_keys=True)
    logger.info("已保存 %s", output_path)


if __name__ == "__main__":
    run()
# common = old_names & result_names
# print("Common:", common)

# 4. 全部差异 (对称差集)
# all_diff = old_names ^ result_names
# print("All differences:", all_diff)