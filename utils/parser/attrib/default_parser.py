from typing import Any, Dict
from utils.parser.attrib.abstract import AttribParser
import xml.etree.ElementTree as ET
import json

def save_eval(value):
    """
    解析字符串值：先尝试eval，失败则尝试json.loads
    """
    # 先尝试使用eval解析（支持Python表达式）
    # '1,2' => [1,2]
    # '1.3' => 1.3
    #  '{'a': 1, 'b': 2}' => {'a': 1, 'b': 2}
    try:
        result = eval(value)
        # 检查结果类型：只允许可json序列化的
        # 基础类型：int, float, bool, None
        # 允许的类型：dict, list, str, int, float, bool, None
        if result is None or isinstance(result, (dict, list, str, int, float, bool)):
            return result
        else:
            # 如果不是允许的类型（如对象、函数等），返回原值
            return value
    except Exception:
        # eval失败，尝试使用json.loads解析（更安全，只解析JSON格式）
        try:
            result = json.loads(value)
            # JSON解析成功，直接返回（JSON只支持基础类型和dict, list）
            return result
        except (json.JSONDecodeError, ValueError):
            # json.loads也失败，返回原值
            return value


def auto_convert(key, value):
    #特属性形式判断 如superB
    if key and key.endswith('B'):
        if value in ['true', '1']: 
            return True
        if value in ['false', '0']: 
            return False
    return save_eval(value)

class DefaultAttribParser(AttribParser):
    """默认属性解析器 - 默认行为为 result[key] = eval(value)"""
    def can_parse(self, element: ET.Element) -> bool:
        return len(element.attrib) > 0 
    
    def parse(self, element: ET.Element, result: Dict[str, Any]) -> None:
        """解析属性，默认行为：尝试eval，失败则使用原始值"""
        for key, value in element.attrib.items():
            result[key] = auto_convert(key, value)



