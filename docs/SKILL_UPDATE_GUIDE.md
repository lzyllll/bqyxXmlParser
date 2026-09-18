# 技能模块解析与版本更新维护指南 (Skill Module & AI Maintenance Guide)

本文档是 `bqXmlParser` 技能模块（`skill`）的权威技术规范与操作指南，**专门为开发者与后续接入的 AI Agent 编写**，旨在指导如何在游戏版本迭代、技能 XML 增加、以及出现复杂复合分发函数时，正确地更新和维护技能库。

---

## 目录
- [1. 模块设计背景与 AS3 对照](#1-模块设计背景与-as3-对照)
- [2. 核心架构缺陷反思：为什么“简单正则”远远不够？](#2-核心架构缺陷反思为什么简单正则远远不够)
- [3. 复合函数 (Compound Functions) 调用链机制详解](#3-复合函数-compound-functions-调用链机制详解)
- [4. 面向 AI Agent 的自动化与更新执行协议 (SOP)](#4-面向-ai-agent-的自动化与更新执行协议-sop)
- [5. 数据结构规范 (`skill.json`)](#5-数据结构规范-skilljson)
- [6. 下游消费与未找到技能保底机制](#6-下游消费与未找到技能保底机制)

---

## 1. 模块设计背景与 AS3 对照

### 1.1 为什么需要独立的 Skill 模块？
在早期版本中，世界地图模块（`worldMap`）为了展示修罗词缀的中文名，侵入式地扫描了部分技能 XML 并将词缀字典内嵌到 `worldMap.json` 中。这种做法破坏了单一真实源 (SSOT)，导致 `worldMap.json` 臃肿且割裂了游戏原版设计。

在爆枪英雄原版 AS3 架构中：
- 地图与怪物只引用技能的**唯一英文 ID**（例如 `demBossSkillArr: ["pioneerDemon", "KingRabbitTreater"]`）；
- 全局所有技能统一在 `DefineGroup.as` 中载入 `SkillDefineGroup`；
- 界面需要展示提示时，通过 `SkillDescrip.getSkillArrGather(...)` 动态向技能池水合获取技能名称与描述。

---

## 2. 核心架构缺陷反思：为什么“简单正则”远远不够？

### 2.1 简单正则的致命盲区
如果仅仅使用简单的正则表达式去匹配形如：
```python
re.compile(r'this\.skill\.inData_byXML\(\s*out0\.(\w+)\s*\)')
```
在旧版本中只能提取出 54 个直接调用的 XML 文件。

**然而，在爆枪英雄的真实源码中，绝大部分敌人技能、怪物被动、载具技能、飞船技能、陷阱装置技能等，根本不是通过 `this.skill.inData_byXML` 直接载入的，而是通过一层或多层“复合函数 (Compound / Dispatch Functions)”间接载入的！**

如果只用简单正则匹配，**将遗漏超过 130 个技能 XML 文件**（例如 `HookWitch.xml`、`CrossBone.xml`、`_01_DieBat.xml` 等数十种精英与首领怪的专属修罗技能全部丢失），导致地图或副本中大量词缀变成无定义的裸英文 ID。

---

## 3. 复合函数 (Compound Functions) 调用链机制详解

在 `DefineGroup.as` 中，游戏开发者为了复用逻辑，编写了大量复合分发函数。一个 XML 文件被传入后，会被同一个函数分发给多个子系统：

### 3.1 典型的复合函数调用链
查看 `compiled/<version>/scripts/dataAll/_data/DefineGroup.as` 第 745–789 行：

```actionscript
// 1. 载具复合函数：同时分发给 vehicle, body, bullet, skill
private function inVehicleXml(xml0:XML) : void {
   this.vehicle.inData_byXML(xml0);
   this.body.inData_byXML(xml0);
   this.bullet.inData_byXML(xml0);
   this.skill.inData_byXML(xml0); // <--- 隐蔽流向 skill
}

// 2. 怪物/敌人复合函数：同时分发给 body, bullet, skill
private function inBodyXml(xml0:XML, bodyType0:String = "normal") : void {
   this.body.inData_byXML(xml0,bodyType0);
   this.bullet.inData_byXML(xml0);
   this.skill.inData_byXML(xml0); // <--- 隐蔽流向 skill
}

// 3. 飞船复合函数：多级嵌套调用！
private function inCraftXml(xml0:XML) : void {
   this.craft.inData_byXML(xml0,"father","craft");
   this.inBodyXml(xml0);          // <--- 嵌套调用了 inBodyXml，间接流向 skill！
   this.peakPro.inData_byXML(xml0,"father","pro");
}

// 4. 武器复合函数：
private function inArmsXml(xml0:XML, otherBulletB0:Boolean = false, armsEditB0:Boolean = false) : void {
   this.bullet.inArmsRangeData_byXML(xml0);
   this.skill.inData_byXML(xml0); // <--- 隐蔽流向 skill
}

// 5. 装置复合函数：
private function inDeviceXml(xml0:XML) : void {
   this.device.inData_byXML(xml0);
   this.body.inData_byXML(xml0);
   this.bullet.inData_byXML(xml0);
   this.skill.inData_byXML(xml0); // <--- 隐蔽流向 skill
}
```

### 3.2 复合分发函数的动态集合
已知在 `DefineGroup.as` 中会流向 `this.skill.inData_byXML` 的复合方法包括（但未来版本可能新增）：
- `inBodyXml`
- `inArmsXml` / `inNewArmsXml`
- `inVehicleXml`
- `inDeviceXml`
- `inCraftXml`（二级嵌套调用）
- `inNewBodyXmlAfterInArms`
- `inLevelXml`

---

## 4. 面向 AI Agent 的自动化与更新执行协议 (SOP)

当未来调用 AI 协助更新技能库时，**AI 必须严格执行以下调用图分析（Call Graph Traversal）协议**，禁止使用单一正则猜测：

### 4.1 AI 静态调用图分析执行逻辑

```
                          ┌──────────────────────────────────────┐
                          │ 打开 DefineGroup.as 反编译代码文件   │
                          └──────────────────┬───────────────────┘
                                             │
                                             ▼
                 【第一阶段：构建所有流向 skill 的 Helper 方法集合】
                 1. 提取所有函数签名与函数体: funcs[name] = body
                 2. 找出所有直接包含 "this.skill.inData_byXML" 的函数 -> 加入 skill_helpers
                 3. 递归寻找调用了 skill_helpers 的上一级函数 (如 inCraftXml 调用 inBodyXml)
                    循环直到 skill_helpers 集合大小收敛 (Fixed Point)
                                             │
                                             ▼
                 【第二阶段：遍历 init() 扫描入参 XML】
                 1. 定位 DefineGroup.as 的 public function init() 方法体
                 2. 匹配所有 this.skill.inData_byXML(out0.xxx)
                 3. 匹配所有 this.<helper>(out0.xxx) (helper ∈ skill_helpers)
                 4. 收集全部 out0.<xmlName> 与 out0["<xmlName>"]
                                             │
                                             ▼
                 【第三阶段：XML 存在性与有效性校验】
                 1. 检查 compiled/<version>/xml/<xmlName>.xml 是否存在
                 2. 检查该 XML 文件内是否真实含有 "<skill" 标签 (排除纯撞体无技能的 XML)
                 3. 产出最终有效技能 XML 列表 (180+ 个文件)
```

### 4.2 Python 解析器中的实现参考
[`bqyx_parser/parser/module/skill/skill.py`](file:///d:/bqyx/python/bqXmlParser/bqyx_parser/parser/module/skill/skill.py) 已内置上述全套调用图算法：

```python
def extract_skill_xml_names_from_as3(as3_file: Path) -> list[str]:
    text = as3_file.read_text(encoding="utf-8")

    # 1. 提取所有函数体
    func_pattern = re.compile(r'function\s+([A-Za-z0-9_]+)\s*\([^)]*\)\s*:[^{]*\{([^}]+)\}', re.DOTALL)
    funcs = {m.group(1): m.group(2) for m in func_pattern.finditer(text)}

    # 2. 递归寻找直接和间接调用 this.skill.inData_byXML 的复合函数
    skill_helpers = {fname for fname, fbody in funcs.items() if "this.skill.inData_byXML" in fbody}
    changed = True
    while changed:
        changed = False
        for fname, fbody in funcs.items():
            if fname in skill_helpers or fname == "init":
                continue
            if any(f"this.{h}(" in fbody for h in list(skill_helpers)):
                skill_helpers.add(fname)
                changed = True

    # 3. 扫描 init() 中所有调用 this.skill 或复合函数的参数
    init_match = re.search(r'function init\(\)[^{]*\{', text)
    init_body = text[init_match.end():] if init_match else text

    targets = ["skill.inData_byXML"] + list(skill_helpers)
    call_pattern = re.compile(rf'this\.(?:{"|".join(map(re.escape, targets))})\s*\(\s*out0(?:\.([A-Za-z0-9_]+)|\[\s*["\']([^"\']+)["\']\s*\])')

    xml_names = []
    for m in call_pattern.finditer(init_body):
        name = m.group(1) or m.group(2)
        if name and name not in xml_names:
            xml_names.append(name)

    return xml_names
```

### 4.3 AI 更新操作步骤 (Action Steps for AI)
未来版本的更新指令：
1. **拉取反编译脚本**：
   ```bash
   python main.py swf update
   ```
2. **运行技能模块解析**：
   ```bash
   python main.py parse -v <version> -m skill
   ```
   - 检查控制台日志，确认自动识别出的复合分发函数与有效技能 XML 数量（一般为 180~200 个）。
3. **验证测试集**：
   ```bash
   python -m pytest test/test_world_map.py -v
   ```
4. **全量解析生成**：
   ```bash
   python main.py parse -v <version> -m all
   ```

### 4.4 XML 加载规范：强制使用 `load_xml`
在编写或修改解析器时，**禁止直接使用 Python 原生标准库的 `xml.etree.ElementTree.parse()`**，必须统一使用项目框架提供的：
```python
from bqyx_parser.parser import Element, load_xml
```

**为什么必须使用 `load_xml`？（底层 lxml 兼容处理）**：
1. **反编译语法缺陷修补**：FFDec 反编译产物中经常出现 `<?xmlversion` 缺少空格的非法 XML 声明，原生 `ET.parse()` 会直接报语法错误抛出异常，而 `load_xml` 会通过 `_normalize_declaration` 自动修复；
2. **底层基于 `lxml` 高性能解析**：配置了 `huge_tree=True`，能够稳定处理上万行的庞大技能或关卡 XML，避免标准库内存限制；
3. **自动剥离注释与空白噪音**：默认启用了 `remove_comments=True` 与 `remove_blank_text=True`，避免 AS3 反编译带来的大量无用注释节点干扰解析遍历；
4. **统一契约**：入参支持 `Path`、`str` 或 `bytes`，返回标准的 `Element`。

---

## 5. 数据结构规范 (`skill.json`)

解析器将全部有效 XML 解析并聚合输出为单一 JSON 文件：`output/<version>/json/skill.json`。

### 字段说明
- `"obj"`: `{ [skill_name]: SkillDefine }`（当前包含 **3,120+** 个技能定义，展开英雄成长等级 `<growth>`）；
- `"cnObj"`: `{ [cn_name]: skill_name }`（中文名至技能英文 ID 的快速反向索引）；
- `"fatherObj"`: `{ [father_name]: { [skill_name]: SkillDefine } }`（按 XML 父分类归类）；
- `"fatherCnNameObj"`: `{ [father_name]: father_cn_name }`（父分类中文名，如 `demonSkill: 修罗技能`）；
- `"demonSkillNameArr"`: 修罗技能英文 ID 数组；
- `"armsSkillNameArr"`: 武器技能英文 ID 数组；
- `"petSkillNameArr"`: 宠物技能英文 ID 数组。

---

## 6. 下游消费与未找到技能保底机制

### 6.1 `bqyx_api` 中的水合服务
在 `bqyx_api` 中，由 [`SkillDefineService`](file:///d:/bqyx/python/bqyx_api/bqyx_api/archive/skill/service/skill_define_service.py) 加载 `skill.json`，并由 [`WorldMapDefine`](file:///d:/bqyx/python/bqyx_api/bqyx_api/archive/world_map/define/world_map_define.py) 进行动态水合：

```python
from bqyx_api.archive.skill import SkillDefineService
from bqyx_api.archive.world_map import WorldMapDefineService

skill_service = SkillDefineService("output/v3671/json")
map_service = WorldMapDefineService("output/v3671/json", skill_service=skill_service)

wotu = map_service.get_define("WoTu")
# 获取水合后的首领修罗词缀（含中文名与英文名）
boss_skills = wotu.demBossSkills
```

### 6.2 严格保底机制（英文原名保底）
无论未来游戏如何更新、新增何种未注册的特殊子弹或测试词缀，**系统绝不允许抛出异常中断运行**，必须执行以下保底策略：
1. **中文名未找到**：`skill_service.get_cn("unknown_name")` 必须直接返回其英文名 `"unknown_name"`；
2. **定义对象未找到**：`skill_service.get_define_or_fallback("unknown_name")` 必须合成生成 `SkillDefine(name="unknown_name", cnName="unknown_name")`；
3. **提示格式化**：`skill_service.get_skill_arr_gather(["unknown_name"])` 必须保底展示 `"unknown_name: unknown_name"`。

遵循本规范，整个技能系统可确保在任何游戏版本演变下，兼具**原版 AS3 调用链真实性**与**极高的系统稳健度**。
