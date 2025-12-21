"""BQYX XML解析器主入口。"""
import asyncio
import logging
from pathlib import Path

from bqyx_parser.core.app import BQYXParserApp
from bqyx_parser.file_handler import classify
from bqyx_parser.file_handler.file_processor import FileProcessor

from bqyx_parser.config.persistent_state import load_last_main_swf, load_last_version,load_FFDEC_path
# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 全局常量
DOWNLOAD_URL = "https://sbai.4399.com/4399swf/upload_swf/ftp15/linxy/20150324/gun/"
FFDEC_PATH =  load_FFDEC_path()
# 修改为你的FFDec反编译路径


def main():
    """
    主函数，启动解析器应用程序。
    """
    # 创建应用实例
    # 如果没有创建环境变量，需要自己指定ffdec-cli的路径
    app = BQYXParserApp(
        ffdec_path=FFDEC_PATH,
        swf_dir="swf_assets"
    )

    
    # 可以选择设置强制更新
    app.set_force_update(False)
    # 更新，获取所有的swf文件 自动判断 耗时操作15s
    asyncio.run(app.update_all_swf())


    # 分类xml文件的步骤，默认分类最近一次版本，可指定版本
    #  拆分这个xml文件，  原生的ET adata注释根据string转xml 会破坏，
    #  需要下载lxml的库
    app.classify_xml()

    if input('是否获取所有装备图片,大约耗时45s，确认为1，其他为取消') == '1':
        #获取所有equip 图片的步骤
        # # # 反编译equipGather获取所有equip的swf 
        app.extract_equip_swf()
        # # # 将所有equip的swf反编译 //耗时操作 45s
        # # # 并将文件名称 删除.swf后缀
        app.compiled_all_equip_swf()
        # # 将所有equip的图片改名 1.png=> pants_icon.png 
        app.rename_all_equip_shapes()
        # 将 pants_icon.png =>  aintSuit_pants.png 分类到 equipIcon文件夹
        # 将 fashion_icon.png => aintSuit.png 分类到 fashionIcon文件夹
        app.extract_all_equip_images()





if __name__ == "__main__":
    main()