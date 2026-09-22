"""BQYX 资源工具与 XML 解析器主入口 (Click CLI)。"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import click

from bqyx_parser.app import BQYXParserApp
from bqyx_parser.parser.registry import get_available_modules, run_all, run_module
from bqyx_parser.tools import load_FFDEC_path, load_last_version

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("bqyx_cli")


@click.group()
def cli() -> None:
    """爆枪英雄 (BQYX) 资源下载、反编译与 XML 解析命令行工具。"""
    pass


# ---------------------------------------------------------------------------
# 1. SWF 资源相关指令组
# ---------------------------------------------------------------------------
@cli.group("swf")
def swf_group() -> None:
    """SWF 资源相关操作（下载更新、反编译提取、装备图片导出）。"""
    pass


@swf_group.command("update")
@click.option("-f", "--force", is_flag=True, help="强制重新下载与反编译（忽略本地版本记录）")
@click.option("-d", "--swf-dir", default="swf_assets", help="SWF 下载根目录 (默认: swf_assets)")
def swf_update(force: bool, swf_dir: str) -> None:
    """从 4399 下载主 SWF，导出 AS3/XML 二进制，并下载依赖资源 SWF。"""
    ffdec_path = load_FFDEC_path()
    app = BQYXParserApp(ffdec_path=ffdec_path, swf_dir=swf_dir)
    app.set_force_update(force)
    logger.info("开始更新 SWF 资源 (force=%s)...", force)
    asyncio.run(app.update_all_swf())
    logger.info("SWF 资源更新完成！")


@swf_group.command("equip")
@click.option("-v", "--version", default=None, help="游戏版本号 (默认: 最新记录版本)")
@click.option("-d", "--swf-dir", default="swf_assets", help="SWF 存放目录 (默认: swf_assets)")
def swf_equip(version: str | None, swf_dir: str) -> None:
    """从 equipGather 提取各装备 SWF，反编译并分类导出装备/时装图片与SVG。"""
    ffdec_path = load_FFDEC_path()
    app = BQYXParserApp(ffdec_path=ffdec_path, swf_dir=swf_dir)
    if version:
        app.version = version
    logger.info("正在提取与反编译装备 SWF 图片 (版本: %s)...", app.version)
    app.extract_equip_swf()
    app.compiled_all_equip_swf()
    app.rename_all_equip_shapes()
    app.extract_all_equip_images()
    logger.info("装备图片提取完成！")


@swf_group.command("assets")
@click.option("-v", "--version", default=None, help="游戏版本号 (默认: 最新记录版本)")
@click.option("-d", "--swf-dir", default=None, help="SWF 存放目录 (默认: swf_assets/<version>)")
@click.option("-c", "--scripts-dir", default=None, help="AS3 源码目录 (默认: compiled/<version>/scripts)")
@click.option("-o", "--output", default=None, help="输出 assets 目录 (默认: output/<version>/assets)")
def swf_assets(version: str | None, swf_dir: str | None, scripts_dir: str | None, output: str | None) -> None:
    """根据 decompiled AS3 源码自动提取该版本所需的所有图片/矢量图标资源。"""
    from bqyx_parser.extractor.asset_extractor import AssetExtractor

    target_ver = version or load_last_version() or "v3690"
    logger.info("正在根据源码提取 SWF 资源到 assets (版本: %s)...", target_ver)
    extractor = AssetExtractor(
        version=target_ver,
        swf_dir=swf_dir,
        scripts_dir=scripts_dir,
        output_assets_dir=output,
    )
    extractor.run()
    logger.info("SWF 资源提取完成！")


@swf_group.command("all")
@click.option("-f", "--force", is_flag=True, help="强制重新下载更新")
@click.option("-d", "--swf-dir", default="swf_assets", help="SWF 下载根目录")
def swf_all(force: bool, swf_dir: str) -> None:
    """一键执行全部 SWF 流程：拉取主SWF及依赖 + 提取反编译装备图片。"""
    ffdec_path = load_FFDEC_path()
    app = BQYXParserApp(ffdec_path=ffdec_path, swf_dir=swf_dir)
    app.set_force_update(force)
    logger.info("=== [1/2] 运行 SWF 资源拉取与主解析 ===")
    asyncio.run(app.update_all_swf())
    logger.info("=== [2/2] 提取反编译装备图片 ===")
    app.extract_equip_swf()
    app.compiled_all_equip_swf()
    app.rename_all_equip_shapes()
    app.extract_all_equip_images()
    logger.info("全部 SWF 流程执行完毕！")


# ---------------------------------------------------------------------------
# 2. XML 解析相关指令
# ---------------------------------------------------------------------------
@cli.command("parse")
@click.option(
    "-v",
    "--version",
    default=None,
    help="指定解析的游戏版本 (例如: v3671，默认读取本地最新版本)",
)
@click.option(
    "-m",
    "--module",
    "modules",
    multiple=True,
    help="指定解析的模块 (如 worldMap, equip, things 等，可多次指定；默认 all 全部模块)",
)
@click.option(
    "-l",
    "--list",
    "list_modules",
    is_flag=True,
    help="列出所有可用的解析模块并退出",
)
@click.option(
    "-x",
    "--xml-dir",
    default=None,
    type=click.Path(path_type=Path),
    help="自定义 XML 来源目录 (默认: compiled/<version>/xml)",
)
@click.option(
    "-o",
    "--output-dir",
    default=None,
    type=click.Path(path_type=Path),
    help="自定义 JSON 输出目录 (默认: output/<version>/resource)",
)
def parse_cmd(
    version: str | None,
    modules: tuple[str, ...],
    list_modules: bool,
    xml_dir: Path | None,
    output_dir: Path | None,
) -> None:
    """将反编译后的游戏 XML 解析为统一 JSON 配置文件。"""
    available_mods = get_available_modules()

    if list_modules:
        click.echo("\n" + "=" * 60)
        click.echo("  BQYX XML 可用解析模块列表")
        click.echo("=" * 60)
        for name, desc in available_mods.items():
            click.echo(f"  - {name:<12} : {desc}")
        click.echo("-" * 60)
        click.echo("提示: 使用 -m <module> 单独解析，或省略 -m 解析全部模块。\n")
        return

    # 版本自动识别
    if not version:
        version = load_last_version()
        if not version:
            compiled_dir = Path("compiled")
            if compiled_dir.exists():
                candidates = [d.name for d in compiled_dir.iterdir() if d.is_dir() and d.name.startswith("v")]
                if candidates:
                    version = sorted(candidates)[-1]
        if not version:
            raise click.UsageError("未能自动检测到游戏版本，请使用 -v / --version 指定版本号（例如: -v v3671）。")

    # 路径默认值
    if xml_dir is None:
        xml_dir = Path("compiled") / version / "xml"
    if output_dir is None:
        output_dir = Path("output") / version / "resource"

    if not xml_dir.exists():
        raise click.ClickException(f"XML 目录不存在: {xml_dir}。请先执行 `python main.py swf update` 下载反编译 XML。")

    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("当前解析目标版本: %s", version)
    logger.info("XML 来源目录: %s", xml_dir)
    logger.info("JSON 输出目录: %s", output_dir)

    # 判断是否全部模块
    if not modules or "all" in modules:
        run_all(xml_dir, output_dir)
    else:
        for mod in modules:
            if mod not in available_mods:
                valid_list = ", ".join(available_mods.keys())
                raise click.UsageError(f"未知模块 '{mod}'。可用模块: {valid_list}")
            run_module(mod, xml_dir, output_dir)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
