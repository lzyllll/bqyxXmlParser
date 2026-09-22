from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bqyx_parser.tools.logger import get_logger

logger = get_logger()


def process_rare_arms_chip(
    chip_data: list[dict[str, Any]],
    arms_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """根据 thingsDefineGroup.ts 的 processRareArmsChip 逻辑生成稀有武器碎片列表。"""
    chip_map = {item["name"]: item for item in chip_data}
    base_d0 = chip_map.get("rareChip", {"father": "rareChip", "fatherCnName": "稀有碎片"})

    result: list[dict[str, Any]] = []
    for arms in arms_data:
        if arms.get("color") == "red" and arms.get("chipNum", 0) > 0:
            name = arms["name"]
            cn_name = arms.get("cnName", "") + "稀有碎片"
            desc = "合成" + cn_name + "所需物品。" + (arms.get("description") or "")
            item: dict[str, Any] = {
                "father": base_d0.get("father", "rareChip"),
                "fatherCnName": base_d0.get("fatherCnName", "稀有碎片"),
                "secType": "arms",
                "cnName": cn_name,
                "name": name,
                "addDropDefineB": 1,
                "btnList": ["compose"],
                "iconUrl": "ThingsIcon/" + name,
                "description": desc,
                "smeltD": {
                    "price": 10,
                    "type": "armsChip",
                    "grade": 1,
                },
            }
            result.append(item)
    return result


def process_black_equip_chip(
    chip_data: list[dict[str, Any]],
    black_equip_data: list[dict[str, Any]] | dict[str, Any],
) -> list[dict[str, Any]]:
    """根据 thingsDefineGroup.ts 的 processBlackEquipChip 逻辑生成黑色装备碎片列表。"""
    arr: list[dict[str, Any]] = []
    chip_map: dict[str, dict[str, Any]] = {}
    for item in chip_data:
        it = dict(item)
        arr.append(it)
        chip_map[it["name"]] = it

    base_d0 = chip_map.get("blackChip", {"father": "blackChip", "fatherCnName": "黑色碎片"})

    if isinstance(black_equip_data, list) and black_equip_data:
        black_suits = black_equip_data[0].get("father", [])
    elif isinstance(black_equip_data, dict):
        black_suits = black_equip_data.get("father", [])
    else:
        black_suits = []

    for father in black_suits:
        father_name = father.get("name", "")
        for image in father.get("image", []):
            part_type = image.get("type", "")
            equip_name = f"{father_name}_{part_type}"
            equip_cn = image.get("cnName", "")
            equip_lv = image.get("itemsLevel", 81)

            d0 = chip_map.get(equip_name)
            if not d0:
                d0 = {
                    "name": equip_name,
                    "cnName": equip_cn + "碎片",
                }
                chip_map[equip_name] = d0
                arr.append(d0)

            d0["father"] = base_d0.get("father", "blackChip")
            d0["fatherCnName"] = base_d0.get("fatherCnName", "黑色碎片")
            d0["secType"] = "equip"
            d0["iconUrl"] = "ThingsIcon/" + d0["name"]
            d0["itemsLevel"] = equip_lv
            d0["addDropDefineB"] = 1

            lv0 = d0["itemsLevel"]
            if lv0 < 86:
                smelt = {"price": 2, "type": "equipChip", "grade": 1}
            elif lv0 < 91:
                smelt = {
                    "price": 10,
                    "type": "equipChip",
                    "grade": 2,
                    "addType": "armsEquip",
                    "maxNum": 1,
                }
            else:
                smelt = {"price": 1, "type": "equipChip"}

            d0["smeltD"] = smelt

            btn_list = ["compose", "composeNum"]
            can_conver = (
                d0["secType"] == "equip"
                and d0["itemsLevel"] < 91
                and d0["father"] == "blackChip"
                and "oracleSuit" not in d0["name"]
            )
            if can_conver:
                btn_list.append("conver")
            d0["btnList"] = btn_list

    return [x for x in arr if x.get("secType") == "equip" and x.get("father") == "blackChip"]


def process_black_arms_chip(
    chip_data: list[dict[str, Any]],
    arms_data: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """根据 thingsDefineGroup.ts 的 processBlackArmsChip 逻辑生成黑色武器碎片列表。"""
    arr: list[dict[str, Any]] = []
    chip_map: dict[str, dict[str, Any]] = {}
    for item in chip_data:
        it = dict(item)
        arr.append(it)
        chip_map[it["name"]] = it

    base_d0 = chip_map.get("blackChip", {"father": "blackChip", "fatherCnName": "黑色碎片"})

    black_arms = [a for a in arms_data if a.get("color") == "black"]
    for arms in black_arms:
        if arms.get("chipNum", 0) > 0:
            name = arms["name"]
            d0 = chip_map.get(name)
            if not d0:
                d0 = {
                    "name": name,
                    "cnName": arms.get("cnName", "") + "碎片",
                }
                chip_map[name] = d0
                arr.append(d0)

            d0["father"] = base_d0.get("father", "blackChip")
            d0["fatherCnName"] = base_d0.get("fatherCnName", "黑色碎片")
            d0["secType"] = "arms"
            d0["name"] = name
            d0["addDropDefineB"] = 1
            if not d0.get("iconUrl"):
                d0["iconUrl"] = "ThingsIcon/" + name
            d0["itemsLevel"] = arms.get("composeLv", 81)

            lv0 = d0["itemsLevel"]
            if lv0 < 86:
                smelt = {"price": 2, "type": "armsChip", "grade": 1}
            elif lv0 < 91:
                smelt = {
                    "price": 10,
                    "type": "armsChip",
                    "grade": 2,
                    "addType": "armsEquip",
                    "maxNum": 1,
                }
            else:
                smelt = {"price": 1, "type": "armsChip"}

            if lv0 >= 90:
                smelt.pop("grade", None)

            d0["smeltD"] = smelt
            d0["btnList"] = ["compose"]

    return [x for x in arr if x.get("secType") == "arms" and x.get("father") == "blackChip"]


def generate_all_chips(
    chip_data: list[dict[str, Any]],
    arms_data: list[dict[str, Any]],
    black_equip_data: list[dict[str, Any]] | dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    """生成所有三种碎片数据。"""
    return {
        "rareArmsChip": process_rare_arms_chip(chip_data, arms_data),
        "blackEquipChip": process_black_equip_chip(chip_data, black_equip_data),
        "blackArmsChip": process_black_arms_chip(chip_data, arms_data),
    }


if __name__ == "__main__":
    out_dir = Path(r"output\v3671\resource\things")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 读取输入数据：优先 output/v3671/resource，兜底 D:/bqyx/rs/resource
    chip_path = out_dir / "chipClass.json"
    if not chip_path.is_file():
        chip_path = Path(r"D:\bqyx\rs\resource\things\chipClass.json")

    arms_path = Path(r"output\v3671\resource\arms\armsClass.json")
    if not arms_path.is_file():
        arms_path = Path(r"D:\bqyx\rs\resource\arms\armsClass.json")

    black_equip_path = Path(r"output\v3671\resource\equip\blackEquip.json")
    if not black_equip_path.is_file():
        black_equip_path = Path(r"D:\bqyx\rs\resource\equip\blackEquip.json")

    logger.info("读取 chip 数据: %s", chip_path)
    chip_data = json.loads(chip_path.read_text(encoding="utf-8"))

    logger.info("读取 arms 数据: %s", arms_path)
    arms_data = json.loads(arms_path.read_text(encoding="utf-8"))

    logger.info("读取 blackEquip 数据: %s", black_equip_path)
    black_equip_data = json.loads(black_equip_path.read_text(encoding="utf-8"))

    chips_result = generate_all_chips(chip_data, arms_data, black_equip_data)

    for chip_name, data in chips_result.items():
        out_file = out_dir / f"{chip_name}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("已保存 %s (共 %d 条)", out_file, len(data))

