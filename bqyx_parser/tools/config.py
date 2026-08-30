"""读写 persistent_state.ini 和 parser_config.ini。"""
import configparser
from pathlib import Path
from typing import Optional

# 用来记录上次下载的swf版本
STATE_FILE = Path("persistent_state.ini")
# ffdec的配置
CONFIG_FILE = Path('parser_config.ini')

def save_main_swf_info(swf_name: str) -> None:
    """
    保存主SWF信息到持久化文件

    Args:
        swf_name: 主SWF文件名
    """
    config = configparser.ConfigParser()

    # 如果文件已存在，先读取现有内容
    if STATE_FILE.exists():
        config.read(STATE_FILE, encoding='utf-8')

    # 确保有默认section
    if 'DEFAULT' not in config:
        config['DEFAULT'] = {}

    config['DEFAULT']['last_main_swf'] = swf_name

    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        config.write(f)


def load_last_main_swf() -> Optional[str]:
    """
    从持久化文件加载上次的主SWF信息

    Returns:
        上次的主SWF文件名，如果不存在则返回None
    """
    if not STATE_FILE.exists():
        return None

    try:
        config = configparser.ConfigParser()
        config.read(STATE_FILE, encoding='utf-8')
        return config.get('DEFAULT', 'last_main_swf')
    except (configparser.Error, KeyError):
        return None
def load_FFDEC_path():
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE, encoding='utf-8')
        return config.get('DEFAULT', 'FFDEC')
    except (configparser.Error, KeyError):
        return 'ffdec-cli.exe'


def load_last_version():
    last_main_swf = load_last_main_swf()
    return Path(last_main_swf).stem if last_main_swf else None