"""解析模块中央注册表与调度器。"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

from bqyx_parser.parser.module import (
    achieve,
    active,
    arms,
    armsSkill,
    body,
    drop,
    equip,
    head,
    parts,
    peak,
    pet,
    post,
    skill,
    skin,
    things,
    top,
    union,
    vip,
    worldMap,
)

logger = logging.getLogger(__name__)

# 模块名 -> (描述, 运行函数)
# 注意顺序：equip 和 arms 优先运行，以便 things 模块合成芯片时获取武器与黑色装备数据
MODULE_MAP: dict[str, tuple[str, Callable[[Path, Path], None]]] = {
    "equip": ("装备、时装与部件属性", equip.run),
    "arms": ("武器数据与充能", arms.run),
    "skin": ("武器与副手皮肤 (armsSkin.json, weaponSkin.json)", skin.run),
    "armsSkin": ("武器与副手皮肤 (armsSkin.json, weaponSkin.json)", skin.run),
    "skill": ("统一技能定义与词缀 (skill.json)", skill.run),
    "armsSkill": ("武器技能 (armsSkillClass.json)", armsSkill.run),
    "things": ("道具、强化与碎片合成", things.run),
    "worldMap": ("世界地图、关卡Boss与修罗词缀 (worldMap.json)", worldMap.run),
    "achieve": ("成就与勋章", achieve.run),
    "union": ("军团建筑、科技与任务", union.run),
    "top": ("顶部榜单与排行 (topClass.json)", top.run),
    "drop": ("掉落颜色与范围", drop.run),
    "body": ("英雄与怪物基础属性", body.run),
    "head": ("称号与荣誉", head.run),
    "parts": ("配件属性与稀有属性", parts.run),
    "peak": ("巅峰属性与战舰", peak.run),
    "pet": ("宠物与强化", pet.run),
    "post": ("邮件与公告", post.run),
    "vip": ("VIP等级与特权礼包", vip.run),
    "active": ("活跃度与任务", active.run),
}


def get_available_modules() -> dict[str, str]:
    """返回所有可用模块名称及其描述。"""
    return {k: v[0] for k, v in MODULE_MAP.items()}


def run_module(name: str, xml_dir: Path, output_dir: Path) -> None:
    """运行指定名称的单个模块。"""
    if name not in MODULE_MAP:
        available = ", ".join(MODULE_MAP.keys())
        raise ValueError(f"未知模块 '{name}'。可用模块: {available}")

    desc, runner = MODULE_MAP[name]
    logger.info(">>> 开始运行模块 [%s]: %s", name, desc)
    runner(xml_dir, output_dir)
    logger.info("<<< 模块 [%s] 运行完成", name)


def run_all(xml_dir: Path, output_dir: Path) -> None:
    """按依赖拓扑顺序运行全部模块。"""
    total = len(MODULE_MAP)
    logger.info("=== 开始全量解析 (共 %d 个模块) ===", total)
    for idx, (name, (desc, runner)) in enumerate(MODULE_MAP.items(), 1):
        logger.info("[%d/%d] 正在解析模块 [%s]: %s ...", idx, total, name, desc)
        runner(xml_dir, output_dir)
    logger.info("=== 全量解析完成 (全部 %d 个模块均已成功生成) ===", total)

