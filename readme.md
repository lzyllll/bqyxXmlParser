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
    classify.py          按 father 分类 XML
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
output/<version>/xml     分类后的 XML
output/<version>/json    解析后的 JSON
```

## 使用流程

1. 运行 `python main.py`，下载主 SWF，反编译 XML/AS3，再补齐依赖资源。
2. 需要装备图时，按提示输入 `1`，会从 equipGather 提取并分类图标。
3. 用 `tools.classify.classify_xml` 把 XML 按 father 拆到 `output/<version>/xml`。
4. 跑脚本生成 JSON：

```text
python script/skill_element.py
python script/bullet_element.py
python script/suit.py
python script/question.py
```

也可以 `uv run script/skill_element.py`。

## 解析框架

基于 lxml。`create_factory()` 每次返回一个新工厂，按三条通道选解析器：

1. `register()`：自定义解析器，按优先级匹配 `can_parse`
2. `register_tag()` / `register_suffix()`：精确标签或后缀，例如 `obj`、`*B`、`*Arr`
3. 形态兜底：纯文本、纯属性、文本+属性、嵌套子元素、空元素

属性工厂 `create_attrib_registry()` 同样三条通道，按单个属性选解析器：

1. `register()`：自定义解析器，按优先级匹配 `can_parse(key, value, element)`
2. `register_name()` / `register_suffix()`：精确属性名或后缀，例如 `name`、`*B`、`*Arr`
3. 兜底：`safe_eval`

```python
factory = create_factory()
factory.attrib_registry.register_suffix("Url", UrlAttribParser())
factory.attrib_registry.register_name("lightColor", HexAttribParser())
```

```python
from bqyx_parser.parser import create_factory, load_xml, parse_element, parse_xml

root = load_xml("output/v3611/xml/father/skill/name/heroSkill.xml")
data = parse_element(root)          # 默认工厂
data = parse_xml(path, factory)     # 读文件并解析
```

`load_xml` 默认去掉注释和空白文本，并兼容 `<?xmlversion` 这种声明。

## 自定义解析器

继承 `ElementParser`，实现 `parse`。`can_parse` 默认返回 True。基类还提供：

- `parse_attribs(element)` 解析属性
- `parse_children(element)` 子元素按 tag 分组，单个为值，多个为列表
- `parse_named_map(element, key)` 把带 name 的子元素收成字典
- `parse_child_list(element)` 把子元素收成列表
- `text(element)` / `eval_text(element)` / `safe_eval(value)`

```python
from bqyx_parser.parser import ElementParser, create_factory, load_xml, parse_element

class TargetParser(ElementParser):
    def parse(self, element):
        return (self.text(element) or "").split(",")

class SkillFatherParser(ElementParser):
    def can_parse(self, element):
        return element.tag in {"data", "father"} and element.find("skill") is not None

    def parse(self, element):
        return self.parse_named_map(element, "skills", child_tag="skill")

factory = create_factory()
factory.register_tag("target", TargetParser())
factory.register(SkillFatherParser(), 100)

root = load_xml(xml_path)
result = parse_element(root, factory)
```

- `register(parser, priority)` 走自定义通道，适合按结构判断
- `register_tag(tag, parser)` 精确匹配标签
- `register_suffix(suffix, parser)` 匹配标签后缀

业务解析器在 `bqyx_parser/parser/module/`。

## 默认规则

- `<obj>"pro":0.35</obj>` -> `{"pro": 0.35}`
- `<superB>1</superB>` -> `True`
- `<effectInfoArr>a,b</effectInfoArr>` -> `["a", "b"]`
- `<dropLevelArr>76,84</dropLevelArr>` -> `[76, 84]`
- `<cnName>鬼目枪</cnName>` -> `"鬼目枪"`
- `<lineD size="2"/>` -> `{"size": 2}`
- 有子元素时，属性 + 子元素组成字典；同名子元素变成列表

属性名以 `B` 结尾时，`true/1` 转成 `True`，其它转成 `False`。
标签或属性名以 `Arr` 结尾时，按逗号拆成列表，每一项再走 `safe_eval`：数字变成数字，普通文本保持字符串。

## 分类后的 XML

先按有没有 `father` 分成 father / other，再按 father 的子标签拆分：

- `father/skill`
- `father/body`

然后再按 father 的 `name`、`type` 分：

- `father/skill/name`
- `father/skill/type`

## 对比工具

解析结果可以和旧 JSON 递归对比：

```python
from bqyx_parser.tools import compare_data, compare_json

compare_data(old, new)
compare_json("achieveClass.json", achieve_result)
```

## 测试

```text
python test/parser_factory_test.py
python test/compare_test.py
```
