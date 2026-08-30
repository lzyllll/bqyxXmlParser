"""导出技能 JSON。"""
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from bqyx_parser.parser.module.skill import main


if __name__ == "__main__":
    main()
