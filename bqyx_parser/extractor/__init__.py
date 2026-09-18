"""提取器：从 SWF / AS3 / XML 中抽出资源。"""

from bqyx_parser.extractor.as3 import BqAS3Parser
from bqyx_parser.extractor.asset_extractor import AssetExtractor
from bqyx_parser.extractor.define_group import extract_define_modules, save_define_modules_json
from bqyx_parser.extractor.equip import (
    copy_equip_image,
    copy_equip_svg,
    copy_fashion_image,
    copy_fashion_svg,
)
from bqyx_parser.extractor.ffdec import FFDecExporter
from bqyx_parser.extractor.swf_url import extract_swf_urls

__all__ = [
    "AssetExtractor",
    "BqAS3Parser",
    "FFDecExporter",
    "copy_equip_image",
    "copy_equip_svg",
    "copy_fashion_image",
    "copy_fashion_svg",
    "extract_define_modules",
    "extract_swf_urls",
    "save_define_modules_json",
]
