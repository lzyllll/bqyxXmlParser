"""通用 father 解析器：把 <father> 下同名子元素展平成列表，并注入 father.name/cnName。"""
from __future__ import annotations

from collections import Counter
from typing import Any

from bqyx_parser.parser.element.base import ElementParser

from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.xml import Element, has_children
from bqyx_parser.tools.gift_str import parse_gift_string


class DataRootParser(ElementParser):
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
                parsed = self.factory.parse(child)
                merged.extend(parsed)

        return [m for m in merged]


class FatherChildrenParser(ElementParser):
    """
    解析 
    <father name="..." cnName="...">
       <things/><things/>...
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
            if not isinstance(child.tag, str):
                continue
            parsed = self.factory.parse(child)
            if element.get("name") != None:
                parsed.update({
                    'father': element.get('name'),
                })
            if element.get("cnName") != None:
                parsed.update({
                    'fatherCnName': element.get('cnName'),
                })  
            children.append(parsed)

        return children




class ThingsParser(ElementParser):
    """
    <things>
        <gift>things;demStone;25,things;demStone;30</gift> 
        <gift>things;demStone;25,things;demStone;30</gift> 
    </things>
    gift 强制解析为列表
    """
    def can_parse(self, element: Element) -> bool:
        return element.tag == 'things'
    def parse(self, element: Element) -> dict[str, Any]:
        result = self.parse_attribs(element)
        
        result.update(
            self.parse_children(element,force_list_for={'gift'})
        )
        return result






def collapse_text(value: str) -> str:
    """description 类多行文本：只去掉行首缩进和制表符，保留换行结构。"""
    if not value:
        return value
    # 按 \r\n / \n 拆行，逐行 strip（去 \t 和行首空格），过滤空行
    lines = [line.strip() for line in value.replace("\r\n", "\n").split("\n")]
    lines = [line for line in lines if line]
    return "\n".join(lines)

class DescriptionParser(ElementParser):
    """description 类多行文本：只去掉行首缩进和制表符，保留换行结构。"""
    def can_parse(self, element: Element) -> bool:
        return element.tag == "description" and self.text(element) is not None
    def parse(self, element: Element) -> str:
        return collapse_text(self.text(element))

def create_things_factory():
    """things 类 XML（father 下是同名事物列表）专用工厂。"""
    factory = create_factory()
    factory.register(ThingsParser(), 200)
    factory.register(DataRootParser(), 200)
    factory.register(FatherChildrenParser(), 100)
    factory.register(DescriptionParser(), 60)
    return factory


if __name__ == "__main__":
    # 端到端小验证：things90.xml vs things90Class.json
    import json
    from pathlib import Path
    from bqyx_parser.parser import load_xml, parse_element
    from bqyx_parser.tools.jsonfile import save_to_json

    xml_dir = Path(r"compiled\v3671\xml")
    out_put_dir = Path(r"output\v3671\json\things")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    factory = create_things_factory()
    xml_things90 = xml_dir / "things90.xml"
    xml_parts = xml_dir / "parts.xml"
    xml_things = xml_dir / "things.xml"
    xml_chip = xml_dir / "chip.xml"

    things90dict = parse_element(load_xml(xml_things90), factory)
    partsdict = parse_element(load_xml(xml_parts), factory)
    thingsdict = parse_element(load_xml(xml_things), factory)
    chipdict = parse_element(load_xml(xml_chip), factory)

    with open(out_put_dir / "things90Class.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(things90dict, ensure_ascii=False, indent=2))
    with open(out_put_dir / "partsClass.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(partsdict, ensure_ascii=False, indent=2))
    with open(out_put_dir / "thingsClass.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(thingsdict, ensure_ascii=False, indent=2))
    with open(out_put_dir / "chipClass.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(chipdict, ensure_ascii=False, indent=2))

    # with open(r"D:\bqyx\rs\resource\things\thingsClass.json", "r", encoding="utf-8") as f:
    #     r = json.load(f)
    #     print(len(r))
    #     print("=== 数据对比结果 ===")
    #     from bqyx_parser.tools.compare import compare_data
    #     compare_data(r, thingsdict)   
