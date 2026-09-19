#!/usr/bin/env python3
"""全自动根据源码提取对应版本的图片/矢量图标资源。

用法示例:
    python script/export_version_assets.py --version v3680
    python script/export_version_assets.py --version v3680 --output output/v3680/assets
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# 添加项目根目录到 sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from bqyx_parser.extractor.asset_extractor import AssetExtractor
from bqyx_parser.tools import load_last_version


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="根据源码自动提取对应版本的SWF图片/图标资源")
    parser.add_argument(
        "-v",
        "--version",
        default="v3680",
        help="目标版本号 (例如 v3680，默认: v3680 或最新记录版本)",
    )
    parser.add_argument(
        "-s",
        "--swf-dir",
        default=None,
        help="SWF 资源根目录 (默认: swf_assets/<version>)",
    )
    parser.add_argument(
        "-c",
        "--scripts-dir",
        default=None,
        help="反编译 AS3 源码目录 (默认: compiled/<version>/scripts)",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="输出 assets 目录 (默认: output/<version>/assets)",
    )

    args = parser.parse_args()
    version = args.version or load_last_version() or "v3680"

    extractor = AssetExtractor(
        version=version,
        swf_dir=args.swf_dir,
        scripts_dir=args.scripts_dir,
        output_assets_dir=args.output,
    )

    result = extractor.run()
    print("\n🎉 提取任务已全部完成！统计结果：")
    print(f"  - 图标分类: {len(result.get('icons', {}))} 个分类")
    for k, v in result.get("icons", {}).items():
        print(f"      • {k}: {v} 个 PNG")
    print(f"  - 装备套装 (EquipGather): {result.get('equip_suits', 0)} 套")
    print(f"  - 武器兵器分类: {len(result.get('weapons', {}))} 个分类")
    for k, v in result.get("weapons", {}).items():
        print(f"      • {k}: {v} 个 PNG")
    print(f"  - 系统通用图标与底框 (icons): {result.get('ui_system_icons', 0)} 个文件")
    print(f"  - 同步至 D:\\bqyx\\rs\\assets: {result.get('rs_synced_files', 0)} 个文件")


if __name__ == "__main__":
    main()

