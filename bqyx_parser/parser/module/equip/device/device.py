from __future__ import annotations

import json
from pathlib import Path

from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.module.equip.base import DescriptionAttribParser, EquipParser, scan_father_equips
from bqyx_parser.tools.logger import get_logger

logger = get_logger()


def create_device_factory():
    factory = create_factory()
    factory.attrib_registry.register_name("description", DescriptionAttribParser())
    factory.register_parser(EquipParser(factory), priority=80)
    return factory


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\resource\equip\device")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    output_path = out_put_dir / "deviceData.json"
    logger.info("解析 device (扫描所有 XML，father name='device')...")

    factory = create_device_factory()
    all_equips = scan_father_equips(xml_dir, "device", factory, inject_father_name=False)

    result = {
        "name": "device",
        "cnName": "装置",
        "equip": all_equips,
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s (共 %d 条装置定义)", output_path, len(all_equips))


if __name__ == "__main__":
    run()
