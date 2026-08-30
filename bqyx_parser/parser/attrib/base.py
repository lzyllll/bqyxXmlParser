"""属性解析器基类。"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from bqyx_parser.parser.xml import Element


class AttribParser(ABC):
    """把单个属性转成 Python 值。注册到工厂时按属性名/后缀匹配。"""

    def can_parse(self, key: str, value: str, element: Element | None = None) -> bool:
        """是否由当前解析器处理。默认 True，精确名/后缀通道可省略。"""
        return True

    @abstractmethod
    def parse(self, key: str, value: str, element: Element | None = None) -> Any:
        """把单个属性转成 Python 值。"""
