from abc import ABC, abstractmethod
from typing import Any
import xml.etree.ElementTree as ET

from utils.parser.attrib.default_parser import save_eval


class ElementParser(ABC):
    """元素解析器抽象基类"""
    
    def __init__(self, factory=None):
        self.factory = factory
    
    def set_factory(self, factory):
        """设置工厂引用，用于递归解析"""
        self.factory = factory
    
    def set_attrib_registr(self, registr):
        """设置属性解析工厂"""
        self.attrib_registr = registr
    def save_eval(self,value):
        return save_eval(value)

    def tag_counter(self, element: ET.Element) -> dict:
        '按标签分组处理子元素 分组计数 之后判断是否为单个元素还是多个元素'
        children_by_tag = {}
        for sub_child in element:
            if sub_child.tag not in children_by_tag:
                children_by_tag[sub_child.tag] = []
            children_by_tag[sub_child.tag].append(sub_child)
        return children_by_tag
    @abstractmethod
    def can_parse(self, element: ET.Element) -> bool:
        """判断是否能解析该元素"""
        pass
    
    @abstractmethod
    def parse(self, element: ET.Element) -> Any:
        """解析元素"""
        pass


