from abc import ABC, abstractmethod
from typing import Any, Dict
import xml.etree.ElementTree as ET

class AttribParser(ABC):


    """属性解析器抽象基类"""
    
    def can_parse(self, element: ET.Element) -> bool:
        """
        判断是否能解析该元素的属性
        
        Args:
            element: XML元素
            
        Returns:
            如果能解析返回True，否则返回False
        """
        return True
    
    @abstractmethod
    def parse(self, element: ET.Element, result: Dict[str, Any]) -> None:
        """
        解析元素的属性并添加到result中
        
        Args:
            element: XML元素
            result: 结果字典，属性会被添加到此字典中
        """
        pass




