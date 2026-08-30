"""BQYX XML解析器主入口。"""
import asyncio
import logging

from bqyx_parser.app import BQYXParserApp
from bqyx_parser.tools import load_FFDEC_path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

FFDEC_PATH = load_FFDEC_path()


def main():
    app = BQYXParserApp(ffdec_path=FFDEC_PATH, swf_dir="swf_assets")
    app.set_force_update(False)
    asyncio.run(app.update_all_swf())

    if input("是否获取所有装备图片,大约耗时45s，确认为1，其他为取消") == "1":
        app.extract_equip_swf()
        app.compiled_all_equip_swf()
        app.rename_all_equip_shapes()
        app.extract_all_equip_images()


if __name__ == "__main__":
    main()
