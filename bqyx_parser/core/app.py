"""应用程序核心类，协调各模块工作。"""
import logging
from pathlib import Path
import shutil
from typing import Optional

from bqyx_parser.decompile.ffdec import FFDecExporter
from bqyx_parser.downloader.downloader import SWFDownloader
from bqyx_parser.file_handler import classify
from bqyx_parser.file_handler.file_processor import FileProcessor, copy_equip_image, copy_equip_svg, copy_fashion_image, copy_fashion_svg
from bqyx_parser.parser.as3_parser import BqAS3Parser
from bqyx_parser.parser.xml_parser import XMLParser
from bqyx_parser.config.persistent_state import load_last_version, save_main_swf_info, load_last_main_swf

logger = logging.getLogger(__name__)

# 封装了aiohttp的下载文件，异步加速下载
# SWFDownloader(base_url, swf_dir)

# 文件处理器，提供文件重命名和清理功能 xml删除非法的注释和不合法的标签 比如 <name a='b'c='a'></name>
# a='b' c='a' 这样的形式要添加空格，不然解析xml报错
# FileProcessor().clean_xml_files(Path(r'C:\Users\lzy\Desktop\bqXmlParser\compiled\v3541\xml'))

# 正则提取反编译 爆枪英雄的as3文件，比如swfLoader要加载的swf资源 和 版本号 local版本号.swf
# gaming.as 和 consts.as
# BqAS3Parser()

# 提取xml文件夹中的 所有swfUrl
# XMLParser()

class BQYXParserApp:
    """BQYX 解析器应用程序主类。"""
    
    def __init__(self,
                 ffdec_path: str,
                 download_url: str = "https://sbai.4399.com/4399swf/upload_swf/ftp15/linxy/20150324/gun/",
                 swf_dir: str = "swf_assets"):
        """
        初始化应用程序。
        
        Args:
            ffdec_path: FFDec命令行工具路径
            download_url: SWF文件基础URL
            swf_dir: 下载文件的根目录
        """
        self.ffdec_path = ffdec_path
        self.base_url = download_url
        self.root_dir = Path(swf_dir)
        self.force_update = False
        self.version = load_last_version()
        
        # 设置FFDec路径
        FFDecExporter.set_ffdec_path(ffdec_path)
        
        # 初始化各个模块
        self.downloader = SWFDownloader(swf_dir, download_url)
        self.file_processor = FileProcessor()
        self.as3_parser = BqAS3Parser()
        self.xml_parser = XMLParser()
        
    def set_force_update(self, force: bool) -> None:
        """设置是否强制更新。"""
        self.force_update = force
        
    def classify_xml(self):
        version = self.version
        xml_dir = Path("compiled",version,'xml')
   
        output_dir = Path("output") /  version / "xml"
        if output_dir.exists():
            shutil.rmtree(output_dir) 
        output_dir.mkdir(exist_ok=True,parents=True)
        classify.classify_xml(xml_dir,output_dir)
        logger.info(f'xml文件分类完成,分类到{output_dir}')

    async def update_all_swf(self) -> None:
        """
        运行应用程序主流程。
        全自动更新所有游戏swf资源，和xml资源，以及as3
        """
        logger.info("开始运行BQYX所有swf资源及xml...")
        
        # 获取主SWF文件信息
        main_swf = await self.downloader.get_main_swf()
        logger.info(f"获取到主SWF文件: {main_swf}")
        
        # 更新根目录为包含版本号的路径
        version_stem = Path(main_swf).stem
      

        self.downloader.update_root_dir(self.root_dir / version_stem)
        
        # 检查是否需要更新
        last_main_swf = load_last_main_swf()
        is_old = (last_main_swf != main_swf) or self.force_update
        
        if not is_old:
            logger.info("当前版本没有更新，如需强制更新请设置force_update=True")
            return
        
        # 保存当前版本信息
        save_main_swf_info(main_swf)
        self.version = version_stem

        logger.info("已保存当前版本信息")
        
        # 下载主SWF文件
        local_main_swf = await self.downloader.download(main_swf)
        
        # 导出二进制数据
        main_game_compiled = Path('compiled') / self.version
        logger.info(f"导出主游戏的二进制数据(swf文件)到: {main_game_compiled}")
        
        exporter = FFDecExporter(
            input_swf=local_main_swf,
            output_dir=main_game_compiled
        )
        exporter.export_binary_data()
        
        # 重命名文件 将提取的binaryData => 当成swf文件看待
        self.file_processor.rename_bin_to_swf(main_game_compiled)
        
        # 导出脚本
        game_swf_path = main_game_compiled / 'L4399Main_gamefile.swf'
        if game_swf_path.exists():
            exporter = FFDecExporter(
                input_swf=game_swf_path,
                output_dir=main_game_compiled
            )
            #只指定了需要的as3文件，防止整个项目全部导出，这样太慢
            exporter.export_scripts(
                select_classes=['Gaming','dataAll._data.ConstantDefine']
            )

            # 提取常量和加载器信息
            main_game_project = main_game_compiled / 'scripts'
            version_dic = self.as3_parser.extract_specific_constants(main_game_project)
            
            # 下载XML SWF文件 local版本号.swf
            if 'xmlSwfUrl' in version_dic:
                await self.downloader.download(version_dic['xmlSwfUrl'])
                
                # 导出XML文件
                xml_swf = self.downloader.root_dir / version_dic['xmlSwfUrl']
                xml_compiled = main_game_compiled / 'xml'
                
                exporter = FFDecExporter(
                    input_swf=xml_swf,
                    output_dir=xml_compiled
                )
                exporter.export_binary_data()
                
                # 重命名和清理XML文件
                self.file_processor.rename_xml_bin(xml_compiled)
                self.file_processor.clean_xml_files(xml_compiled)
                logger.info(f"XML文件已解析并清理到: {xml_compiled}")
                
                # 提取并下载所有需要的SWF文件
                await self._download_all_swf_files(main_game_project, xml_compiled)
        
        logger.info("所有操作完成！")
    
    async def _download_all_swf_files(self, project_path: Path, xml_dir: Path) -> None:
        """下载所有需要的SWF文件。"""
        # 提取SWF URL列表 来自local版本号.swf 的所有xml
        # 比如<swfUrl> swf/vehcile/xxx <swfUrl/>
        swf_urls_from_xml = self.xml_parser.extract_swf_urls(xml_dir)
        # 从swfLoader的as3提取的
        swf_loaders = self.as3_parser.extract_swf_loaders(project_path)
        swf_urls_from_loaders = [rel_path for rel_path, _, _ in swf_loaders]
        
        # 合并并去重
        all_swf_urls = list(set(swf_urls_from_xml + swf_urls_from_loaders))
        
        logger.info(f"开始下载 {len(all_swf_urls)} 个SWF文件...")
        await self.downloader.download_multiple(all_swf_urls)
        logger.info("所有SWF文件下载完毕")

    def extract_equip_swf(self):
        '''
        将所有equip从equipGather提取出
        '''
        # equipGather
        # 先将equipGather的binaryData反编译，将所有 1_xxxx.bin => xxx.swf
        # 然后
        
        version = self.version

        equip_gather_dir = Path('swf_assets') / self.version / 'swf' / 'equip' / 'equipGather'
        # 重新提取,把之前的全部删除了
        if equip_gather_dir.exists():
            shutil.rmtree(equip_gather_dir)

        equip_gather_swf = self.file_processor.find_swf_by_prefix(
            'equipGather',
            Path('swf_assets') / self.version / 'swf' / 'equip'
        )
        FFDecExporter(
            input_swf= equip_gather_swf,
            output_dir=  equip_gather_dir
        ).export_binary_data()
        # 将 数字_xxxx.bin => xxxx.swf
        self.file_processor.rename_bin_to_swf(
             equip_gather_dir
        )
        # 移除没用的前后缀，只保留装备名称  前缀 装备名称 后缀 => 装备名称
        self.file_processor.rename_equip_swf(
             equip_gather_dir
        )
        logger.info(f'所有equip的swf反编译提取到{equip_gather_dir}')

    def compiled_all_equip_swf(self):
        '''
        自带将所有equip的swf内容
        '''
        output_dir = Path('compiled') / self.version /'equipGather'
        output_dir.mkdir(parents=True, exist_ok=True)
        equip_gather_dir = Path('swf_assets') / self.version / 'swf' / 'equip' / 'equipGather'
        FFDecExporter(
            input_swf= equip_gather_dir,
            output_dir=output_dir
        ).export_all()
        self.file_processor.rename_equip_dir(output_dir)
        logger.info(f'已将所有equip的swf内容反编译,输出到{output_dir}')
    def rename_all_equip_shapes(self):
        equip_gather_dir = Path('compiled') / self.version /'equipGather'
        for equip in equip_gather_dir.iterdir():
            self.file_processor.rename_images_and_svgs(equip)
        logger.info(f'以将所有equip的图片和svg全部改为英文名')
        
    def extract_all_equip_images(self):
        output_dir = Path('output') / self.version / 'images' / 'equip'
        if output_dir.exists():
            shutil.rmtree(output_dir)
        svg_fashion_dir = output_dir / 'svg' / 'fashionIcon'
        svg_equip_dir = output_dir / 'svg' / 'equipIcon'

        image_equip_dir = output_dir / 'image' / 'equipIcon'
        image_fashion_dir = output_dir / 'image' / "fashionIcon"
        # 确保文件夹存在
        svg_fashion_dir.mkdir(exist_ok=True,parents=True)
        svg_equip_dir.mkdir(exist_ok=True,parents=True)
        image_equip_dir.mkdir(exist_ok=True,parents=True)
        image_fashion_dir.mkdir(exist_ok=True,parents=True)

        equip_gather_dir = Path('compiled') / self.version /'equipGather'
        # 复制，并重命名，将icons_pants => aintSuit_pants这样提取
        for equip in equip_gather_dir.iterdir():
            copy_equip_svg(equip,svg_equip_dir)
            copy_fashion_svg(equip,svg_fashion_dir)
            copy_equip_image(equip,image_equip_dir)
            copy_fashion_image(equip,image_fashion_dir)
        logger.info(f'所有武器和时装图片，以分类到{output_dir}')
    # 提取
    # 部分护盾，饰品在equipIcon

    # 所有副手，部分饰品在thingsIcon
 