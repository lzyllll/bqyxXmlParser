"""把 XML 文本/属性转成可写入 JSON 的 Python 值。"""
from __future__ import annotations

import json
from typing import Any


def safe_eval(value: Any) -> Any:
    """尽量把字符串转成数字、列表、字典；失败则原样返回。"""
    if value is None or isinstance(value, (dict, list, int, float, bool)):
        return value
    if not isinstance(value, str):
        return value

    try:
        result = eval(value)
    except Exception:
        pass
    else:
        # 只接受能直接 JSON 序列化的类型
        if result is None or isinstance(result, (dict, list, str, int, float, bool)):
            return result
        return value

    try:
        return json.loads(value)
    except (json.JSONDecodeError, ValueError, TypeError):
        return value


def parse_arr(value: Any) -> list[Any]:
    """按逗号拆成列表，丢掉空项，每一项走 safe_eval。"""
    if value is None:
        return []
    text = value if isinstance(value, str) else str(value)
    return [safe_eval(item) for item in text.split(",") if item != ""]


def parse_bool_flag(value: Any) -> bool:
    """true/1 为 True，其余为 False。"""
    return value in ("true", "1", True, 1)


def auto_convert(key: str | None, value: Any) -> Any:
    """属性名以 B / Arr 结尾时按后缀处理，name 保持字符串，其余走 safe_eval。"""
    if key and key.endswith("B"):
        return parse_bool_flag(value)
    if key and key.endswith("Arr"):
        return parse_arr(value)
    if key in ("name",):
        return str(value)

    return safe_eval(value)
