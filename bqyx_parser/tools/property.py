from __future__ import annotations

from pathlib import Path
from typing import Any

from bqyx_parser.parser.convert import safe_eval
from bqyx_parser.parser.xml import Element, load_xml


def parse_pro_node(pro_node: Element) -> dict[str, Any]:
    """解析单个 <pro> 节点。"""
    item: dict[str, Any] = {}
    for k, v in pro_node.attrib.items():
        if k in ("fixedNum", "maxLv"):
            try:
                item[k] = int(v)
            except ValueError:
                item[k] = 0
        elif k.endswith("B"):
            item[k] = v in ("1", "true", True, 1)
        elif k in ("name", "cnName", "unit", "gatherColor"):
            item[k] = str(v)
        elif "~" in str(v):
            parts = str(v).split("~")
            item[k] = [safe_eval(p) for p in parts]
        else:
            item[k] = safe_eval(v)

    raw_text = (pro_node.text or "").strip()
    if raw_text:
        data_arr = []
        for line in raw_text.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.endswith("%"):
                line = line[:-1]
                item["unit"] = "%"
            try:
                val = float(line)
                data_arr.append(int(val) if val.is_integer() else val)
            except ValueError:
                pass
        item["dataArr"] = data_arr

    return item


def parse_property(xml_path: str | Path) -> list[dict[str, Any]] | dict[str, list[dict[str, Any]]]:
    """
    读取 XML 文件，返回属性字典列表或按分组划分的字典。
    1. 若根节点下直接为 <pro>，返回 list[dict]；
    2. 若根节点下按分类分组（如 <base><pro/></base><bullet><pro/></bullet>），返回 dict[str, list[dict]]；
    3. 兜底返回所有递归查找到的 <pro> 列表。
    """
    root = load_xml(xml_path)

    direct_pros = [c for c in root if isinstance(c.tag, str) and c.tag == "pro"]
    if direct_pros:
        return [parse_pro_node(p) for p in direct_pros]

    containers: dict[str, list[dict[str, Any]]] = {}
    for child in root:
        if isinstance(child.tag, str):
            pros = [c for c in child if isinstance(c.tag, str) and c.tag == "pro"]
            if pros:
                containers[child.tag] = [parse_pro_node(p) for p in pros]
    if containers:
        return containers

    return [parse_pro_node(p) for p in root.findall(".//pro")]