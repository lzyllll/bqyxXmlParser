# XML 解析器框架 - 自定义类注册说明

https://github.com/lzyllll/bqyxXmlParser

## 概述

本框架提供了一个灵活的 XML 解析系统，支持通过注册自定义解析器来处理特定结构的 XML 元素。以下以 `SkillFatherParser` 为例说明如何创建和使用自定义解析器。

## 核心组件

### ElementParser 基类
所有自定义解析器都需要继承此基类，并实现以下两个方法：

### 1. can_parse(element)
**功能**: 判断解析器是否能处理当前 XML 元素
**参数**: 
- `element`: ET.Element - XML 元素对象
**返回**: bool - 是否能解析该元素

```python
def can_parse(self, element: ET.Element) -> bool:
    # 检查元素标签和特定子元素
    if element.tag == 'father':
        if element.find('skill') is not None:
            return True
    return False
```

### 2. parse(element)
**功能**: 解析 XML 元素并返回字典结果
**参数**: 
- `element`: ET.Element - XML 元素对象
**返回**: Dict[str, Any] - 解析结果

## 自定义解析器示例：SkillFatherParser

### 解析逻辑

```python
class SkillFatherParser(ElementParser):
    #使用状态判断
    def can_parse(self, element: ET.Element) -> bool:
        '''检查是否为包含skill子元素的father元素'''
        if element.tag == 'father':
            if element.find('skill') is not None:
                return True
        return False
    # 解析element
    # text,attrib,childs 的解析需要自己实现
    # 可使用self.factry self.attrib_registr来递归使用
    def parse(self, element: ET.Element) -> Dict[str, Any]:
        result = {} 
        
        # 1. 处理元素文本内容（如果有）
        # result[element.tag] = self.safe_eval(element.text)
        
        # 2. 解析元素属性 ,也可自己实现,
        # 此函数，为将解析后的结果，放到result中
        self.attrib_registr.parse(element, result)
        
        # 3. 按标签分组处理子元素
        result['skills'] = {}
        for bullet in element:
            # 递归解析子元素
            bullet_dict = self.factory.parse_element(bullet)
            
            # 使用name作为主键
            name = bullet_dict.get('name')

            result['skills'][name] = bullet_dict
            
        return result
```

### 关键特性

1. **属性解析**: 使用 `attrib_registr` 自动解析元素属性
2. **递归解析**: 使用 `factory.parse_element()` 递归处理子元素
3. **结构化数据**: 将子元素按名称分组存储
4. **eval**: 提供 `safe_eval()` 方法安全处理文本内容，可转换dict,list等基本数据类型

## 注册和使用

### 注册解析器

```python
# 创建工厂实例
factory = get_default_factory()

# 注册自定义解析器（数字表示优先级）
factory.register_parser(SkillFatherParser(), 100)
factory.register_parser(GrowthObjParser(), 110)
```

### 解析 XML

```python
# 直接解析XML文件
root = direct_parse_xml(xml_path)

# 使用注册的解析器处理元素
ele_dict = parse_element(root, element_factory=factory)
```

# 分类后的xml

先根据father，和other分出去
然后根据father的所有child，拆分  如一堆skill和一堆body元素
father/skill
father/body
然后再根据father的name,type分
father/skill/name
father/skill/type