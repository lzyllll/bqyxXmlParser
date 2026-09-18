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

class RootParser(ElementParser):
    """<data> 下若全是 <father>，把每个 father 的列表扁平合并。"""

    def can_parse(self, element: Element) -> bool:
        if element.tag != "data":
            return False
        child_tags = {child.tag for child in element if isinstance(child.tag, str)}
        return bool(child_tags) and child_tags.issubset({"father"})

    def parse(self, element: Element) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        for child in element:
            if isinstance(child.tag, str) and child.tag == "father":
                parsed = self.parser_element(child)
                merged.extend(parsed)

        return [m for m in merged]
class fatherChildrenParser(ElementParser):
    """
    解析 
    <father name="..." cnName="...">
       <head/><head/>...
    </father>

    结果：把所有同层子元素（同名多个展平成列表，异名保留为 dict）
    展开后，每条记录注入 father / fatherCnName 两个字段。
    """

    def can_parse(self, element: Element) -> bool:
        return element.tag == "father" and has_children(element)

    def parse(self, element: Element) -> list[dict[str, Any]]:
        # 1) 让默认通道把每个子元素解析成 Python 对象
        children: list[Any] = []
        for child in element:
            if child.tag == "head":
                parsed = self.parser_element(child)
                if element.get("name") != None:
                    parsed.update({
                        'fatherName': element.get('name'),
                    })
                children.append(parsed)
        return children

class HeadParser(ElementParser):
    """
    解析 
    <head name="..." cnName="...">
       <pro/><pro/>...
    </head>

    结果：把所有同层子元素（同名多个展平成列表，异名保留为 dict）
    展开后，每条记录注入 head / headCnName 两个字段。
    """

    def can_parse(self, element: Element) -> bool:
        return element.tag == "head" and has_children(element)

    def parse(self, element: Element) -> list[dict[str, Any]]:
        result = self.parse_attribs(element)
                
        result.update(
            self.parse_children(
                element,
                force_list_for={'gift'},
                rename_tags={'addObjJson': 'addObj'}
            )
        )
        return result



def create_head_factory():
    factory = create_factory()
    factory.register_tag("data", RootParser())
    factory.register_tag("father", fatherChildrenParser())
    factory.register_tag("head", HeadParser())
    return factory
def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\json\head")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "head.xml"
    output_path = out_put_dir / "headData.json"

    logger.info("解析 %s", xml_path)
    result = parse_element_by_factory(load_xml(xml_path), create_head_factory())
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s", output_path)


if __name__ == "__main__":
    run()
