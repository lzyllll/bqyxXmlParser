import json
from typing import Any
from pathlib import Path


from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.xml import Element
from bqyx_parser.parser import load_xml, parse_element_by_factory
from bqyx_parser.tools.logger import get_logger
from bqyx_parser.tools.property import parse_property

logger = get_logger()
class DataRootParser(ElementParser):
    """<data> 下若全是 <gather>，开始解析 gather 并更新每个成就的gather字段"""

    def can_parse(self, element: Element) -> bool:
        if element.tag != "data":
            return False
        child_tags = {child.tag for child in element if isinstance(child.tag, str)}
        return bool(child_tags) and child_tags.issubset({"gather"})

    def parse(self, element: Element) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        for gather in element:
            if isinstance(gather.tag, str) and gather.tag == "gather":
                merged.extend(self.parser_element(gather))
        #转字典
        merged_dict = {achieve['name']: achieve for achieve in merged}
        return merged_dict



class GatherParser(ElementParser):
    """<gather> 下若全是 <father>，把每个 father生成的achieve列表 扁平合并。更新gather字段"""

    def can_parse(self, element: Element) -> bool:
        if element.tag != "gather":
            return False
        child_tags = {child.tag for child in element if isinstance(child.tag, str)}
        return bool(child_tags) and child_tags.issubset({"father"})

    def parse(self, element: Element) -> list[dict[str, Any]]:
        merged: list[dict[str, Any]] = []
        for father in element:
            if isinstance(father.tag, str) and father.tag == "father":
                achieves:list[dict[str, Any]] = self.parser_element(father)
                for achieve in achieves:
                    achieve.update(
                        {
                            'gather': element.get('name'),
                        }
                    )
                merged.extend(achieves)

        return [m for m in merged]

class FatherParser(ElementParser):
    """解析 <father> 下的 <achieve> 元素。设置返回为列表，并更新father字段"""

    def can_parse(self, element: Element) -> bool:
        return element.tag == "father" and any(
            isinstance(child.tag, str) and child.tag == "achieve" for child in element
        )

    def parse(self, element: Element) -> list[dict[str, Any]]:
        achieves: list[dict[str, Any]] = []
        for achieve in element:
            if isinstance(achieve.tag, str) and achieve.tag == "achieve":
                parsed:dict = self.parser_element(achieve)
                parsed.update({
                    'father': element.get('name'),
                })
                if isinstance(parsed, dict):
                    achieves.append(parsed)
        return achieves


def create_achieve_factory():
    """things 类 XML（father 下是同名事物列表）专用工厂。"""
    factory = create_factory()
    factory.register_parser(DataRootParser(factory), priority=100)
    factory.register_parser(GatherParser(factory), priority=90)
    factory.register_parser(FatherParser(factory), priority=80)
    return factory



def generate_achieveGatherFatherMap(xml_path):
    loaded_xml = load_xml(xml_path)
    fathers = loaded_xml.findall(".//father")
    gathers = loaded_xml.findall(".//gather")
    father_gather_list = []

    for father in fathers:
        father_name = father.get("name")
        father_cnName = father.get("cnName")
        father_gather_list.append({
            "type": 'father',
            "name": father_name,
            "cnName": father_cnName
        })

    for gather in gathers:
        gather_name = gather.get("name")
        gather_cnName = gather.get("cnName")
        father_gather_list.append({
            'type': 'gather',
            'name': gather_name,
            'cnName': gather_cnName,
        })
    return father_gather_list


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\json\achieve")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "achieve.xml"
    output_achieve_path = out_put_dir / "achieve.json"
    output_achievefatherGather_path = out_put_dir / "achieveFatherGather.json"

    logger.info("解析 %s", xml_path)
    father_gather_result = generate_achieveGatherFatherMap(xml_path)
    achieve_result = parse_element_by_factory(load_xml(xml_path), create_achieve_factory())

    with open(output_achievefatherGather_path, "w", encoding="utf-8") as f:
        json.dump(father_gather_result, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s", output_achievefatherGather_path)

    with open(output_achieve_path, "w", encoding="utf-8") as f:
        json.dump(achieve_result, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s", output_achieve_path)


if __name__ == "__main__":
    run()
