"""下载器模块，负责处理网络请求和文件下载。"""
import asyncio
import aiohttp
import aiofiles
import logging
import re
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


class SWFDownloader:
    """SWF文件下载器。"""
    
    def __init__(self,
                 output_dir: str | Path,
                 downLoad_base_url: str = "https://sbai.4399.com/4399swf/upload_swf/ftp15/linxy/20150324/gun/"):
        """
        初始化下载器。
        
        Args:
            downLoad_base_url: SWF文件基础URL
            output_dir: 下载文件的根目录
        """
        self.base_url = downLoad_base_url
        self.root_dir = Path(output_dir)
    
    def update_root_dir(self, new_root: Path) -> None:
        """更新根目录。"""
        self.root_dir = new_root
    
    async def get_main_swf(self) -> str:
        """
        从游戏网页获取主SWF文件名。
        
        Returns:
            str: 主SWF文件名，如 'v3541.swf'
            
        Raises:
            ValueError: 无法从网页中提取SWF文件名
        """
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.4399.com/flash/130396.htm') as response:
                html = await response.text(encoding='gb2312')
                
                # 使用正则表达式提取 v + 数字
                match = re.search(r"src='.*?/(v\d+)", html)
                if match:
                    extracted = match.group(1)  # 直接得到 v3541
                    return extracted + '.swf'
                else:
                    raise ValueError('错误，无法解析主SWF文件名')
    
    async def download(self, swf_path: str | Path) -> Path:
        """
        下载单个SWF文件。
        
        Args:
            swf_path: 相对路径
            
        Returns:
            Path: 下载后的本地文件路径
        """
        url = self.base_url + str(swf_path)
        local_path = self.root_dir / swf_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        async with aiofiles.open(local_path, 'wb') as f:
                            await f.write(content)
                        logger.info(f"✅ 成功下载: {swf_path}")
                    else:
                        logger.error(f"❌ 下载失败 ({resp.status}): {url}")
                return local_path
        except Exception as e:
            logger.error(f"💥 下载错误 {url}: {e}")
            raise
    
    async def download_multiple(self, swf_paths: List[str]) -> List[Path]:
        """
        批量下载多个SWF文件。
        tcp每次connection最多5个
        
        Args:
            swf_paths: SWF文件路径列表
            
        Returns:
            List[Path]: 下载后的本地文件路径列表
        """
        async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(limit=5),
        ) as session:
            tasks = []
            for rel_path in swf_paths:
                task = self._download_with_session(session, rel_path)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            # 处理异常结果
            successful_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"下载失败 {swf_paths[i]}: {result}")
                else:
                    successful_results.append(result)
            
            return successful_results
    
    async def _download_with_session(self, session: aiohttp.ClientSession, swf_path: str) -> Path:
        """
        使用给定的会话下载单个文件。
        
        Args:
            session: aiohttp会话
            swf_path: 相对路径
            
        Returns:
            Path: 下载后的本地文件路径
        """
        url = self.base_url + str(swf_path)
        local_path = self.root_dir / swf_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    content = await resp.read()
                    async with aiofiles.open(local_path, 'wb') as f:
                        await f.write(content)
                    logger.debug(f"已下载: {swf_path}")
                else:
                    logger.warning(f"下载失败 ({resp.status}): {url}")
                return local_path
        except Exception as e:
            logger.error(f"下载错误 {url}: {e}")
            raise