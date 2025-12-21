"""AS3解析器模块，负责从AS3代码中提取信息。"""
import logging
import re
from pathlib import Path
from typing import List, Tuple, Dict, Optional

logger = logging.getLogger(__name__)


class BqAS3Parser:
    """爆枪AS3代码解析器，提供从AS3文件中提取信息的功能。"""
    
    def extract_swf_loaders(self, project_path: Path) -> List[Tuple[str, str, str]]:
        """
        从AS3文件中提取 swfLoaderManager.addSWFLoader 配置
        即Gameing.as

        Args:
            project_path: 游戏项目名称

        Returns:
            list: 包含 (swf_path, name, type) 元组的列表
        """
        file_path = project_path / 'Gaming.as'
        
        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            return []
        
        try:
            with file_path.open('r', encoding='utf-8') as file:
                content = file.read()

            # 正则表达式匹配 swfLoaderManager.addSWFLoader 调用
            pattern = r'swfLoaderManager\.addSWFLoader\(\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\);'

            matches = re.findall(pattern, content)
            logger.info(f"从 {file_path} 中提取到 {len(matches)} 个SWF加载器配置")
            return matches
        except Exception as e:
            logger.error(f"提取SWF加载器配置失败: {e}")
            return []
    
    def extract_specific_constants(self, project_path: Path) -> Dict[str, Optional[str]]:
        """
        从AS3文件中提取特定的常量定义

        dataAll/_data/ConstantDefine.as'

        Args:
            project_path: as3项目path

        Returns:
            dict: 包含 versionNumber, inVersion, xmlSwfUrl 的字典
        """
        file_path = project_path / 'dataAll/_data/ConstantDefine.as'
        
        if not file_path.exists():
            logger.error(f"文件不存在: {file_path}")
            return {
                'versionNumber': None,
                'inVersion': None,
                'xmlSwfUrl': None
            }
        
        try:
            with file_path.open('r', encoding='utf-8') as file:
                content = file.read()

            # 定义要查找的常量
            constants_to_find = ['versionNumber', 'inVersion', 'xmlSwfUrl']
            result = {}

            for const_name in constants_to_find:
                # 正则表达式匹配特定常量
                pattern = rf'public\s+static\s+const\s+{const_name}:String\s*=\s*"([^"]*)";'
                match = re.search(pattern, content)
                if match:
                    result[const_name] = match.group(1)
                else:
                    result[const_name] = None
                    logger.warning(f"未找到常量: {const_name}")
            
            logger.info(f"从 {file_path} 中提取到常量定义")
            return result
        except Exception as e:
            logger.error(f"提取常量定义失败: {e}")
            return {
                'versionNumber': None,
                'inVersion': None,
                'xmlSwfUrl': None
            }