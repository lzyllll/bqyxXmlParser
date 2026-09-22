from __future__ import annotations

import json
from pathlib import Path

from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.module.equip.base import EquipParser, scan_father_equips
from bqyx_parser.tools.logger import get_logger

logger = get_logger()


def create_jewelry_factory():
    factory = create_factory()
    factory.register_parser(EquipParser(factory), priority=80)
    return factory


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\resource\equip\jewelry")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    output_path = out_put_dir / "jewelryData.json"
    logger.info("解析 jewelry (扫描所有 XML，father name='jewelry')...")

    factory = create_jewelry_factory()
    jewelries = scan_father_equips(xml_dir, "jewelry", factory, inject_father_name=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(jewelries, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s (共 %d 条饰品定义)", output_path, len(jewelries))


if __name__ == "__main__":
    run()
