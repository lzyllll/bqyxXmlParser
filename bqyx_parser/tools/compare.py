"""递归对比两个数据结构，用 logger 输出差异。"""
from __future__ import annotations

import json
from collections import defaultdict
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
    - 元素为 dict 且都有唯一 name / lv / id / cnName 时，按该字段对齐后再递归对比
    - 其他列表按元素内容做集合差集

    建议转为 {'bulletName':{xxxxx}} 这样的形式来对比

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
            for line in _format_diffs(diffs):
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
            f"[类型变化] {path or '<root>'}: {type(old).__name__} -> {type(new).__name__} ({_brief(old)} -> {_brief(new)})"
        )
        return

    if isinstance(old, dict):
        old_keys = set(old)
        new_keys = set(new)
        for key in sorted(new_keys - old_keys, key=str):
            diffs.append(f"[新增] {_join(path, key)} = {_brief(new[key])}")
        for key in sorted(old_keys - new_keys, key=str):
            diffs.append(f"[删除] {_join(path, key)} = {_brief(old[key])}")
        for key in sorted(old_keys & new_keys, key=str):
            _compare(old[key], new[key], _join(path, key), diffs)
        return

    if isinstance(old, list):
        _compare_list(old, new, path, diffs)
        return

    if old != new:
        diffs.append(f"[值变化] {path or '<root>'}: {_brief(old)} -> {_brief(new)}")


def _compare_list(old: list[Any], new: list[Any], path: str, diffs: list[str]) -> None:
    index_field = _index_field(old, new)
    if index_field is not None:
        _compare(
            {item[index_field]: item for item in old},
            {item[index_field]: item for item in new},
            path,
            diffs,
        )
        return

    old_map = {_freeze(item): item for item in old}
    new_map = {_freeze(item): item for item in new}
    location = f"{path}[]" if path else "<root>"
    for key in sorted(new_map.keys() - old_map.keys(), key=str):
        diffs.append(f"[新增元素] {location} = {_brief(new_map[key])}")
    for key in sorted(old_map.keys() - new_map.keys(), key=str):
        diffs.append(f"[删除元素] {location} = {_brief(old_map[key])}")


def _index_field(old: list[Any], new: list[Any]) -> str | None:
    for field in ("name", "lv", "id", "cnName"):
        if _can_index_by(old, field) and _can_index_by(new, field):
            return field
    return None


def _can_index_by(items: list[Any], field: str) -> bool:
    if not all(isinstance(item, dict) and field in item for item in items):
        return False
    keys = [item[field] for item in items]
    return len(keys) == len(set(map(_freeze, keys)))


def _brief(value: Any, limit: int = 120) -> str:
    text = repr(value)
    if len(text) <= limit:
        return text
    if isinstance(value, dict):
        for key in ("name", "lv", "id", "cnName"):
            if key in value:
                return f"{{{key}={value[key]!r}, ... {len(value)} keys}}"
        return f"{{... {len(value)} keys}}"
    if isinstance(value, list):
        labels = []
        for item in value:
            if not isinstance(item, dict):
                labels = []
                break
            for key in ("name", "lv", "id", "cnName"):
                if key in item:
                    labels.append(str(item[key]))
                    break
            else:
                labels = []
                break
        if labels:
            shown = ", ".join(labels[:6])
            extra = f", ... +{len(labels) - 6}" if len(labels) > 6 else ""
            return f"[{shown}{extra}]"
        return f"[... {len(value)} items]"
    return text[:limit] + "..."


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


def _parse_diff(line: str) -> tuple[str, str, str, str, str]:
    kind = ""
    body = line
    if line.startswith("["):
        end = line.find("]")
        if end != -1:
            kind = line[1:end]
            body = line[end + 1 :].lstrip()
    if " = " in body:
        path, value = body.split(" = ", 1)
        sep = "="
    elif ": " in body:
        path, value = body.split(": ", 1)
        sep = ":"
    else:
        path, value, sep = body, "", ""
    field = path.rsplit(".", 1)[-1] if path else path
    return kind, path, field, value, sep


def _owner_path(path: str, field: str) -> str:
    suffix = f".{field}"
    if path.endswith(suffix):
        return path[: -len(suffix)]
    return ""


def _split_owner(owner: str) -> tuple[str, str]:
    if "." not in owner:
        return "", owner
    parent, _, name = owner.rpartition(".")
    return parent, name


def _format_diffs(diffs: list[str]) -> list[str]:
    parsed = [_parse_diff(line) for line in diffs]
    groups: dict[tuple[str, str], list[int]] = {}
    order: list[tuple[str, str]] = []
    for index, (kind, _path, field, _value, _sep) in enumerate(parsed):
        key = (kind, field)
        if key not in groups:
            groups[key] = []
            order.append(key)
        groups[key].append(index)

    lines: list[str] = []
    pending: list[int] = []

    def flush_pending() -> None:
        if not pending:
            return
        owner_groups: dict[tuple[str, str], list[int]] = {}
        owner_order: list[tuple[str, str]] = []
        for index in pending:
            kind, path, field, _value, _sep = parsed[index]
            owner = _owner_path(path, field)
            gkey = (kind, owner)
            if gkey not in owner_groups:
                owner_groups[gkey] = []
                owner_order.append(gkey)
            owner_groups[gkey].append(index)
        for gkey in owner_order:
            indexes = owner_groups[gkey]
            if len(indexes) < 3:
                lines.extend(diffs[index] for index in indexes)
                continue
            kind, owner = gkey
            location = owner or "<root>"
            lines.append(f"[{kind}] {location} ({len(indexes)})")
            for index in indexes:
                _kind, _path, field, value, sep = parsed[index]
                if sep == "=":
                    lines.append(f"  {field} = {value}")
                elif sep == ":":
                    lines.append(f"  {field}: {value}")
                else:
                    lines.append(f"  {field}")
        pending.clear()

    for key in order:
        indexes = groups[key]
        items = [parsed[index] for index in indexes]
        values = {item[3] for item in items}
        if len(indexes) < 3 or len(values) == len(items):
            pending.extend(indexes)
            continue
        flush_pending()
        lines.extend(_format_field_group(key, items))
    flush_pending()
    return lines


def _format_field_group(
    key: tuple[str, str],
    items: list[tuple[str, str, str, str, str]],
) -> list[str]:
    kind, field = key
    values = {item[3] for item in items}
    seps = {item[4] for item in items}
    same_value = len(values) == 1 and len(seps) == 1
    if same_value:
        sep = next(iter(seps))
        value = next(iter(values))
        if sep == "=":
            header = f"[{kind}] *.{field} = {value} ({len(items)})"
        elif sep == ":":
            header = f"[{kind}] *.{field}: {value} ({len(items)})"
        else:
            header = f"[{kind}] *.{field} ({len(items)})"
    else:
        header = f"[{kind}] *.{field} ({len(items)})"

    by_parent: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for kind_, path, field_, value, sep in items:
        owner = _owner_path(path, field_)
        parent, name = _split_owner(owner)
        by_parent[parent].append((name, value, sep))

    lines = [header]
    for parent in by_parent:
        leaves = by_parent[parent]
        parent_values = {value for _name, value, _sep in leaves}
        parent_seps = {sep for _name, _value, sep in leaves}
        names = ", ".join(name for name, _value, _sep in leaves)
        if same_value or (len(parent_values) == 1 and len(parent_seps) == 1):
            sep = next(iter(parent_seps))
            value = next(iter(parent_values))
            if same_value:
                detail = names
            elif sep == "=":
                detail = f"{names} = {value}"
            elif sep == ":":
                detail = f"{names}: {value}"
            else:
                detail = names
            lines.append(f"  {parent}: {detail}" if parent else f"  {detail}")
            continue
        parts = []
        for name, value, sep in leaves:
            if sep == "=":
                parts.append(f"{name} = {value}")
            elif sep == ":":
                parts.append(f"{name}: {value}")
            else:
                parts.append(name)
        joined = ", ".join(parts)
        lines.append(f"  {parent}: {joined}" if parent else f"  {joined}")
    return lines
