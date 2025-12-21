"""XML解析器模块，负责从XML文件中提取信息。"""
import logging
from lxml import etree
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)


class XMLParser:
    """XML文件解析器，提供从XML文件中提取信息的功能。"""
    
    def extract_swf_urls(self, xml_file_dir: Path) -> List[str]:
        """
        从local版本号.swf中的所有xml提取所有swf下载地址

        Args:
            xml_file_dir: XML文件目录

        Returns:
            List[str]: SWF URL列表
        """
        result = []
        
        if not xml_file_dir.exists():
            logger.error(f"XML文件目录不存在: {xml_file_dir}")
            return result
        
        for file in xml_file_dir.iterdir():
            if not file.is_file():
                continue
            
            try:
                tree = etree.parse(file)
                root = tree.getroot()
                swf_elements = root.findall('.//swfUrl')
                urls = [elem.text.strip() for elem in swf_elements if elem.text]
                result.extend(urls)
                logger.debug(f"从 {file} 中提取到 {len(urls)} 个SWF URL")
            except etree.ParseError as e:
                logger.error(f"XML解析错误 {file}: {e}")
            except Exception as e:
                logger.error(f"处理文件错误 {file}: {e}")
        
        logger.info(f"总共从XML文件中提取到 {len(result)} 个SWF URL")
        return result