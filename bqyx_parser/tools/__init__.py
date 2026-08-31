"""工具：配置、文件处理、XML 分类、JSON 保存。"""

from bqyx_parser.tools.classify import classify_xml
from bqyx_parser.tools.compare import compare_data, compare_json
from bqyx_parser.tools.config import (
    load_FFDEC_path,
    load_last_main_swf,
    load_last_version,
    save_main_swf_info,
)
from bqyx_parser.tools.files import FileProcessor
from bqyx_parser.tools.jsonfile import save_to_json
from bqyx_parser.tools.logger import add_file_handler, get_logger

__all__ = [
    "FileProcessor",
    "add_file_handler",
    "classify_xml",
    "compare_data",
    "compare_json",
    "get_logger",
    "load_FFDEC_path",
    "load_last_main_swf",
    "load_last_version",
    "save_main_swf_info",
    "save_to_json",
]
