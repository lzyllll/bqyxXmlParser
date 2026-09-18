"""从 DefineGroup.as 的 init() 提取模块 -> xmlOut 文件映射。"""
from __future__ import annotations

import json
import logging
import re
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Mapping

logger = logging.getLogger(__name__)

OUT0_RE = re.compile(r'out0(?:\.([A-Za-z_]\w*)|\[\s*["\']([^"\']+)["\']\s*\])')
HELPER_RE = re.compile(r'this\.(?P<helper>in(?:Body|Arms|Vehicle|Device|Craft)Xml)\s*\(')
CALL_RE = re.compile(
    r'(?P<target>this\.[A-Za-z_]\w*(?:\.[A-Za-z_]\w+)*|[A-Z][A-Za-z0-9_]*)'
    r'\.(?P<method>in\w+|init)\s*\('
)
ARMS_OTHER_RE = re.compile(
    r'this\.inArmsXml\s*\(\s*out0(?:\.\w+|\[[^\]]+\])\s*,\s*true\s*\)'
)

# 分发函数会把同一份 XML 灌进多个模块
DISPATCH = {
    "inBodyXml": ["body", "bullet", "skill"],
    "inArmsXml": ["bullet", "skill"],
    "inVehicleXml": ["vehicle", "body", "bullet", "skill"],
    "inDeviceXml": ["device", "body", "bullet", "skill"],
    "inCraftXml": ["craft", "body", "bullet", "skill", "peakPro"],
}

MODULE_ORDER = [
    "body", "bullet", "skill", "vehicle", "device", "craft",
    "imageUrl", "dataList", "unend", "cityBody", "food", "normal",
    "scene", "armsCharger", "gene", "things", "partsProperty",
    "equip", "suitProperty", "dropItems", "dropColor", "worldMap",
    "union", "level", "say", "task", "goods", "top", "gift",
    "giftHome", "active", "vip", "blackMarket", "achieve", "ask",
    "post", "wilder", "count", "keyAction", "weapon", "jewelry",
    "shield", "head", "outfit", "love", "cheating", "peakPro",
    "editPro", "partner", "BCardPKCreator", "equipCreator",
]


def _extract_brace_block(text: str, start: int) -> str:
    i = text.find("{", start)
    if i < 0:
        raise ValueError("init() body not found")
    depth = 0
    for j, ch in enumerate(text[i:], i):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1:j]
    raise ValueError("unclosed init() body")


def _get_init_body(src: str) -> str:
    match = re.search(r"public function init\(\)\s*:\s*\*\s*\{", src)
    if not match:
        raise ValueError("public function init() not found")
    return _extract_brace_block(src, match.start())


def _split_statements(body: str) -> List[str]:
    stmts: List[str] = []
    buf: List[str] = []
    depth = 0
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == ";" and depth == 0:
            stmt = re.sub(r"\s+", " ", "".join(buf)).strip()
            if stmt:
                stmts.append(stmt)
            buf = []
            continue
        buf.append(ch)
    return stmts


def _out0_names(stmt: str) -> List[str]:
    names: List[str] = []
    for match in OUT0_RE.finditer(stmt):
        name = match.group(1) or match.group(2)
        if name and name not in names:
            names.append(name)
    return names


def _classify(stmt: str) -> List[str]:
    helper_match = HELPER_RE.search(stmt)
    if helper_match:
        return list(DISPATCH[helper_match.group("helper")])

    call_match = CALL_RE.search(stmt)
    if not call_match:
        return ["?"]

    target = call_match.group("target")
    if target.startswith("this."):
        return [target[5:].split(".")[0]]
    return [target]


def _ordered_modules(by_module: Mapping[str, Mapping[str, object]]) -> List[str]:
    seen = set()
    out: List[str] = []
    for name in MODULE_ORDER:
        if name in by_module:
            out.append(name)
            seen.add(name)
    for name in by_module:
        if name not in seen:
            out.append(name)
    return out


def extract_define_modules(source: str | Path) -> Dict[str, List[str]]:
    """解析 DefineGroup.as，返回 {module: [xmlOutName, ...]}。"""
    path = Path(source)
    text = path.read_text(encoding="utf-8")
    body = _get_init_body(text)

    by_module: OrderedDict[str, OrderedDict[str, None]] = OrderedDict()
    for stmt in _split_statements(body):
        names = _out0_names(stmt)
        if not names:
            continue
        for module in _classify(stmt):
            if module not in by_module:
                by_module[module] = OrderedDict()
            for name in names:
                by_module[module][name] = None

    result = OrderedDict()
    for module in _ordered_modules(by_module):
        result[module] = list(by_module[module].keys())

    logger.info(
        "从 %s 提取到 %d 个模块, %d 个 xmlOut 文件",
        path,
        len(result),
        len({name for files in result.values() for name in files}),
    )
    return dict(result)


def save_define_modules_json(data: Mapping[str, List[str]], output_path: str | Path) -> Path:
    """保存模块映射为 JSON 文件。"""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path
