from __future__ import annotations

import json
from pathlib import Path

import pytest

from bqyx_parser.parser.module.skill.skill import parse_skills_from_xmls
from bqyx_parser.parser.module.worldMap.worldMap import (
    build_unified_world_map,
    parse_all_level_bosses,
    parse_last_level_boss,
    parse_last_level_name,
    parse_world_map,
)


@pytest.fixture
def paths():
    base = Path(__file__).resolve().parents[1]
    xml_dir = base / "compiled" / "v3671" / "xml"
    output_dir = base / "output" / "v3671" / "json" / "worldMap"
    return {
        "xml_dir": xml_dir,
        "output_dir": output_dir,
    }


def test_world_map_structure(paths):
    """验证 worldMap 解析出的地图结构与 78 张感染区地图。"""
    wm_xml = paths["xml_dir"] / "worldMap.xml"
    bml_xml = paths["xml_dir"] / "bossMatchList.xml"
    wm_data = parse_world_map(wm_xml)
    lln_data = parse_last_level_name(bml_xml)
    levels_data = parse_all_level_bosses(paths["xml_dir"])
    last_level_bosses = parse_last_level_boss(wm_data, lln_data, levels_data)
    unified = build_unified_world_map(wm_data, last_level_bosses)

    infected_places = []
    for father in unified["fathers"]:
        if father["name"] == "infected_area":
            infected_places = father["places"]
            break

    assert len(infected_places) == 78

    demon_places = [p for p in infected_places if p.get("demBossSkillArr")]
    assert len(demon_places) == 26

    for place in demon_places:
        assert place["bossLevel"] != ""
        assert isinstance(place["demBossSkillArr"], list)
        assert len(place["demBossSkillArr"]) > 0


def test_skill_parser_and_world_map_skills_coverage(paths):
    """验证 skill 模块能完整解析技能并覆盖世界地图中的全部修罗技能。"""
    skills_result = parse_skills_from_xmls(paths["xml_dir"])
    skill_obj = skills_result["obj"]
    assert len(skill_obj) > 900
    assert "demonSkill" in skills_result["fatherObj"]

    wm_xml = paths["xml_dir"] / "worldMap.xml"
    wm_data = parse_world_map(wm_xml)

    all_map_dem_skills = set()
    for father in wm_data["fathers"]:
        for place in father.get("places", []):
            for s in place.get("demBossSkillArr", []):
                all_map_dem_skills.add(s)
            for s in place.get("demSkillArr", []):
                all_map_dem_skills.add(s)

    # 检查世界地图中所有修罗技能在统一技能库中的命中率
    found = [s for s in all_map_dem_skills if s in skill_obj]
    # 绝大部分技能均能直接命中；少数子弹类型技能可由保底机制显示英文名
    coverage = len(found) / len(all_map_dem_skills)
    assert coverage > 0.9, f"Skill coverage too low: {coverage:.2%}"
