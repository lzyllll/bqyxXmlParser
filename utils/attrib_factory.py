import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Callable, Optional

from utils.parser.attrib.abstract import AttribParser
from utils.parser.attrib.default_parser import DefaultAttribParser




class AttribParserRegistry:
    """属性解析器注册表 - 支持根据条件选择不同的属性解析策略"""
    
    def __init__(self, default_parser: Optional[AttribParser] = None):
        """
        初始化属性解析器注册表
        
        Args:
            default_parser: 默认的属性解析器，如果为None则使用DefaultAttribParser
        """
        self._parsers = []  # 存储 (priority, condition, parser)
        self._default_parser = default_parser or DefaultAttribParser()
    
    def register_parser(self, parser: AttribParser, condition: Optional[Callable[[ET.Element], bool]] = None, priority: int = 0):
        """
        注册属性解析器
        
        Args:
            parser: 属性解析器实例
            condition: 可选的条件函数，接受ET.Element返回bool，如果为None则作为默认解析器
            priority: 优先级，数值越大优先级越高
        """
        self._parsers.append((priority, condition, parser))
        # 按优先级降序排序
        self._parsers.sort(key=lambda x: x[0], reverse=True)
    
    def get_parser(self, child: ET.Element) -> AttribParser:
        """
        根据元素获取合适的属性解析器
        
        Args:
            child: XML元素
            
        Returns:
            合适的属性解析器
        """
        for priority, condition, parser in self._parsers:
            # 检查外部条件函数和解析器自身的can_parse方法
            if (condition is None or condition(child)) and parser.can_parse(child):
                return parser
        # 如果注册的解析器都不匹配，检查默认解析器
        if self._default_parser.can_parse(child):
            return self._default_parser
        # 如果默认解析器也不能解析，返回默认解析器（至少尝试解析）
        return self._default_parser
    
    def parse(self, child: ET.Element, result: Dict[str, Any]) -> None:
        """
        解析元素的属性并添加到result中（使用注册的解析器）
        
        Args:
            child: XML元素
            result: 结果字典，属性会被添加到此字典中
        """
        parser = self.get_parser(child)
        parser.parse(child, result)

    def unregister_parser(self, parser_class: type):
        """注销指定类型的属性解析器"""
        self._parsers = [(p, c, parser) for p, c, parser in self._parsers 
                          if not isinstance(parser, parser_class)]
    
    def get_registered_parsers(self) -> List[tuple]:
        """获取已注册的属性解析器列表（用于调试）"""
        return [(priority, condition.__name__ if condition else 'default', type(parser).__name__) 
                for priority, condition, parser in self._parsers]




