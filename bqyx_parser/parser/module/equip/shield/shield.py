from __future__ import annotations

import json
from pathlib import Path

from bqyx_parser.parser.attrib.base import AttribParser
from bqyx_parser.parser.factory import create_factory
from bqyx_parser.parser.module.equip.base import EquipParser, scan_father_equips
from bqyx_parser.parser.xml import Element
from bqyx_parser.tools.logger import get_logger

logger = get_logger()


class FloatAttribParser(AttribParser):
    """强制转换为浮点数。"""

    def parse(self, key: str, value: str, element: Element | None = None) -> float:
        return float(value)


def create_shield_factory():
    factory = create_factory()
    factory.attrib_registry.register_name("cd", FloatAttribParser())
    factory.attrib_registry.register_name("delay", FloatAttribParser())
    factory.register_parser(EquipParser(factory), priority=80)
    return factory


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\resource\equip\shield")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    output_path = out_put_dir / "shieldData.json"
    logger.info("解析 shield (扫描所有 XML，father name='shield')...")

    factory = create_shield_factory()
    shields = scan_father_equips(xml_dir, "shield", factory, inject_father_name=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(shields, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s (共 %d 条护盾定义)", output_path, len(shields))


if __name__ == "__main__":
    run()
