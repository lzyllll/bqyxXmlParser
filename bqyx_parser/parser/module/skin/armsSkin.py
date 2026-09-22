from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bqyx_parser.parser.convert import safe_eval
from bqyx_parser.parser.xml import load_xml
from bqyx_parser.tools.logger import get_logger

logger = get_logger()


def parse_arms_skin(xml_path: str | Path) -> list[dict[str, Any]]:
    """使用统一安全加载函数 load_xml 解析 armsSkin.xml，返回枪械皮肤列表。"""
    root = load_xml(xml_path)
    result: list[dict[str, Any]] = []

    for gather in root.findall(".//gather"):
        gather_name = gather.attrib.get("name", "arms")
        for father in gather.findall(".//father"):
            father_name = father.attrib.get("name", "")
            father_cn = father.attrib.get("cnName", "")
            for body in father.findall(".//body"):
                item: dict[str, Any] = {}
                for k, v in body.attrib.items():
                    if k in ("name", "cnName", "url", "icon", "color", "author", "au", "info", "items", "goods"):
                        item[k] = str(v)
                    elif k in ("lightColor", "bulletColor"):
                        try:
                            item[k] = int(v, 16) if v.startswith(("0x", "0X")) else int(v)
                        except ValueError:
                            item[k] = safe_eval(v)
                    elif k in ("evoLv", "vip", "stren"):
                        try:
                            item[k] = int(v)
                        except ValueError:
                            item[k] = safe_eval(v)
                    elif k == "p":
                        try:
                            item[k] = float(v) if "." in v else int(v)
                        except ValueError:
                            item[k] = safe_eval(v)
                    else:
                        item[k] = safe_eval(v)

                item["fatherName"] = father_name
                if father_cn:
                    item["fatherCnName"] = father_cn
                if gather_name:
                    item["gather"] = gather_name
                result.append(item)

    return result


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\resource\skin")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "armsSkin.xml"
    output_path = out_put_dir / "armsSkin.json"

    logger.info("解析 %s", xml_path)
    skins = parse_arms_skin(xml_path)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(skins, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s (共 %d 条皮肤定义)", output_path, len(skins))


if __name__ == "__main__":
    run()
