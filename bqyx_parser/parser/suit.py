"""套装和装备 XML 解析器。"""
from __future__ import annotations

import json
from pathlib import Path

from bqyx_parser.parser.xml import load_xml, parse_element
from bqyx_parser.tools import load_last_version


def parse_suit_pro(suit_attr_str: str) -> dict[str, float]:
    """解析 suitPro，例如 hurtAll:1.15 或 hurtAll_1.15。"""
    attr_dict: dict[str, float] = {}
    for attr in suit_attr_str.split(","):
        key, value = attr.split(":") if ":" in attr else attr.split("_")
        attr_dict[key] = float(value)
    return attr_dict


def parse_suits(version: str | None = None) -> tuple[dict, dict]:
    """读取黑装、普通装、暗金装，返回套装加成和单件装备表。"""
    version = version or load_last_version()
    files = [
        Path("output", version, "xml", "other", "equipImageClass.xml"),
        Path("output", version, "xml", "other", "blackEquipClass.xml"),
        Path("output", version, "xml", "other", "darkgoldEquipClass.xml"),
    ]
    suit_result: dict = {}
    equip_result: dict = {}
    for xml_path in files:
        root = load_xml(xml_path)
        for father in root.findall(".//father"):
            if father.get("suitPro"):
                suit_result[father.get("name")] = {
                    "RoleBonus": parse_suit_pro(father.get("suitPro")),
                    "cnName": father.get("cnName"),
                }
            range_value = father.getparent().attrib.get("range")
            for image in father.findall("image"):
                name = father.get("name") + "_" + image.find("type").text
                equip_result[name] = parse_element(image)
                if range_value:
                    start, mx1, mx2, end = list(map(int, range_value.split(",")))
                    equip_result[name]["level"] = {
                        "startLv": start,
                        "maxLv1": mx1,
                        "maxLv2": mx2,
                        "endLv": end,
                    }
    return suit_result, equip_result


def main() -> None:
    version = load_last_version()
    output_dir = Path("output", version, "json", "equip")
    output_dir.mkdir(parents=True, exist_ok=True)
    suit_result, equip_result = parse_suits(version)
    (output_dir / "suit.json").write_text(
        json.dumps(suit_result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (output_dir / "equip.json").write_text(
        json.dumps(equip_result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
