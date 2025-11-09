import xml.etree.ElementTree as ET
from typing import Any, Dict


from utils.parser.tag.abstract import ElementParser



class EmptyElementParser(ElementParser):
    """空元素解析器 - 最低优先级"""
    
    def can_parse(self, element: ET.Element) -> bool:
        return ((element.text is None or not element.text.strip()) and 
                len(element.attrib) == 0 and 
                len(element) == 0)
    
    def parse(self, element: ET.Element) -> Any:
        return None


class TextElementParser(ElementParser):
    """纯文本元素解析器 - 优先级 1"""
    
    def can_parse(self, element: ET.Element) -> bool:
        # 没有子元素且没有属性，只有文本内容
        return (len(element) == 0 and 
                element.text is not None and 
                len(element.attrib) == 0)
    
    def parse(self, element: ET.Element) -> Any:
        text = element.text.strip() if element.text else None
        if not text:
            return None
            
        # 尝试将文本内容转换为Python对象

        return self.safe_eval(text)
class AttributeElementParser(ElementParser):
    """属性元素解析器 - 优先级 1"""
    
    def can_parse(self, element: ET.Element) -> bool:
        #仅仅有属性 没有文本内容 没有子元素
        return len(element) == 0 and len(element.attrib) > 0 and element.text is None
    
    def parse(self, element: ET.Element) -> Dict[str, Any]:
        result = {}
        # 解析属性
        self.attrib_registr.parse(element, result)
        return result

class NestedElementParser(ElementParser):
    """嵌套元素解析器 - 优先级 2"""
    
    def can_parse(self, element: ET.Element) -> bool:
        # 有子元素 和 属性 没有文本内容
        has_text = element.text and element.text.strip()
        return len(element) > 0 and not has_text
    
    def parse(self, element: ET.Element) -> Dict[str, Any]:
        result = {}
        # 解析属性
        self.attrib_registr.parse(element, result)

        # 按标签分组处理子元素
        children_by_tag = self.tag_counter(element)
        # 处理每个标签组的元素
        for tag, elements in children_by_tag.items():
            if len(elements) == 1:
                # 单个元素，直接解析
                result[tag] = self.factory.parse_element(elements[0])
            else:
                # 多个相同标签的元素，解析为列表
                result[tag] = [self.factory.parse_element(elem) for elem in elements]
        return result


class TagAttribElementParser(ElementParser):
    """标签和属性元素解析器（有文本、属性、没有子元素）- 优先级 3"""
    
    def can_parse(self, element: ET.Element) -> bool:
        # 只有文本内容和属性 没有子元素
        has_text = element.text and element.text.strip()
        has_attrib = len(element.attrib) > 0
        has_children = len(element) > 0
        return has_text and has_attrib and not has_children
    
    def parse(self, element: ET.Element) -> Dict[str, Any]:
        result = {}
        # 解析文本内容
        if element.text and element.text.strip():
            text = element.text.strip()
            result['value'] = self.safe_eval(text)
        # 解析属性
        self.attrib_registr.parse(element, result)
        return result

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                








