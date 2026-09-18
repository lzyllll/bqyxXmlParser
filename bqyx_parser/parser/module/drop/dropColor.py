from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bqyx_parser.parser import load_xml, parse_element_by_factory
from bqyx_parser.parser.convert import safe_eval
from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.xml import Element
from bqyx_parser.tools.logger import get_logger

logger = get_logger()


class DataRootParser(ElementParser):
    """<data> 解析所有 <father>。"""

    def can_parse(self, element: Element) -> bool:
        return element.tag == "data"

    def parse(self, element: Element) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for child in element:
            if isinstance(child.tag, str) and child.tag == "father":
                result.append(self.parser_element(child))
        return result


class FatherParser(ElementParser):
    """
    <father name="..." cnName="...">
        <body>...</body>
        <equip>...</equip>
        <arms>...</arms>
    </father>
    """

    def can_parse(self, element: Element) -> bool:
        return element.tag == "father"

    def parse(self, element: Element) -> dict[str, Any]:
        result: dict[str, Any] = {
            "name": element.attrib["name"],
        }
        if "cnName" in element.attrib:
            result["cnName"] = element.attrib["cnName"]

        for child in element:
            if isinstance(child.tag, str) and child.tag in ("body", "equip", "arms"):
                result[child.tag] = self.parser_element(child)

        return result


class DropTableParser(ElementParser):
    """
    解析 body, equip, arms 等按列存储的子元素，将其转置为行字典列表。
    子元素文本为逗号分隔的列数据，例如：
        <name>white, green, blue</name>
        <lvRange>-5~0, -5~0, -4~0</lvRange>
    将转置为：
        [
            {"name": "white", "lvRange": [-5.0, 0.0]},
            {"name": "green", "lvRange": [-5.0, 0.0]},
            ...
        ]
    """

    def can_parse(self, element: Element) -> bool:
        return element.tag in ("body", "equip", "arms")

    def _parse_value(self, key: str, val_str: str) -> Any:
        val_str = val_str.strip()
        if key == "name":
            return val_str
        if "range" in key.lower() or "Range" in key:
            return [float(x.strip()) for x in val_str.split("~")]
        return safe_eval(val_str)

    def parse(self, element: Element) -> list[dict[str, Any]]:
        cols: dict[str, list[Any]] = {}
        for child in element:
            if not isinstance(child.tag, str):
                continue
            key = child.tag
            raw_text = child.text or ""
            vals = [self._parse_value(key, v) for v in raw_text.split(",") if v.strip()]
            cols[key] = vals

        col_names = list(cols.keys())
        num_rows = len(cols[col_names[0]]) if col_names else 0
        rows: list[dict[str, Any]] = []
        for i in range(num_rows):
            row = {k: cols[k][i] for k in col_names}
            rows.append(row)
        return rows


def create_dropColor_factory():
    factory = create_factory()
    factory.register_parser(DataRootParser(factory), priority=100)
    factory.register_parser(FatherParser(factory), priority=90)
    factory.register_parser(DropTableParser(factory), priority=80)
    return factory


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\json\drop")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "dropColor.xml"
    output_path = out_put_dir / "dropColor.json"

    logger.info("解析 %s", xml_path)
    result = parse_element_by_factory(load_xml(xml_path), create_dropColor_factory())
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s", output_path)


if __name__ == "__main__":
    run()
