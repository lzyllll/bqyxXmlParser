from typing import Any, List, TYPE_CHECKING
import xml.etree.ElementTree as ET

from utils.parser.tag.abstract import ElementParser
from utils.parser.tag.default_parser import EmptyElementParser


class ElementParserFactory:
    """元素解析器工厂 - 支持优先级注册和递归解析"""
    
    def __init__(self, attrib_registr):
        self._parsers = []  # 存储 (priority, parser) 
        self.attrib_registr = attrib_registr
    
    def set_attrib_registr(self, attrib_registr):
        """设置属性解析工厂，并更新所有已注册解析器的引用"""
        self.attrib_registr = attrib_registr
        # 更新所有已注册解析器的 attrib_registr
        for _, parser in self._parsers:
            parser.set_attrib_registr(attrib_registr)

    def register_parser(self, parser: 'ElementParser', priority: int = 0):
        """
        注册解析器
        
        Args:
            parser: 解析器实例
            priority: 优先级，数值越大优先级越高
        """
        # 注册时直接设置factory和attrib_registr
        parser.set_factory(self)
        parser.set_attrib_registr(self.attrib_registr)
        self._parsers.append((priority, parser))
        # 按优先级降序排序
        self._parsers.sort(key=lambda x: x[0], reverse=True)

    
    def parse_element(self, child: ET.Element) -> Any:
        """解析元素（公开的解析方法）"""
        parser = self.get_parser(child)
        return parser.parse(child)
    
    def get_parser(self, child: ET.Element) -> 'ElementParser':
        """获取适合的解析器（按优先级顺序检查）"""
        for priority, parser in self._parsers:
            if parser.can_parse(child):
                return parser
        return EmptyElementParser()
    
    def unregister_parser(self, parser_class: type):
        """注销指定类型的解析器"""
        self._parsers = [(p, parser) for p, parser in self._parsers 
                        if not isinstance(parser, parser_class)]
    
    def get_registered_parsers(self) -> List[tuple]:
        """获取已注册的解析器列表（用于调试）"""
        return [(priority, type(parser).__name__) for priority, parser in self._parsers]

