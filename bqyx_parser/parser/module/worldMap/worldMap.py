from __future__ import annotations

import glob
import json
from pathlib import Path
from typing import Any

from bqyx_parser.parser import Element, load_xml
from bqyx_parser.tools.logger import get_logger

logger = get_logger()


def parse_place(p: Element) -> dict[str, Any]:
    """解析 worldMap.xml 中的单个 place 节点。"""
    obj: dict[str, Any] = {}

    # 属性解析
    for k, v in p.attrib.items():
        try:
            obj[k] = int(v)
        except ValueError:
            obj[k] = v

    # 子节点解析
    for child in p:
        tag = child.tag
        if tag == "description":
            continue
        elif tag == "levelArr":
            levels: list[str] = []
            for lvl in child.iter("level"):
                lvl_name = lvl.findtext("name")
                if lvl_name:
                    levels.append(lvl_name)
            obj["levelArr"] = levels
        elif tag in ("demBossSkillArr", "demSkillArr", "demNoModeArr", "linkArr", "labelArr"):
            text = (child.text or "").strip()
            arr = [s.strip() for s in text.split(",") if s.strip()] if text else []
            obj[tag] = arr
        elif tag in ("mustWinShowB", "noTaskB", "noEndlessB", "firstShowB"):
            text = (child.text or "").strip()
            obj[tag] = bool(int(text)) if text.isdigit() else bool(text)
        else:
            obj[tag] = (child.text or "").strip()

    # 规范化必须字段：demBossSkillArr, demSkillArr, demNoModeArr, levelArr
    for k in ("demBossSkillArr", "demSkillArr", "demNoModeArr", "levelArr"):
        if k not in obj:
            obj[k] = []

    return obj


def parse_world_map(xml_path: Path) -> dict[str, Any]:
    """解析 worldMap.xml 并返回完整的地图层次结构。"""
    root = load_xml(xml_path)
    fathers: list[dict[str, Any]] = []
    for f in root.findall("father"):
        f_obj = {
            "name": f.attrib.get("name", ""),
            "cnName": f.attrib.get("cnName", ""),
            "places": [parse_place(p) for p in f.findall("place")],
        }
        fathers.append(f_obj)
    return {"fathers": fathers}


def parse_last_level_name(xml_path: Path) -> dict[str, str]:
    """从 bossMatchList.xml 解析前代历史关卡名映射 lastLevelName。"""
    root = load_xml(xml_path)
    last_levels: dict[str, str] = {}
    for body in root.iter("body"):
        if body.attrib.get("name") == "lastLevelName":
            text = body.text or ""
            for line in text.strip().splitlines():
                line = line.strip()
                if ":" in line:
                    k, v = line.split(":", 1)
                    last_levels[k.strip()] = v.strip()
    return last_levels


def parse_all_level_bosses(xml_dir: Path) -> dict[str, dict[str, Any]]:
    """扫描所有关卡 XML，解析所有关卡的原生 Boss 及其 <fixed target> 继承关系。"""
    levels: dict[str, dict[str, Any]] = {}
    for path in xml_dir.glob("*.xml"):
        try:
            root = load_xml(path)
            for lvl in root.iter("level"):
                name = lvl.attrib.get("name")
                if not name:
                    continue
                fixed_elem = lvl.find("fixed")
                fixed_target = fixed_elem.attrib.get("target") if fixed_elem is not None else None
                bosses: list[str] = []
                for u in lvl.iter("unit"):
                    if u.attrib.get("unitType", "").lower() == "boss":
                        cn = u.attrib.get("cnName")
                        if cn and cn not in bosses:
                            bosses.append(cn)
                if name not in levels or (not levels[name]["bosses"] and bosses):
                    levels[name] = {"bosses": bosses, "fixed_target": fixed_target}
                elif fixed_target and not levels[name]["fixed_target"]:
                    levels[name]["fixed_target"] = fixed_target
        except Exception:
            continue
    return levels


def resolve_level_bosses(
    level_name: str,
    levels_data: dict[str, dict[str, Any]],
    visited: set[str] | None = None,
) -> list[str]:
    """递归解析指定关卡的真实 Boss 列表（自动追踪 fixed target 继承）。"""
    if "_plot" in level_name:
        return []
    if visited is None:
        visited = set()
    if level_name in visited:
        return []
    visited.add(level_name)

    info = levels_data.get(level_name)
    if not info:
        return []

    bosses = list(info["bosses"])
    if not bosses and info["fixed_target"]:
        bosses = resolve_level_bosses(info["fixed_target"], levels_data, visited)
    return bosses


def parse_last_level_boss(
    world_map_data: dict[str, Any],
    last_level_name: dict[str, str],
    levels_data: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """生成 infected_area 所有 78 张地图的终关及 Boss 映射。"""
    derived_bosses: dict[str, dict[str, Any]] = {}
    for father in world_map_data["fathers"]:
        if father.get("name") == "infected_area":
            for p in father.get("places", []):
                name = p.get("name")
                if not name:
                    continue
                levels_list = p.get("levelArr", [])
                lvl = last_level_name.get(name, levels_list[-1] if levels_list else "")
                bosses = resolve_level_bosses(lvl, levels_data)
                derived_bosses[name] = {"level": lvl, "bosses": bosses}
    return derived_bosses


def build_unified_world_map(
    world_map_data: dict[str, Any],
    last_level_bosses: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """构建统一地图模型（整合 Boss 关卡及 Boss 列表，技能保持原生技能名引用）。"""
    unified_fathers = []
    for father in world_map_data["fathers"]:
        f_name = father.get("name", "")
        f_cn = father.get("cnName", "")
        unified_places = []
        for p in father.get("places", []):
            place = dict(p)
            name = place.get("name", "")

            # 注入 Boss 终关与 Boss 列表
            boss_info = last_level_bosses.get(name)
            if boss_info:
                place["bossLevel"] = boss_info.get("level", "")
                place["bosses"] = list(boss_info.get("bosses", []))
            else:
                levels = place.get("levelArr", [])
                place["bossLevel"] = levels[-1] if levels else ""
                place["bosses"] = []

            unified_places.append(place)

        unified_fathers.append({
            "name": f_name,
            "cnName": f_cn,
            "places": unified_places,
        })

    return {"fathers": unified_fathers}


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\resource\worldMap")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    world_map_xml = xml_dir / "worldMap.xml"
    boss_match_xml = xml_dir / "bossMatchList.xml"

    logger.info("=== 开始解析 worldMap 模块 ===")

    # 1. 基础地图解析与关卡 Boss 追踪
    logger.info("解析地图与关卡 Boss...")
    world_map_data = parse_world_map(world_map_xml)
    last_level_name = parse_last_level_name(boss_match_xml)
    levels_data = parse_all_level_bosses(xml_dir)
    last_level_bosses = parse_last_level_boss(world_map_data, last_level_name, levels_data)

    # 2. 构建并保存 worldMap.json (技能由 skill 模块水合)
    logger.info("构建统一数据模型 worldMap.json...")
    unified_map = build_unified_world_map(world_map_data, last_level_bosses)
    wm_output = out_put_dir / "worldMap.json"
    with open(wm_output, "w", encoding="utf-8") as f:
        json.dump(unified_map, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s", wm_output)
    logger.info("=== worldMap 模块解析完成 ===")


if __name__ == "__main__":
    run()

