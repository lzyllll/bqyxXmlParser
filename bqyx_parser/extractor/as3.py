"""从反编译后的 AS3 中提取加载器和版本常量。"""
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class BqAS3Parser:
    """读取 Gaming.as 和 ConstantDefine.as。"""

    def extract_swf_loaders(self, project_path: Path) -> List[Tuple[str, str, str]]:
        """提取 swfLoaderManager.addSWFLoader 配置，返回 (路径, 名称, 类型)。"""
        file_path = project_path / "Gaming.as"
        if not file_path.exists():
            logger.error("文件不存在: %s", file_path)
            return []

        try:
            content = file_path.read_text(encoding="utf-8")
            pattern = r'swfLoaderManager\.addSWFLoader\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\);'
            matches = re.findall(pattern, content)
            logger.info("从 %s 中提取到 %s 个 SWF 加载器配置", file_path, len(matches))
            return matches
        except Exception as exc:
            logger.error("提取 SWF 加载器配置失败: %s", exc)
            return []

    def extract_specific_constants(self, project_path: Path) -> Dict[str, Optional[str]]:
        """提取 versionNumber、inVersion、xmlSwfUrl。"""
        empty = {"versionNumber": None, "inVersion": None, "xmlSwfUrl": None}
        file_path = project_path / "dataAll/_data/ConstantDefine.as"
        if not file_path.exists():
            logger.error("文件不存在: %s", file_path)
            return empty

        try:
            content = file_path.read_text(encoding="utf-8")
            result = {}
            for const_name in ("versionNumber", "inVersion", "xmlSwfUrl"):
                pattern = rf'public\s+static\s+const\s+{const_name}:String\s*=\s*"([^"]*)";'
                match = re.search(pattern, content)
                result[const_name] = match.group(1) if match else None
                if match is None:
                    logger.warning("未找到常量: %s", const_name)
            logger.info("从 %s 中提取到常量定义", file_path)
            return result
        except Exception as exc:
            logger.error("提取常量定义失败: %s", exc)
            return empty
