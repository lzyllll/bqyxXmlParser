"""递归对比两个数据结构，打印或收集差异。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def compare_data(
    old: Any,
    new: Any,
    path: str = "",
    *,
    print_diff: bool = True,
) -> list[str]:
    """
    递归对比两个数据结构（dict/list/基本类型）。

    old : 原始数据（如从 achieveClass.json 读入）
    new : 新数据（如刚解析出的 achieve_result）
    path: 当前路径（用于定位差异位置）
    print_diff: 是否打印差异，默认 True
    """
    diffs: list[str] = []
    _compare(old, new, path, diffs)
    if print_diff:
        for line in diffs:
            print(line)
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
        if len(old) != len(new):
            diffs.append(f"[长度变化] {path or '<root>'}: 长度 {len(old)} -> {len(new)}")
        for index in range(min(len(old), len(new))):
            _compare(old[index], new[index], f"{path}[{index}]", diffs)
        if len(new) > len(old):
            for index in range(len(old), len(new)):
                diffs.append(f"[新增元素] {path}[{index}] = {new[index]!r}")
        elif len(old) > len(new):
            for index in range(len(new), len(old)):
                diffs.append(f"[删除元素] {path}[{index}] = {old[index]!r}")
        return

    if old != new:
        diffs.append(f"[值变化] {path or '<root>'}: {old!r} -> {new!r}")


def _join(path: str, key: Any) -> str:
    return f"{path}.{key}" if path else str(key)
