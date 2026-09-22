# 爆枪英雄 XML 解析器

https://github.com/lzyllll/bqyxXmlParser

从 4399 下载爆枪英雄 SWF，用 FFDec 反编译，再把 XML 解析成 JSON。

## 环境

Python 3.12+。需要本机可用的 `ffdec-cli`。

使用 pip：

```text
pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
pip install -r requirements.txt
python main.py
```

使用 uv：

```text
uv python pin 3.12
uv sync
uv run main.py
```

lxml 类型提示：

```text
uv pip install -U types-lxml
pip install -U types-lxml
```

`parser_config.ini` 里配置 FFDec 路径：

```ini
[DEFAULT]
ffdec = ffdec-cli.exe
```

## 目录

```text
bqyx_parser/
  app.py                 总流程：下载 -> 提取 -> 清理
  downloader/            下载器，拉取游戏 SWF
  extractor/             提取器
    ffdec.py             调用 FFDec 导出脚本/图片/二进制
    as3.py               从 AS3 提取加载器和版本常量
    swf_url.py           从 XML 提取 <swfUrl>
    equip.py             复制装备/时装图标
    asset_extractor.py   源码驱动的图片资源与系统图标全自动提取器
  parser/                解析器
    factory.py           元素工厂和属性工厂
    xml.py               读 XML、parse_element / parse_xml
    convert.py           文本和属性类型转换
    element/             元素解析器
    attrib/              属性解析器
    module/              业务模块
      achieve/           成就、勋章
      things/            道具、强化
      union/             军团
    suit.py              套装和装备
  tools/                 工具
    config.py            版本号和 FFDec 路径
    files.py             重命名、清理非法 XML
    jsonfile.py          保存 JSON
    compare.py           递归对比 JSON / 解析结果
    gift_str.py          解析 gift 字符串
script/                  命令行入口，调用 parser 里的业务解析
test/                    工厂、默认规则和对比工具测试
```

数据目录：

```text
swf_assets/              下载下来的 SWF
compiled/                FFDec 反编译结果
output/<version>/resource    解析后的 JSON
resources/icons/         预置通用UI图标、强化星级与品质底框
```

## 使用流程 (Click CLI)

本工具提供基于 `click` 的全功能命令行界面，涵盖 SWF 资源下载更新与 XML 多版本配置解析。

### 1. 查看帮助与模块列表

```bash
# 查看全局帮助
python main.py --help

# 查看所有可用 XML 解析模块
python main.py parse --list
```

### 2. SWF 资源流程 (`swf`)

```bash
# 下载主 SWF，反编译 XML/AS3，并补齐依赖资源 SWF
python main.py swf update

# 强制重新下载（忽略本地已下载版本记录）
python main.py swf update --force

# 从 equipGather 提取并反编译装备/时装图片与 SVG
python main.py swf equip

# 根据 AS3 源码全自动提取对应版本的全量图片、装备部件与 UI 图标 (详见 docs/ASSET_EXTRACTION_GUIDE.md)
python main.py swf assets -v v3680

# 一键完整执行 SWF 资源更新与装备图片提取
python main.py swf all
```

### 3. XML 配置解析 (`parse`)

```bash
# 一键全量解析当前最新版本的所有 17 个模块并生成 JSON
python main.py parse

# 指定版本全量解析
python main.py parse -v v3671

# 按单模块或多模块指定解析
python main.py parse -v v3671 -m worldMap
python main.py parse -v v3671 -m equip -m arms -m things

# 自定义 XML 输入与 JSON 输出目录
python main.py parse -v v3671 -x compiled/v3671/xml -o output/v3671/resource
```

## 解析体系全景

解析系统基于 `lxml`，核心采用**双工厂模式（元素工厂 + 属性工厂）**与**三通道责任链**架构，支持全局字段改名、强制列表、以及针对特定标签/属性/数据形态的精细化解析。

```
                    ┌─────────────────────────┐
                    │      load_xml(...)      │ 
                    │  (自动清洗/修补非法格式)  │
                    └────────────┬────────────┘
                                 │ Element 树
                                 ▼
                    ┌─────────────────────────┐
                    │  ElementParserFactory   │◄── rename_maps (全局改名)
                    │       (元素工厂)         │◄── force_list_for (全局列表)
                    └────────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
   【通道 1: 自定义】        【通道 2: 标签/后缀】       【通道 3: 形态兜底】
   register(parser, prio)  register_tag("obj", ...) NestedElementParser (嵌套)
                           register_suffix("B",...) AttributeElementParser (属性)
                                                    TextElementParser (纯文本)
                                                    TagAttribElementParser (文本+属性)
                                                    EmptyElementParser (空标签)
                                 │
                                 ▼ 遇到元素属性时
                    ┌─────────────────────────┐
                    │   AttribParserFactory   │
                    │       (属性工厂)         │
                    └────────────┬────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
   【通道 1: 自定义】        【通道 2: 属性名/后缀】     【通道 3: 默认转换】
   register(parser, prio)  register_name("name",..) ParserArrAttribParser (逗号列表)
                           register_suffix("B", ..) DefaultAttribParser (safe_eval)
                           register_suffix("Arr",.)
```

---

## 快速上手

### 1. 最简读取与解析

```python
from bqyx_parser.parser import create_factory, load_xml, parse_xml

# 方式一：一步从 XML 文件解析为 Python 字典/数据结构
result = parse_xml("output/v3671/xml/head.xml")

# 方式二：使用独立工厂灵活解析
factory = create_factory()
root = load_xml("output/v3671/xml/head.xml")
result = factory.parse(root)
```

---

## 核心配置：全局改名与强制列表

针对爆枪英雄 XML 中常见的命名不规范、以及“单个元素是对象，多个元素才是数组”导致的类型不一致问题，工厂提供了开箱即用的全局配置支持：

```python
from bqyx_parser.parser import create_factory

factory = create_factory(
    # 1. 全局字段重命名映射
    rename_maps={
        # 属性改名：解析属性时自动把原属性名替换为新键名
        "attrib": {
            "cnName": "nameCn",
            "desc": "description",
            "activeB": "active",
        },
        # 元素改名：解析子元素时自动把标签名改名为新键名
        "element": {
            "addObjJson": "addObj",
            "detailInfo": "detail",
        },
    },
    # 2. 全局强制列表集合
    # 即使该标签在当前父级下只有一个，也强制解析为 list 包装 [value]
    force_list_for={"gift", "skill", "dropLevel", "pro"},
)

# 支持通过链式调用动态追加配置：
factory.add_rename_maps(attrib={"unitB": "unitFlag"})
factory.add_force_list_for("medal", "items")  # 参数支持可变长参数、集合或列表
```

### 规则运行机制

| 配置项 | 作用阶段 | 详细行为 |
| :--- | :--- | :--- |
| `rename_maps["attrib"]` | `parse_attribs` | 遍历属性键值时，优先从映射表中取出新名称；未配置的保持原名。若调用方在 `parse_attribs(element, rename_keys={...})` 中传入局部改名，局部配置优先。 |
| `rename_maps["element"]` | `parse_children` / `NestedElementParser` | 子元素解析完成后，将字典的 key 映射为新名称。若调用方传入 `rename_tags={...}`，局部优先。 |
| `force_list_for` | `parse_children` / `NestedElementParser` | 遍历子元素分组时，若标签名在强制列表集合中（**原始标签名或重命名后的标签名均支持匹配**），则无论该子标签数量是 1 还是多个，始终输出为 `[item]` 数组。解析器也可通过 `parse_children(element, force_list_for={...})` 追加局部强制列表。 |

---

## 自定义解析器开发

### `ElementParser` 基类与内置方法

编写自定义业务解析器只需继承 `ElementParser`，实现 `parse(element)`。解析器注册到工厂时会自动绑定 `factory` 与 `attrib_registry`。

```python
from bqyx_parser.parser.element.base import ElementParser
from bqyx_parser.parser.xml import Element

class MyElementParser(ElementParser):
    def can_parse(self, element: Element) -> bool:
        """是否处理当前元素。默认返回 True。"""
        return element.tag == "myTag"

    def parse(self, element: Element) -> dict:
        # 1. 解析当前元素的属性（自动应用全局 rename_maps["attrib"]）
        result = self.parse_attribs(element)

        # 2. 解析所有子元素（自动应用全局 force_list_for 和 rename_maps["element"]）
        children = self.parse_children(
            element,
            force_list_for={"specialTag"},       # 可选：追加当前解析器特有的强制列表标签
            rename_tags={"oldName": "newName"},  # 可选：追加当前解析器特有的改名映射
        )
        result.update(children)
        return result
```

基类常用辅助方法一览：

- `self.parse_attribs(element, result=None, rename_keys=None)`：解析元素属性，自动根据属性工厂转换类型，支持局部改名。
- `self.parse_children(element, force_list_for=None, rename_tags=None)`：解析下属所有子元素，将同名标签收纳为列表，不同名标签收纳为单值（受 `force_list_for` 控制）。
- `self.parser_element(child)`：递归调用工厂解析某一个子元素节点，返回 Python 值。
- `self.group_children(element)`：将子元素按 tag 分组为 `dict[str, list[Element]]`。
- `self.text(element)`：获取经过 strip 清理的文本内容；若无文本则返回 `None`。
- `self.eval_text(element)`：获取文本并自动进行 `safe_eval`（如数字转 `int`/`float`，json 字符串转 `dict`）。
- `self.safe_eval(value)`：智能类型求值。

### 注册与调度通道

工厂通过注册方法扩展，执行时按优先级自上而下匹配首个满足 `can_parse` 的解析器：

```python
factory = create_factory()

# 1. 自定义通道（按优先级数值从大到小匹配，优先级高先执行）
factory.register(CustomRootParser(), priority=100)

# 2. 标签/后缀通道
factory.register_tag("gift", GiftParser())               # 针对特定标签
factory.register_suffix("Rect", EndWithRectParser())    # 针对以 Rect 结尾的标签

# 3. 兜底通道（通常框架已默认注册：纯文本、纯属性、嵌套、空节点）
factory.register_fallback(CustomFallbackParser(), priority=0)
```

---

## 属性解析器与类型转换

### 默认转换规则

- **布尔值 (`*B`)**：属性名或标签名以 `B` 结尾（如 `superB="1"`、`<activeB>true</activeB>`）自动解析为 Python `bool` (`True`/`False`)。
- **列表数组 (`*Arr`, `*ArrCn`)**：以 `Arr` 结尾的属性或纯文本标签（如 `dropLevelArr="76,84"`），自动按逗号分割，并将内部元素转为对应数字或字符串。
- **矩形坐标 (`*Rect`, `hurtRectArr`)**：如 `-12,-50,24,50` 自动映射为 `{"x": -12.0, "y": -50.0, "width": 24.0, "height": 50.0}`。
- **嵌入 JSON 结构 (`<obj>`, `addObjJson`)**：自动补全花括号并反序列化为 Python `dict`。
- **礼物奖励串 (`<gift>`)**：分号分隔字符串自动解析为结构化字典。

### 属性工厂扩展

```python
from bqyx_parser.parser.attrib.base import AttribParser

class HexColorParser(AttribParser):
    def parse(self, key: str, value: str, element=None):
        return int(value, 16)

factory = create_factory()
# 精确按属性名拦截
factory.attrib_registry.register_name("lightColor", HexColorParser())
# 按后缀拦截
factory.attrib_registry.register_suffix("Hex", HexColorParser())
```

---

## XML 读写与节点工具 (`bqyx_parser.parser.xml`)

模块 `bqyx_parser.parser.xml` 封装了基于 `lxml` 的底层读写、格式清洗、容错加载以及节点形态判断函数，是整个解析框架的基础。

### 1. XML 文件加载与批量读取

- **`load_xml(source, ...)`**：核心底层加载函数。
  - **支持来源**：文件路径（`str` 或 `Path`）或内存二进制流（`bytes`）。
  - **自动修复**：反编译产物中常出现不规范的 `<?xmlversion="1.0"?>`（缺少空格），内部会自动修复为 `<?xml version="1.0"?>`。
  - **核心参数**：
    - `remove_comments=True`：自动过滤 XML 注释。
    - `remove_blank_text=True`：移除无意义的缩进和空白文本。
    - `strip_cdata=True`：提取 CDATA 内容并替换为普通文本。
    - `recover=False`：遇到畸形/不闭合的 XML 时可设为 `True` 开启 lxml 容错恢复模式。
    - 内部默认开启 `huge_tree=True`，完美支持超大 XML 文件的解析。
- **`load_xml_files(paths, ...)`**：
  批量加载给定的路径集合，自动过滤出存在的 `.xml` 文件，并返回对应的根节点列表 `list[Element]`。

```python
from pathlib import Path
from bqyx_parser.parser import load_xml, load_xml_files

# 1. 普通加载单个文件
root = load_xml("compiled/v3671/xml/head.xml")

# 2. 遇到语法不严格或损坏的 XML 时开启容错
root = load_xml("damaged.xml", recover=True)

# 3. 从内存 bytes 加载
root = load_xml(b"<data><name>test</name></data>")

# 4. 批量加载目录下所有 XML
xml_paths = Path("compiled/v3671/xml").glob("*.xml")
roots = load_xml_files(xml_paths)
```

### 2. 便捷解析入口

- **`parse_xml(source, factory=None, **kwargs)`**：
  最常用的一步解析函数。结合了 `load_xml` 与工厂解析，直接返回解析后的 Python 数据（字典或列表）。若未传入 `factory`，则自动复用全局默认工厂。
- **`parse_element_by_factory(element, factory=None)`**：
  对已有 `Element` 节点使用指定工厂进行解析。未传入 `factory` 时同样自动复用全局默认工厂。

```python
from bqyx_parser.parser import create_factory, parse_xml, parse_element_by_factory, load_xml

# 1. 极简一步解析文件（使用默认工厂）
data = parse_xml("compiled/v3671/xml/head.xml")

# 2. 传入带自定义配置的工厂解析
custom_factory = create_factory(force_list_for={"gift"})
data = parse_xml("compiled/v3671/xml/head.xml", factory=custom_factory)

# 3. 对已有 Element 节点解析
root = load_xml("compiled/v3671/xml/head.xml")
data = parse_element_by_factory(root, custom_factory)
```

### 3. 节点形态判断与文本提取

在编写自定义解析器的 `can_parse(element)` 以及分支逻辑时，可直接使用内置的轻量工具函数：

| 函数 | 类型签名 | 说明 |
| :--- | :--- | :--- |
| `is_element(node)` | `(object) -> bool` | 排除注释（Comment）、处理指令（PI）等非标签节点，确认是真正的 XML 元素且 `tag` 为有效字符串。 |
| `has_children(element)` | `(Element) -> bool` | 判断当前元素是否包含子元素节点（`len(element) > 0`）。 |
| `has_attrib(element)` | `(Element) -> bool` | 判断当前元素是否包含任何属性（`bool(element.attrib)`）。 |
| `has_text(element)` | `(Element) -> bool` | 判断当前元素是否包含非空白文本（等价于 `element_text(element) is not None`）。 |
| `element_text(element)` | `(Element) -> str \| None` | 获取元素文本并自动去除首尾空白；若无文本或全空白则返回 `None`。 |
| `eval_text(element)` | `(Element) -> Any` | 获取非空白文本，并自动通过 `safe_eval` 转为对应 Python 类型（如 `"120"` -> `120`）。 |

```python
from bqyx_parser.parser.xml import has_children, has_attrib, has_text, element_text, eval_text

class SkillParser(ElementParser):
    def can_parse(self, element):
        # 必须是包含子节点、且带有 name 属性的 skill 标签
        return element.tag == "skill" and has_children(element) and has_attrib(element)

    def parse(self, element):
        # 提取文本
        desc = element_text(element.find("description"))
        # 自动求值（数字自动转 int/float）
        cd = eval_text(element.find("cd"))
        return {"desc": desc, "cd": cd}
```

---

## 辅助工具集 (`bqyx_parser.tools`)

### 1. 反编译文件重命名与清理 (`FileProcessor`)

位于 `bqyx_parser.tools.files.py`，负责处理 FFDec 反编译后的原始产物：

```python
from pathlib import Path
from bqyx_parser.tools.files import FileProcessor

processor = FileProcessor()

# 1. 把 *_XMLOut_xxxClass.bin 重命名为标准的 xxx.xml
processor.rename_xml_bin(Path("compiled/v3671/scripts"))

# 2. 修复 XML 中非法注释（如连字符冲突）及缺少空格的属性（如 <tag a="1"b="2">）
processor.clean_xml_files(Path("compiled/v3671/xml"))

# 3. 规范化武器/装备图片和矢量图名称（根据 symbolClass 映射还原）
processor.rename_images_and_svgs(Path("compiled/v3671"))
```

### 2. 字符串转换与拆分工具

- **`parse_gift_string` (`bqyx_parser.tools.gift_str`)**：
  将爆枪格式的奖励字符串（如 `things;demStone;25`）拆解为包含 `type`, `name`, `num`, `color`, `lv`, `tipB` 等规范字段的字典。
- **`clean_split_text` (`bqyx_parser.tools.split`)**：
  按指定分隔符（默认逗号）切割文本，并彻底剥离因反编译产生的换行符、制表符及前后空白，滤除空元素。
- **`parse_property` (`bqyx_parser.tools.property`)**：
  递归查找所有 `<pro>` 标签，提取属性并解析内部多行百分比数据为数值数组。

### 3. JSON 保存与自动排重 (`save_to_json`)

位于 `bqyx_parser.tools.jsonfile.py`：

```python
from pathlib import Path
from bqyx_parser.tools.jsonfile import save_to_json

# 将数据保存为 JSON。如果目标文件已存在，会自动安全递增编号（如 head_1.json）
saved_path = save_to_json(result, xml_path=Path("head.xml"), output_dir="output/resource")
```

### 4. 数据对比工具 (`compare_data` / `compare_json`)

位于 `bqyx_parser.tools.compare.py`，用于新解析的数据与旧版资源/存档 JSON 之间做精细化递归比对：

```python
from bqyx_parser.tools.compare import compare_data, compare_json

# 对比两个内存数据结构，自动按唯一标识（如 name / id / lv / cnName）对齐列表项
diffs = compare_data(old_dict, new_dict)

# 或直接对比两个 JSON 文件：
diffs = compare_json("resource/headData.json", "output/headData.json")
```

差异输出包含四大类：
- `[新增]` / `[新增元素]`
- `[删除]` / `[删除元素]`
- `[类型变化]`（如 `int` -> `str`）
- `[值变化]`（如 `100` -> `120`）

---

## 实战示例：开发一个完整模块解析脚本

以 `head` 模块（头像与属性）为例：

```python
import json
from pathlib import Path
from bqyx_parser.parser import ElementParser, create_factory, load_xml, parse_element_by_factory
from bqyx_parser.tools.compare import compare_data
from bqyx_parser.tools.logger import get_logger

logger = get_logger()

class HeadParser(ElementParser):
    def can_parse(self, element):
        return element.tag == "head"

    def parse(self, element):
        # 1. 提取自身属性
        result = self.parse_attribs(element)
        # 2. 提取子节点，强制 gift 保持为列表
        result.update(
            self.parse_children(
                element,
                force_list_for={"gift"},
                rename_tags={"addObjJson": "addObj"},
            )
        )
        return result

def create_head_factory():
    # 创建带全局规则的基础工厂
    factory = create_factory(
        rename_maps={"attrib": {"cnName": "nameCn"}},
        force_list_for={"gift"},
    )
    # 注册模块特定解析器
    factory.register_tag("head", HeadParser())
    return factory

if __name__ == "__main__":
    xml_path = Path("compiled/v3671/xml/head.xml")
    output_path = Path("output/v3671/resource/head/headData.json")
    resource_path = Path("resource/head/headData.json")

    # 1. 解析
    factory = create_head_factory()
    result = parse_element_by_factory(load_xml(xml_path), factory)

    # 2. 输出 JSON
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # 3. 对比验证
    if resource_path.is_file():
        with open(resource_path, "r", encoding="utf-8") as f:
            old_data = json.load(f)
        compare_data(old_data, result)
```

---

## 运行测试

```text
# 运行工厂与默认规则测试
python test/parser_factory_test.py

# 运行数据对比工具测试
python test/compare_test.py
```

