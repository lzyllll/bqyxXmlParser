"""应用入口：下载 SWF，提取资源，再交给解析器。"""
from __future__ import annotations

import logging
import shutil
from pathlib import Path

from bqyx_parser.downloader import SWFDownloader
from bqyx_parser.extractor import (
    BqAS3Parser,
    FFDecExporter,
    copy_equip_image,
    copy_equip_svg,
    copy_fashion_image,
    copy_fashion_svg,
    extract_swf_urls,
)
from bqyx_parser.tools import FileProcessor, load_last_main_swf, load_last_version, save_main_swf_info

logger = logging.getLogger(__name__)


class BQYXParserApp:
    """协调下载器、提取器和文件工具的主流程。"""

    def __init__(
        self,
        ffdec_path: str,
        download_url: str = "https://sbai.4399.com/4399swf/upload_swf/ftp15/linxy/20150324/gun/",
        swf_dir: str = "swf_assets",
    ):
        self.ffdec_path = ffdec_path
        self.base_url = download_url
        self.root_dir = Path(swf_dir)
        self.force_update = False
        self.version = load_last_version()

        FFDecExporter.set_ffdec_path(ffdec_path)
        self.downloader = SWFDownloader(swf_dir, download_url)
        self.file_processor = FileProcessor()
        self.as3_extractor = BqAS3Parser()

    def set_force_update(self, force: bool) -> None:
        """是否忽略本地版本记录，强制重新下载。"""
        self.force_update = force

    async def update_all_swf(self) -> None:
        """下载主 SWF，反编译 XML/AS3，再补齐依赖的资源 SWF。"""
        logger.info("开始运行BQYX所有swf资源及xml...")
        main_swf = await self.downloader.get_main_swf()
        logger.info("获取到主SWF文件: %s", main_swf)

        version_stem = Path(main_swf).stem
        self.downloader.update_root_dir(self.root_dir / version_stem)

        last_main_swf = load_last_main_swf()
        if last_main_swf == main_swf and not self.force_update:
            logger.info("当前版本没有更新，如需强制更新请设置force_update=True")
            return

        save_main_swf_info(main_swf)
        self.version = version_stem
        logger.info("已保存当前版本信息")

        local_main_swf = await self.downloader.download(main_swf)
        main_game_compiled = Path("compiled") / self.version
        logger.info("导出主游戏的二进制数据(swf文件)到: %s", main_game_compiled)

        FFDecExporter(input_swf=local_main_swf, output_dir=main_game_compiled).export_binary_data()
        self.file_processor.rename_bin_to_swf(main_game_compiled)

        game_swf_path = main_game_compiled / "L4399Main_gamefile.swf"
        if not game_swf_path.exists():
            logger.info("所有操作完成！")
            return

        exporter = FFDecExporter(input_swf=game_swf_path, output_dir=main_game_compiled)
        # 只导出需要的 AS3，避免整包脚本全导出
        exporter.export_scripts(select_classes=["Gaming", "dataAll._data.ConstantDefine"])

        main_game_project = main_game_compiled / "scripts"
        version_dic = self.as3_extractor.extract_specific_constants(main_game_project)
        if "xmlSwfUrl" in version_dic:
            await self.downloader.download(version_dic["xmlSwfUrl"])
            xml_swf = self.downloader.root_dir / version_dic["xmlSwfUrl"]
            xml_compiled = main_game_compiled / "xml"
            FFDecExporter(input_swf=xml_swf, output_dir=xml_compiled).export_binary_data()
            self.file_processor.rename_xml_bin(xml_compiled)
            self.file_processor.clean_xml_files(xml_compiled)
            logger.info("XML文件已解析并清理到: %s", xml_compiled)
            await self._download_all_swf_files(main_game_project, xml_compiled)

        logger.info("所有操作完成！")

    async def _download_all_swf_files(self, project_path: Path, xml_dir: Path) -> None:
        """合并 XML 与 AS3 中的 SWF 路径后批量下载。"""
        swf_urls_from_xml = extract_swf_urls(xml_dir)
        swf_loaders = self.as3_extractor.extract_swf_loaders(project_path)
        swf_urls_from_loaders = [rel_path for rel_path, _, _ in swf_loaders]
        all_swf_urls = list(set(swf_urls_from_xml + swf_urls_from_loaders))
        logger.info("开始下载 %s 个SWF文件...", len(all_swf_urls))
        await self.downloader.download_multiple(all_swf_urls)
        logger.info("所有SWF文件下载完毕")

    def extract_equip_swf(self) -> None:
        """从 equipGather 中拆出各装备 SWF。"""
        equip_gather_dir = Path("swf_assets") / self.version / "swf" / "equip" / "equipGather"
        if equip_gather_dir.exists():
            shutil.rmtree(equip_gather_dir)

        equip_gather_swf = self.file_processor.find_swf_by_prefix(
            "equipGather",
            Path("swf_assets") / self.version / "swf" / "equip",
        )
        FFDecExporter(input_swf=equip_gather_swf, output_dir=equip_gather_dir).export_binary_data()
        self.file_processor.rename_bin_to_swf(equip_gather_dir)
        self.file_processor.rename_equip_swf(equip_gather_dir)
        logger.info("所有equip的swf反编译提取到%s", equip_gather_dir)

    def compiled_all_equip_swf(self) -> None:
        """反编译全部装备 SWF 到 compiled/equipGather。"""
        output_dir = Path("compiled") / self.version / "equipGather"
        output_dir.mkdir(parents=True, exist_ok=True)
        equip_gather_dir = Path("swf_assets") / self.version / "swf" / "equip" / "equipGather"
        FFDecExporter(input_swf=equip_gather_dir, output_dir=output_dir).export_all()
        self.file_processor.rename_equip_dir(output_dir)
        logger.info("已将所有equip的swf内容反编译,输出到%s", output_dir)

    def rename_all_equip_shapes(self) -> None:
        """按 symbolClass 把装备图片改成英文名。"""
        equip_gather_dir = Path("compiled") / self.version / "equipGather"
        for equip in equip_gather_dir.iterdir():
            self.file_processor.rename_images_and_svgs(equip)
        logger.info("以将所有equip的图片和svg全部改为英文名")

    def extract_all_equip_images(self) -> None:
        """把装备图标和时装图标分类复制到 output/images。"""
        output_dir = Path("output") / self.version / "images" / "equip"
        if output_dir.exists():
            shutil.rmtree(output_dir)

        svg_fashion_dir = output_dir / "svg" / "fashionIcon"
        svg_equip_dir = output_dir / "svg" / "equipIcon"
        image_equip_dir = output_dir / "image" / "equipIcon"
        image_fashion_dir = output_dir / "image" / "fashionIcon"
        for path in (svg_fashion_dir, svg_equip_dir, image_equip_dir, image_fashion_dir):
            path.mkdir(exist_ok=True, parents=True)

        equip_gather_dir = Path("compiled") / self.version / "equipGather"
        for equip in equip_gather_dir.iterdir():
            copy_equip_svg(equip, svg_equip_dir)
            copy_fashion_svg(equip, svg_fashion_dir)
            copy_equip_image(equip, image_equip_dir)
            copy_fashion_image(equip, image_fashion_dir)
        logger.info("所有武器和时装图片，以分类到%s", output_dir)
