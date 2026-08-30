"""从反编译后的 XML 中提取 SWF 下载地址。"""
from __future__ import annotations

import logging
from pathlib import Path

from lxml import etree

from bqyx_parser.parser.xml import load_xml

logger = logging.getLogger(__name__)


def extract_swf_urls(xml_file_dir: Path) -> list[str]:
    """扫描目录里的 XML，收集全部 <swfUrl> 文本。"""
    result: list[str] = []
    if not xml_file_dir.exists():
        logger.error("XML 目录不存在: %s", xml_file_dir)
        return result

    for file in xml_file_dir.iterdir():
        if not file.is_file():
            continue
        try:
            root = load_xml(file)
            urls = [elem.text.strip() for elem in root.findall(".//swfUrl") if elem.text]
            result.extend(urls)
            logger.debug("从 %s 提取到 %s 个 SWF 地址", file, len(urls))
        except etree.ParseError as exc:
            logger.error("XML 解析失败 %s: %s", file, exc)
        except Exception as exc:
            logger.error("处理文件失败 %s: %s", file, exc)

    logger.info("共从 XML 中提取到 %s 个 SWF 地址", len(result))
    return result
