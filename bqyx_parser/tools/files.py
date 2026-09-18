"""文件处理器模块，负责文件重命名和清理。"""
import logging
import re
from pathlib import Path
from typing import Optional
import shutil
logger = logging.getLogger(__name__)

def get_symbol_map(compiled_dir:Path):
    file_path = compiled_dir / Path('symbolClass') / 'symbols.csv'
    with open(file_path, 'r', encoding='utf-8') as f:
        result = [raw_str.strip().split(';') for raw_str in f.readlines()]

    return {k:v for k,v in result}

def rename_svg(compiled_dir:Path,symbol_map:dict):
    svgs = compiled_dir / 'shapes'
    for svg in svgs.iterdir():
        # 去除那些已生成的,非数字开头的
        if not str(svg.stem).isdigit():
            break
        # 生成索引，与svg 和 symbolclass 差1
        index = str(int(svg.stem)+1)
        if index in symbol_map:
            new_name = svg.with_stem(symbol_map[index])
            svg.rename(new_name)

def rename_image(compiled_dir:Path,symbol_map:dict):
    svgs = compiled_dir / 'images'
    for svg in svgs.iterdir():
        # 去除那些已生成的,非数字开头的
        if not str(svg.stem).isdigit():
            break
        # 生成索引，与svg 和 symbolclass 差2
        index = str(int(svg.stem)+2)
        if index in symbol_map:
            new_name = svg.with_stem(symbol_map[index])
            svg.rename(new_name)


class FileProcessor:
    """文件处理器，提供文件重命名、清理功能。"""

    def rename_images_and_svgs(self,directory):
        '''
        1.png=>weapon.png
        1.svg=>weapon.svg
        根据symbol_map重名明image
        image有合体的Image ,因此，改数字不会被命名 比如 人体的一堆部件
        '''
        symbol_map = get_symbol_map(directory)
        rename_image(directory,symbol_map)
        rename_svg(directory,symbol_map)

    def rename_bin_to_swf(self, directory: Path) -> None:
        """
        重命名目录中的所有.bin文件：去掉数字_前缀，.bin改为.swf
        1_xxxxx.bin => xxx.swf
        如果目标文件已存在，则覆盖
        
        Args:
            directory: 要处理的目录路径
        """
        logger.info(f"开始重命名 {directory} 中的.bin文件")
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                old_name = file_path.name
                # 使用正则重命名：去掉数字_前缀，.bin改为.swf
                new_name = re.sub(r'^\d+_(.*)\.bin$', r'\1.swf', old_name)
                if new_name != old_name:  # 只有当文件名确实改变时才重命名
                    new_path = file_path.parent / new_name
                    # 如果目标文件已存在，先删除
                    if new_path.exists():
                        new_path.unlink()
                    file_path.rename(new_path)
                    logger.debug(f"重命名: {old_name} -> {new_name}")
        
        logger.info("文件重命名完成")
    def rename_equip_swf(self, directory: Path):
        """
        重命名 SWF 文件：
        1. 移除 equipGather数字xxx_fla.MainTimeline_ 前缀
        2. 清理 Class_dataClass 后缀
        """
        # 前缀模式
        prefix_pattern = r'^equipGather\d+_fla\.MainTimeline_'
        
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() == '.swf':
                old_name = file_path.name
                
                # 移除前缀
                new_name = re.sub(prefix_pattern, '', old_name)
                
                # 处理后缀：将 Class_dataClass 删除
                if new_name.endswith('Class_dataClass.swf'):
                    new_name = new_name.replace('Class_dataClass.swf', '.swf')
                
                if new_name != old_name:
                    new_path = file_path.parent / new_name
                    if new_path.exists():
                        shutil.rmtree(new_path)
                    file_path.rename(new_path)
    def rename_equip_dir(self, directory: Path):
        for dir_path in directory.iterdir():
            if dir_path.name.endswith('.swf'):
                new_name = dir_path.name.removesuffix('.swf')
                new_path = dir_path.parent / new_name
                if new_path.exists():
                    shutil.rmtree(new_path)
                dir_path.rename(new_path)

    def rename_xml_bin(self, folder_path: Path) -> None:
        """
        处理整个文件夹中的 .bin 文件，将其转换为 .xml 文件
        
        Args:
            folder_path: 文件夹路径
        """
        if not folder_path.exists():
            logger.error(f"文件夹不存在: {folder_path}")
            return
        
        logger.info(f"开始重命名 {folder_path} 中的XML .bin文件")
        
        # 查找所有 .bin 文件
        bin_files = list(folder_path.glob("*.bin"))
        
        for bin_file in bin_files:
            new_name = self._convert_filename(bin_file)
            new_path = folder_path / new_name
            # 如果目标文件已存在，先删除
            if new_path.exists():
                new_path.unlink(new_path)
            bin_file.rename(new_path)
            logger.debug(f"重命名XML: {bin_file.name} -> {new_name}")
        
        logger.info("XML文件重命名完成")
   
    def _convert_filename(self, file_path: Path) -> str:
        """
        转换文件名格式，返回新的文件名（带.xml后缀）
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 新的文件名
        """
        filename = file_path.name

        # 移除数字前缀和 XMLOut 部分
        pattern = r'^\d+_XMLOut_'
        match = re.match(pattern, filename)
        if match:
            # 移除数字_XMLOut_部分
            remaining = filename[match.end():]
            # 获取不带数字前缀的部分
            clean_name = remaining.replace('Class.bin', '.xml')
        else:
            # 直接替换后缀
            clean_name = file_path.with_suffix('.xml').name


        return clean_name
    
    def clean_xml_files(self, folder_path: Path) -> None:
        """
        清理文件夹中的XML文件，修复XML注释和属性格式
        
        Args:
            folder_path: 文件夹路径
        """
        logger.info(f"开始清理 {folder_path} 中的XML文件")
        
        xml_files = folder_path.glob("*.xml")

        for xml_file in xml_files:
            try:
                with open(xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 修复XML格式
                cleaned_content = self._fix_xml(content)

                # 写回文件
                with open(xml_file, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                
                logger.debug(f"已清理: {xml_file.name}")
            except Exception as e:
                logger.error(f"清理文件错误 {xml_file}: {e}")
        
        logger.info("XML文件清理完成")

    def _fix_xml(self,text):
        """
        删除连续的连字符，确保XML注释中只有单个连字符，且 --> 前不能有 -
        <!-- --> 把连续的"-"删除，只保留左右的注释
        匹配 "value1"word= 的模式，在 " 和 word 之间添加空格
        <skill index="0"cnName="逐渐死亡">

        """

        def replace_dashes_in_comment(match):
            full_comment = match.group(0)
            comment_content = match.group(1)

            # 将2个或更多连续的连字符替换为单个连字符
            cleaned_content = re.sub(r'-{2,}', '-', comment_content)

            # 确保内容末尾不以连字符结尾（避免与 --> 冲突）
            if cleaned_content.endswith('-'):
                cleaned_content = cleaned_content.rstrip('-')

            return f"<!--{cleaned_content}-->"

        # 匹配 <!-- 任意内容 --> 的模式
        pattern = r'<!--(.*?)-->'
        result = re.sub(pattern, replace_dashes_in_comment, text, flags=re.DOTALL)

        """修复XML标签中缺少空格的属性，只处理双引号的情况"""
        # 匹配 "value1"word= 的模式，在 " 和 word 之间添加空格
        # <skill index="0"cnName="逐渐死亡">
        pattern = r'("[^"]*")(\w+=)'
        fixed_text = re.sub(pattern, r'\1 \2', result)

        return fixed_text
    
    def find_swf_by_prefix(self,prefix: str, dir: Path):
        """
        根据前缀在 equip 文件夹中查找 SWF 文件
        
        Args:
            prefix: 文件前缀，如 "equipGather"
            base_dir: 基础目录（包含 equip 文件夹的目录）
        """
        
        
        if not dir.exists():
            print(f"错误: equip 文件夹不存在 - {dir}")
            return []
        

        
        # 遍历 equip 文件夹
        for item in dir.iterdir():
            if item.is_file() and item.name.startswith(prefix) and item.suffix.lower() == '.swf':
                return item
        
        return None
 
'''
=================================
### 将所有equip图片svg复制，并重命名
=================================
'''
