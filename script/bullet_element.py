"""导出子弹 JSON。"""
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from bqyx_parser.parser.module.bullet import main


if __name__ == "__main__":
    main()
