"""技能定义模块 (参照 Flash AS3 SkillDefineGroup.as 及 DefineGroup.as 实现)。

负责解析 DefineGroup.as 中加载的全部 53 个技能 XML，
生成统一技能索引数据 (skill.json)。
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from bqyx_parser.parser import Element, load_xml

logger = logging.getLogger(__name__)

# AS3 DefineGroup.as 中 this.skill.inData_byXML 调用的 XML 文件基准列表（按调用顺序）
SKILL_XML_NAMES: list[str] = [
    "foodRaw",
    "sceneSkill",
    "redFire",
    "rocketCate",
    "meltFlamer",
    "waterFlamer",
    "yearPig",
    "yearDog",
    "yearSnake",
    "yearChicken",
    "yearHourse",
    "yearMouse",
    "yearDragon",
    "lightCone",
    "yearMonkey",
    "yearRabbit",
    "penGun",
    "yearCattle",
    "yearTiger",
    "greedySnake",
    "pianoGun",
    "yearSheep",
    "skyArch",
    "skill",
    "enemySkill",
    "demonSkill",
    "nightmareSkill",
    "wilderEnemySkill",
    "ninetySkill",
    "FightKingSkill",
    "SpiderKingSkill",
    "FightPigSkill",
    "armsSkill",
    "heroSkill",
    "wenJieSkill",
    "xinLingSkill",
    "yingSkill",
    "equipSkill",
    "outfitSkill",
    "vehicleSkill",
    "thingsSkill",
    "petSkill",
    "darkgoldEquip",
    "unionSkill",
    "deviceSkill",
    "weaponSkill",
    "jewelry",
    "shield",
    "loveSkill",
    "loveSkillWenJie",
    "loveSkillZangShi",
    "loveSkillXinLing",
    "loveSkillXiaoMei",
    "peakSkill",
    "partsSkill",
]

FLOAT_FIELDS: set[str] = {
    "mul",
    "secMul",
    "cd",
    "firstCd",
    "duration",
    "intervalT",
    "minTriggerT",
    "firstTriggerT",
    "cdRandomRange",
    "delay",
    "doGap",
    "range",
    "minRange",
    "conditionRange",
    "value",
    "studyMustMul",
    "upgradeMustMul",
    "coinMustMul",
}

INT_FIELDS: set[str] = {
    "mustLv",
    "continueNum",
    "lv",
    "index",
    "haveEffectBuletHitNum",
}

LIST_FIELDS: set[str] = {
    "otherConditionArr",
    "passiveSkillArr",
    "linkArr",
    "applyArr",
    "effectProArr",
    "preEffectArr",
    "effectInfoArr",
    "labelArr",
}

PER_PRO_KEYS: set[str] = {"secMul", "mul", "obj.pro", "obj.per"}


def parse_obj_field(text: str) -> dict[str, Any]:
    """解析 obj 标签/属性中的内容（可能为 JSON 或 key:value 格式）。"""
    text = text.strip()
    if not text:
        return {}
    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except Exception:
            pass
    try:
        return json.loads("{" + text + "}")
    except Exception:
        pass
    res: dict[str, Any] = {}
    for part in text.split(","):
        if ":" in part:
            k, v = part.split(":", 1)
            k = k.strip().strip('"\'')
            v = v.strip().strip('"\'')
            if v in ("true", "True"):
                res[k] = True
            elif v in ("false", "False"):
                res[k] = False
            else:
                try:
                    res[k] = float(v) if "." in v else int(v)
                except ValueError:
                    if (v.startswith("[") and v.endswith("]")) or (v.startswith("{") and v.endswith("}")):
                        try:
                            res[k] = json.loads(v)
                            continue
                        except Exception:
                            pass
                    res[k] = v
    return res


def format_pro_text(data: dict[str, Any], prop_name: str, op: str = "") -> str:
    """对应 AS3 SkillDefine.getProText，将属性占位符转为显示文本。"""
    parts = prop_name.split(".")
    val: Any = data
    for p in parts:
        if isinstance(val, dict):
            val = val.get(p)
        elif isinstance(val, list) and p.isdigit():
            idx = int(p)
            val = val[idx] if idx < len(val) else None
        else:
            val = None
            break
    if val is None:
        return ""

    is_per = prop_name in PER_PRO_KEYS or prop_name.startswith("effectProArr.")
    try:
        num_val = float(val)
        if op == "1-":
            num_val = 1.0 - num_val
        elif op == "-1":
            num_val = num_val - 1.0
        elif op == "/2":
            num_val = num_val / 2.0

        if is_per:
            pct = round(num_val * 100, 2)
            return f"{pct:.1f}%" if pct % 1 != 0 else f"{int(pct)}%"
        else:
            return f"{int(num_val)}" if num_val.is_integer() else f"{num_val}"
    except (ValueError, TypeError):
        return str(val)


def format_description(desc: str, data: dict[str, Any]) -> str:
    """对应 AS3 SkillDefine.swapProText 与 getDescription。"""
    if not desc:
        return ""

    def repl(m: re.Match[str]) -> str:
        expr = m.group(1).strip()
        if expr.startswith("1-"):
            return format_pro_text(data, expr[2:], "1-")
        elif expr.endswith("-1"):
            return format_pro_text(data, expr[:-2], "-1")
        elif expr.endswith("/2"):
            return format_pro_text(data, expr[:-2], "/2")
        else:
            return format_pro_text(data, expr)

    res = re.sub(r"\[([^\]]+)\]", repl, desc)
    res = res.replace("{n}", "\n").replace("{", "<").replace("}", ">")
    return res


def parse_skill_node(elem: Element, father_name: str, father_cn_name: str) -> dict[str, Any]:
    """解析单个 <skill> 节点，参照 AS3 SkillDefine.inData_byXML。"""
    data: dict[str, Any] = {
        "father": father_name,
        "fatherCnName": father_cn_name,
        "conditionType": "passive",
        "addType": "state",
        "haveEffectBuletHitNum": 9999,
        "firstCd": -1.0,
        "cd": 0.0,
        "duration": 0.0,
        "intervalT": 0.0,
        "mul": 1.0,
        "secMul": 1.0,
        "value": 0.0,
        "continueNum": 1,
    }

    # 读取节点属性
    for k, v in elem.attrib.items():
        v_str = str(v).strip()
        if k in INT_FIELDS:
            if not v_str:
                data[k] = 0
            else:
                try:
                    data[k] = int(v_str)
                except ValueError:
                    data[k] = 0
        elif k in FLOAT_FIELDS:
            if not v_str:
                data[k] = 0.0
            else:
                try:
                    data[k] = float(v_str)
                except ValueError:
                    data[k] = 0.0
        elif k.endswith("B"):
            data[k] = v_str in ("1", "true", "True")
        elif k == "obj":
            data["obj"] = parse_obj_field(v_str)
        elif k in LIST_FIELDS:
            if v_str:
                parts = [p.strip() for p in v_str.split(",") if p.strip()]
                if k == "effectProArr":
                    num_parts = []
                    for p in parts:
                        try:
                            num_parts.append(float(p))
                        except ValueError:
                            num_parts.append(p)
                    data[k] = num_parts
                else:
                    data[k] = parts
            else:
                data[k] = []
        else:
            data[k] = v_str

    # 读取子标签
    growth_elem: Element | None = None
    for child in elem:
        tag = child.tag
        if tag == "growth":
            growth_elem = child
            continue

        text = (child.text or "").strip()
        if tag == "obj":
            data["obj"] = parse_obj_field(text)
        elif tag in FLOAT_FIELDS:
            if not text:
                data[tag] = 0.0
            else:
                try:
                    data[tag] = float(text)
                except ValueError:
                    data[tag] = 0.0
        elif tag in INT_FIELDS:
            if not text:
                data[tag] = 0
            else:
                try:
                    data[tag] = int(text)
                except ValueError:
                    data[tag] = 0
        elif tag.endswith("B"):
            data[tag] = text in ("1", "true", "True")
        elif tag in LIST_FIELDS:
            if text:
                parts = [p.strip() for p in text.split(",") if p.strip()]
                # 特殊处理 effectProArr 中的数值
                if tag == "effectProArr":
                    num_parts = []
                    for p in parts:
                        try:
                            num_parts.append(float(p))
                        except ValueError:
                            num_parts.append(p)
                    data[tag] = num_parts
                else:
                    data[tag] = parts
            else:
                data[tag] = []
        elif tag in ("addSkillEffectImg", "meEffectImg", "targetEffectImg", "pointEffectImg", "stateEffectImg"):
            url = child.attrib.get("url") or child.findtext("url") or text
            if url:
                data[tag] = url
        else:
            data[tag] = text

    # AS3 默认值补偿逻辑 (SkillDefine.as lines 234-254)
    name = str(data.get("name") or "")
    data["name"] = name
    data["baseLabel"] = name
    if data.get("firstCd", -1.0) == -1.0:
        data["firstCd"] = round((data.get("cd", 0.0) / 3.0) * 2.0, 2)
    if data.get("intervalT", 0.0) == 0.0:
        data["intervalT"] = data.get("duration", 0.0)
    if father_name in ("enemySuper", "noEnemySuper", "heroSkill"):
        data["showInLifeBarB"] = True

    # 描述文本格式化
    desc = data.get("description", "")
    if desc:
        data["formattedDescription"] = format_description(desc, data)
    else:
        data["formattedDescription"] = ""

    # 解析 growth 节点 (HeroSkillDefine.getGrowthArr)
    if growth_elem is not None:
        growth_skills = []
        for lvl_idx, g_skill in enumerate(growth_elem.findall("skill"), 1):
            g_data = dict(data)
            g_data["lv"] = lvl_idx
            g_data["name"] = f"{name}_{lvl_idx}"
            g_data["baseLabel"] = name

            # 覆盖 growth 中的子标签
            for g_child in g_skill:
                g_tag = g_child.tag
                g_text = (g_child.text or "").strip()
                if g_tag in FLOAT_FIELDS:
                    try:
                        g_data[g_tag] = float(g_text)
                    except ValueError:
                        g_data[g_tag] = g_text
                elif g_tag in INT_FIELDS:
                    try:
                        g_data[g_tag] = int(g_text)
                    except ValueError:
                        g_data[g_tag] = g_text
                elif g_tag.endswith("B"):
                    g_data[g_tag] = g_text in ("1", "true", "True")
                else:
                    g_data[g_tag] = g_text

            # 重新格式化成长技能描述
            g_desc = g_data.get("description", "")
            if g_desc:
                g_data["formattedDescription"] = format_description(g_desc, g_data)

            growth_skills.append(g_data)

        data["growthArr"] = growth_skills
        data["maxLevel"] = len(growth_skills)

    return data


def extract_skill_xml_names_from_as3(as3_file: Path) -> list[str]:
    """通过静态调用图分析 (Call Graph Analysis) 从 DefineGroup.as 中递归提取所有流向 skill 的 XML 文件。

    不仅能提取直调 `this.skill.inData_byXML(...)`，还能自动追踪所有复合分发函数（如
    `inArmsXml`, `inBodyXml`, `inVehicleXml`, `inDeviceXml`, `inCraftXml`, `inLevelXml`
    以及未来版本可能新增的复合包装函数）。
    """
    if not as3_file.is_file():
        return []
    try:
        text = as3_file.read_text(encoding="utf-8")

        # 1. 扫描所有方法体
        func_pattern = re.compile(
            r'function\s+([A-Za-z0-9_]+)\s*\([^)]*\)\s*:[^{]*\{([^}]+)\}',
            re.DOTALL,
        )
        funcs: dict[str, str] = {}
        for m in func_pattern.finditer(text):
            funcs[m.group(1)] = m.group(2)

        # 2. 递归构建直接或间接调用 this.skill.inData_byXML 的 helper 复合分发函数集合
        skill_helpers: set[str] = set()
        for fname, fbody in funcs.items():
            if "this.skill.inData_byXML" in fbody:
                skill_helpers.add(fname)

        # 迭代追踪多级复合嵌套（如 inCraftXml 内部调用了 inBodyXml，而 inBodyXml 内部调用了 skill）
        changed = True
        while changed:
            changed = False
            for fname, fbody in funcs.items():
                if fname in skill_helpers or fname == "init":
                    continue
                for helper in list(skill_helpers):
                    if f"this.{helper}(" in fbody:
                        skill_helpers.add(fname)
                        changed = True
                        break

        logger.info("分析 DefineGroup.as 发现以下复合分发函数流向 skill: %s", skill_helpers)

        # 3. 扫描 init() 方法体中所有向 this.skill.inData_byXML 或复合分发函数传入的 XML 参数
        init_match = re.search(r'function init\(\)[^{]*\{', text)
        init_body = text[init_match.end():] if init_match else text

        targets = ["skill.inData_byXML"] + list(skill_helpers)
        target_re = "|".join([re.escape(t) for t in targets])
        call_pattern = re.compile(
            rf'this\.(?:{target_re})\s*\(\s*out0(?:\.([A-Za-z0-9_]+)|\[\s*["\']([^"\']+)["\']\s*\])'
        )

        xml_names: list[str] = []
        for m in call_pattern.finditer(init_body):
            name = m.group(1) or m.group(2)
            if name and name not in xml_names:
                xml_names.append(name)

        logger.info("从 DefineGroup.as 调用图中提取到 %d 个候选 XML 文件", len(xml_names))
        return xml_names
    except Exception as e:
        logger.warning("解析 AS3 脚本调用图失败: %s", e)
        return []


def resolve_skill_xml_list(xml_dir: Path) -> list[str]:
    """计算当前版本需要加载的技能 XML 文件列表。

    策略：
    1. 优先使用 DefineGroup.as 的调用图静态分析，提取全部直调与复合调用的 XML；
    2. 若未找到 AS3，使用静态清单作为基准；
    3. 校验每个 XML 文件是否真实包含 <skill> 节点，排除仅用于怪物碰撞等无技能属性的文件。
    """
    candidates = [
        xml_dir.parent / "scripts" / "dataAll" / "_data" / "DefineGroup.as",
        xml_dir.parent.parent / "scripts" / "dataAll" / "_data" / "DefineGroup.as",
    ]
    raw_names: list[str] = []
    for as3_path in candidates:
        if as3_path.is_file():
            raw_names = extract_skill_xml_names_from_as3(as3_path)
            if raw_names:
                break

    if not raw_names:
        raw_names = list(SKILL_XML_NAMES)

    # 过滤与验证：仅保留实际存在且包含 <skill> 节点的 XML
    valid_names: list[str] = []
    for name in raw_names:
        p = xml_dir / f"{name}.xml"
        if not p.is_file():
            continue
        try:
            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                content_sample = f.read(4096)
                if "<skill" in content_sample:
                    valid_names.append(name)
                else:
                    f.seek(0)
                    if "<skill" in f.read():
                        valid_names.append(name)
        except Exception:
            continue

    return valid_names


def parse_skills_from_xmls(xml_dir: Path) -> dict[str, Any]:
    """按 AS3 加载顺序解析全部技能 XML。"""
    obj: dict[str, dict[str, Any]] = {}
    cn_obj: dict[str, str] = {}
    father_obj: dict[str, dict[str, dict[str, Any]]] = {}
    father_cn_name_obj: dict[str, str] = {}
    arms_skill_name_arr: list[str] = []
    pet_skill_name_arr: list[str] = []
    demon_skill_name_arr: list[str] = []

    xml_names = resolve_skill_xml_list(xml_dir)
    logger.info("本次解析将加载 %d 个技能 XML 文件", len(xml_names))

    for fname in xml_names:
        p = xml_dir / f"{fname}.xml"
        if not p.is_file():
            logger.warning("技能 XML 文件不存在: %s", p)
            continue

        try:
            root = load_xml(p)
        except Exception as e:
            logger.error("解析 XML 失败 %s: %s", p, e)
            continue

        for father in root.findall("father"):
            f_name = father.attrib.get("name", "")
            f_cn = father.attrib.get("cnName", "")
            if f_name:
                father_cn_name_obj[f_name] = f_cn
                if f_name not in father_obj:
                    father_obj[f_name] = {}

            for skill_elem in father.findall("skill"):
                s_data = parse_skill_node(skill_elem, f_name, f_cn)
                s_name = s_data.get("name")
                s_cn = s_data.get("cnName")
                if not s_name:
                    continue

                # 存入全局对象 obj
                obj[s_name] = s_data

                # 存入中文索引 cnObj (AS3 中首次出现的 cnName 优先生效)
                if s_cn and s_cn not in cn_obj:
                    cn_obj[s_cn] = s_name

                # 存入分类父对象 fatherObj
                if f_name:
                    father_obj[f_name][s_name] = s_data

                # 特殊分类收集
                if f_name == "demonSkill" and s_name not in demon_skill_name_arr:
                    demon_skill_name_arr.append(s_name)
                elif f_name == "armsSkill" and s_name not in arms_skill_name_arr:
                    if not s_data.get("noRandomListB", False):
                        arms_skill_name_arr.append(s_name)
                elif f_name == "petSkill" and s_name not in pet_skill_name_arr:
                    pet_skill_name_arr.append(s_name)

                # 将 heroSkill 等级展开实例并入 obj (对应 AS3 createAllHeroSkillDefine)
                if "growthArr" in s_data:
                    for g_skill in s_data["growthArr"]:
                        g_name = g_skill["name"]
                        obj[g_name] = g_skill
                        if f_name:
                            father_obj[f_name][g_name] = g_skill

    return {
        "obj": obj,
        "cnObj": cn_obj,
        "fatherObj": father_obj,
        "fatherCnNameObj": father_cn_name_obj,
        "demonSkillNameArr": demon_skill_name_arr,
        "armsSkillNameArr": arms_skill_name_arr,
        "petSkillNameArr": pet_skill_name_arr,
    }


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    """运行 skill 模块解析并将结果保存为 skill.json 与 skillClass.json。"""
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\json")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=== 开始解析 skill 统一技能模块 ===")
    logger.info("解析 XML 路径: %s", xml_dir)
    result = parse_skills_from_xmls(xml_dir)

    # 保存到主目录 output/<version>/json/skill.json
    skill_json_path = out_put_dir / "skill.json"
    with open(skill_json_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    logger.info("已生成技能库: %s (共 %d 个技能)", skill_json_path, len(result["obj"]))

    # 同时保存到子目录 output/<version>/json/skill/skill.json 方便分模块访问
    sub_skill_dir = out_put_dir / "skill"
    sub_skill_dir.mkdir(parents=True, exist_ok=True)
    sub_skill_path = sub_skill_dir / "skill.json"
    with open(sub_skill_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 同时生成兼容 armsSkillClass.json 的武器技能定义
    arms_class_path = out_put_dir / "armsSkillClass.json"
    if "armsSkill" in result["fatherObj"]:
        arms_result = {
            "name": "armsSkill",
            "cnName": "武器技能",
            "skill": list(result["fatherObj"]["armsSkill"].values()),
        }
        with open(arms_class_path, "w", encoding="utf-8") as f:
            json.dump({"armsSkill": arms_result}, f, ensure_ascii=False, indent=2)
        logger.info("已生成兼容武器技能定义: %s", arms_class_path)

    logger.info("=== skill 模块解析完成 ===")


if __name__ == "__main__":
    run()
