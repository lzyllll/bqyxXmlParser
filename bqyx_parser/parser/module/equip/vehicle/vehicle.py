from __future__ import annotations

import json
from pathlib import Path

from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.element.defaults import TextElementParser
from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.module.equip.base import EquipParser, scan_father_equips
from bqyx_parser.parser.xml import Element
from bqyx_parser.tools.logger import get_logger

logger = get_logger()

# 载具支持的 fatherName 类别
VEHICLE_FATHER_NAMES = {"car", "aircraft", "beast", "fit", "vehicle"}


class RawAttribParser(ElementParser):
    """保持 main / sub 属性为原始字符串字典。"""

    def can_parse(self, element: Element) -> bool:
        return element.tag in ("main", "sub")

    def parse(self, element: Element) -> dict[str, str]:
        return dict(element.attrib)


def create_vehicle_factory():
    factory = create_factory()
    factory.register_parser(RawAttribParser(), priority=100)
    factory.register_parser(EquipParser(factory), priority=90)
    factory.register_tag("specialInfoArr", TextElementParser())
    return factory


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\resource\equip\vehicle")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    output_path = out_put_dir / "vehicleData.json"
    logger.info("解析 vehicle (扫描所有 XML，过滤 %s)...", VEHICLE_FATHER_NAMES)

    factory = create_vehicle_factory()
    vehicles = scan_father_equips(
        xml_dir,
        VEHICLE_FATHER_NAMES,
        factory,
        inject_father_name=True,
        primary_file="vehicle.xml",
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(vehicles, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s (共 %d 条载具定义)", output_path, len(vehicles))


if __name__ == "__main__":
    run()
