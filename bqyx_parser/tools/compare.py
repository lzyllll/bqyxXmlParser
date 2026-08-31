"""递归对比两个数据结构，用 logger 输出差异。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bqyx_parser.tools.logger import get_logger


def compare_data(
    old: Any,
    new: Any,
    path: str = "",
    *,
    print_diff: bool = True,
) -> list[str]:
    """
    递归对比两个数据结构（dict/list/基本类型）。

    列表按集合对比，忽略顺序：
    - 元素为 dict 且都有唯一 name 时，按 name 对齐后再递归对比
    - 其他列表按元素内容做集合差集

    old : 原始数据（如从 achieveClass.json 读入）
    new : 新数据（如刚解析出的 achieve_result）
    path: 当前路径（用于定位差异位置）
    print_diff: 是否打印差异，默认 True
    """
    diffs: list[str] = []
    _compare(old, new, path, diffs)
    diffs.sort(key=_diff_order)
    if print_diff:
        logger = get_logger()
        if not diffs:
            logger.info("对比一致")
        else:
            logger.warning("共 %d 处差异", len(diffs))
            for line in diffs:
                logger.debug(line)
    return diffs


def compare_json(
    old_source: str | Path | Any,
    new_source: str | Path | Any,
    path: str = "",
    *,
    print_diff: bool = True,
) -> list[str]:
    """对比两份 JSON。参数可以是文件路径，或已经加载好的数据。"""
    return compare_data(
        _load_json(old_source),
        _load_json(new_source),
        path,
        print_diff=print_diff,
    )



_DIFF_ORDER = {
    "新增": 0,
    "新增元素": 0,
    "删除": 1,
    "删除元素": 1,
    "类型变化": 2,
    "值变化": 2,
}


def _diff_order(line: str) -> int:
    if line.startswith("["):
        end = line.find("]")
        if end != -1:
            return _DIFF_ORDER.get(line[1:end], 9)
    return 9


def _load_json(source: str | Path | Any) -> Any:
    if isinstance(source, Path):
        return json.loads(source.read_text(encoding="utf-8"))
    if isinstance(source, str):
        json_path = Path(source)
        if json_path.is_file():
            return json.loads(json_path.read_text(encoding="utf-8"))
        try:
            return json.loads(source)
        except json.JSONDecodeError:
            return source
    return source


def _compare(old: Any, new: Any, path: str, diffs: list[str]) -> None:
    if type(old) is not type(new):
        diffs.append(
            f"[类型变化] {path or '<root>'}: {type(old).__name__} -> {type(new).__name__} ({old!r} -> {new!r})"
        )
        return

    if isinstance(old, dict):
        old_keys = set(old)
        new_keys = set(new)
        for key in sorted(new_keys - old_keys, key=str):
            diffs.append(f"[新增] {_join(path, key)} = {new[key]!r}")
        for key in sorted(old_keys - new_keys, key=str):
            diffs.append(f"[删除] {_join(path, key)} = {old[key]!r}")
        for key in sorted(old_keys & new_keys, key=str):
            _compare(old[key], new[key], _join(path, key), diffs)
        return

    if isinstance(old, list):
        _compare_list(old, new, path, diffs)
        return

    if old != new:
        diffs.append(f"[值变化] {path or '<root>'}: {old!r} -> {new!r}")


def _compare_list(old: list[Any], new: list[Any], path: str, diffs: list[str]) -> None:
    if _can_index_by_name(old) and _can_index_by_name(new):
        _compare(
            {item["name"]: item for item in old},
            {item["name"]: item for item in new},
            path,
            diffs,
        )
        return

    old_map = {_freeze(item): item for item in old}
    new_map = {_freeze(item): item for item in new}
    location = f"{path}[]" if path else "<root>"
    for key in sorted(new_map.keys() - old_map.keys(), key=str):
        diffs.append(f"[新增元素] {location} = {new_map[key]!r}")
    for key in sorted(old_map.keys() - new_map.keys(), key=str):
        diffs.append(f"[删除元素] {location} = {old_map[key]!r}")


def _can_index_by_name(items: list[Any]) -> bool:
    if not all(isinstance(item, dict) and "name" in item for item in items):
        return False
    names = [item["name"] for item in items]
    return len(names) == len(set(map(_freeze, names)))


def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return ("dict", tuple(sorted((str(k), _freeze(v)) for k, v in value.items())))
    if isinstance(value, list):
        return ("list", frozenset(_freeze(item) for item in value))
    if isinstance(value, (set, frozenset)):
        return ("set", frozenset(_freeze(item) for item in value))
    return value


def _join(path: str, key: Any) -> str:
    return f"{path}.{key}" if path else str(key)
