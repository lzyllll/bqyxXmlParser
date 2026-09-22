# SWF 游戏资源与 UI 图标全自动提取指南

本文档介绍如何基于反编译 AS3 源码（`compiled/<version>/scripts/`）与游戏 SWF 资源包（`swf_assets/<version>/`），使用 `FFDecExporter` 与 `ffdec-cli` 全自动提取游戏运行及前端展示所需的所有矢量图标、套装装备部件、枪械兵器与 UI 系统底框资源。

---

## 1. 概述与核心变更

### 1.1 背景与设计目的
- **源码驱动**：以往手动或遍历导出 SWF 会产生海量无用的人体骨骼动画与冗余帧，耗时长且无法与引擎代码精确对应。本系统直接解析 `compiled/<version>/scripts/Gaming.as` 中的模块加载器（`SWFLoaderManager`），精准获取游戏运行必需的资源。
- **废弃旧 images 目录**：全量清理已废弃的 `output/<version>/images` 目录，统一按规范化架构输出至 `output/<version>/assets/`。
- **前端系统图标对齐**：针对项目前端/客户端使用的系统图标目录（如 `D:\bqyx\rs\assets\icons`），完整实现 100% 自动溯源与同名生成。

---

## 2. 核心模块与实现机制

### 2.1 `FFDecExporter` 模块 (`bqyx_parser/extractor/ffdec.py`)
封装对 `ffdec-cli` 的底层命令行调用，提供高灵活度的导出参数：
- **格式指定 (`formats`)**：支持 `formats="sprite:svg"` 实现矢量元件无损导出为 SVG，或 `formats="sprite:png"` 导出光栅序列帧。
- **指定导出对象 (`select_id`)**：通过 `-selectid <ID_LIST>` 仅导出目标 character ID，规避大型 SWF 内嵌的几千帧动作解析。
- **导出方法**：
  - `export_sprites(formats="sprite:svg", select_id=...)`
  - `export_binary_data(select_id=...)`
  - `export_symbol_class()`

### 2.2 `AssetExtractor` 提取器 (`bqyx_parser/extractor/asset_extractor.py`)
主业务编排引擎，分为以下四大部分：

#### ① 基础图标库提取 (`extract_icon_swfs`)
- 自动定位 `AchieveIcon`、`ThingsIcon`、`SkillIcon`、`NewIcon`、`PartsIcon`、`IconGather`、`BodyImg`、`FoodUI`、`equipIcon` 等 SWF。
- 以 `sprite:svg` 格式将各元件导出为矢量 SVG，按其 AS3 符号类名保存（例如 `IconGather/achieve.svg`, `ThingsIcon/arms.svg`）。

#### ② 装备套装性能优化提取 (`extract_equip_gather`)
- Flash 中的套装 SWF（如 `goshawkSuit.swf`, `aintSuit.swf`）包含全套人物行走、奔跑、开枪等数十帧复杂骨骼部件，整套全量导出耗时 70s+。
- **优化方案**：
  1. 先用 0.15s 导出 `symbolClass`；
  2. 通过正则匹配仅筛选部件图标（`head_icon`, `coat_icon`, `pants_icon`, `belt_icon`, `fashion_icon` 等）对应的 Character ID；
  3. 传递 `-selectid` 仅导出目标图标，并将无图标的纯特效包（如 `hundredGhostsHD`）自动跳过；
  4. 耗时降至 1.5s/套（提速 40+ 倍），输出格式为 `EquipGather/<suitName>/<suitName>_<part>.svg`。

#### ③ 武器与兵器库提取 (`extract_weapon_swfs`)
- 定位 `newGun`、`specialGun`、`weapon`。
- 提取武器全部 SVG 矢量图形与高清位图 PNG。

#### ④ 前端通用系统图标与品质底框 (`extract_ui_system_icons`)
对应 `D:\bqyx\rs\assets\icons` 与 `output/<version>/assets/icons`：
- **主功能导航 SVG**：
  - `achieve.svg` ← `IconGather/achieve.svg`（成就勋章）
  - `active.svg` ← `IconGather/dailySign.svg`（活动/每日签到）
  - `arms.svg` ← `ThingsIcon/arms.svg`（武器背包）
  - `ask.svg` ← `IconGather/ask.svg`（每日问答）
  - `blackMarket.svg` ← `IconGather/blackMarket.svg`（黑市神秘商人）
  - `head.svg` ← `IconGather/head.svg`（称号系统）
  - `pay.svg` ← `IconGather/pay.svg`（充值福利）
  - `thingsBag.svg` ← `IconGather/wear.svg`（角色装备/道具背包）
- **系统底框与静态素材固化 (`resources/icons/`)**：
  - 为避免各版本 SWF 内部 Character ID 偏移（如 822 变为 824），系统底层极少变动的 40 个通用图标与品质底框已固化在仓库 `resources/icons/` 下，解析时秒级直接复制。
  - 详细定位与维护说明请查阅：[BasicUI 图标维护指南](file:///d:/bqyx/python/bqXmlParser/docs/BASIC_UI_ICONS_GUIDE.md)。
  - `arms/lock.png`：锁定图标 (12×12)
  - `stars/str_5.png` ~ `stars/str_50.png`：强化星级 (46×10)
  - `back/equip_*.png`：装备品质底框 (10 种品质，56×56)
  - `back/arm_*.png`：武器品质底框 (10 种品质，173×69)
  - 颜色顺序（对应 1~10 帧）：`white`, `green`, `blue`, `purple`, `orange`, `red`, `black`, `darkgold`, `purgold`, `yagold`。

---

## 3. 产物目录结构与统计

以 `v3680` 版本为例，生成的完整资源目录位于 `output/v3680/assets/`：

```text
output/v3680/assets/
├── icons/                           # 前端/客户端通用系统图标库 (39 个文件)
│   ├── arms/
│   │   └── lock.png                 # 锁定图标 (12x12)
│   ├── back/                        # 装备/武器品质底框
│   │   ├── arm_white.png ~ yagold.png (10 种品质，173x69)
│   │   └── equip_white.png ~ yagold.png (10 种品质，56x56)
│   ├── stars/                       # 强化星级显示图 (46x10)
│   │   └── str_5.png ~ str_50.png   (10 档星级)
│   ├── achieve.svg
│   ├── active.svg
│   ├── arms.svg
│   ├── ask.svg
│   ├── blackMarket.svg
│   ├── head.svg
│   ├── pay.svg
│   └── thingsBag.svg
└── img/                             # 游戏核心资源库 (2,913 个文件)
    ├── AchieveIcon/                 # 成就、勋章图标 (343 个 SVG)
    ├── BodyImg/                     # 角色形象、立绘 (79 个 SVG)
    ├── EquipGather/                 # 119 套装备部件矢量图标 (468 个 SVG)
    │   ├── aintSuit/
    │   ├── goshawkSuit/
    │   └── ...
    ├── equipIcon/                   # 基础装备槽位图标 (13 个 SVG)
    ├── FoodUI/                      # 食物补给类矢量图标 (29 个 SVG)
    ├── IconGather/                  # 游戏通用图标 (328 个 SVG)
    ├── newGun/                      # 主流枪械与部件 (234 个 SVG/PNG)
    ├── NewIcon/                     # 新版道具/活动图标 (142 个 SVG)
    ├── PartsIcon/                   # 枪械配件与芯片图标 (58 个 SVG)
    ├── SkillIcon/                   # 技能图标 (300 个 SVG)
    ├── specialGun/                  # 特殊枪械与重火器 (478 个 SVG/PNG)
    ├── ThingsIcon/                  # 道具材料图标 (456 个 SVG)
    └── weapon/                      # 冷兵器、飞镖武器图标 (187 个 SVG/PNG)
```

---

## 4. 使用方式

### 4.1 CLI 命令行

```bash
# 提取默认最新版本 (v3680)
python main.py swf assets

# 指定版本号与路径
python main.py swf assets -v v3680 -o output/v3680/assets
```

参数说明：
- `-v, --version`: 游戏版本号（默认：`v3680` 或本地记录版本）。
- `-d, --swf-dir`: SWF 文件存放目录（默认：`swf_assets/<version>`）。
- `-c, --scripts-dir`: 反编译源码目录（默认：`compiled/<version>/scripts`）。
- `-o, --output`: 目标输出目录（默认：`output/<version>/assets`）。

### 4.2 独立脚本执行

```bash
# 运行全自动提取脚本
python script/export_version_assets.py --version v3680
```

### 4.3 Python API 调用

```python
from bqyx_parser.extractor.asset_extractor import AssetExtractor

# 初始化提取器
extractor = AssetExtractor(version="v3680")

# 执行完整导出 (包括自动同步到 D:/bqyx/rs/assets/icons)
result = extractor.run(sync_to_rs_icons=True)

# 或单独提取/同步前端系统图标库
extractor.extract_ui_system_icons()
```

