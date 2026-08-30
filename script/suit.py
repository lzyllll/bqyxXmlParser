"""导出套装和装备 JSON。"""
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from bqyx_parser.parser.suit import main


if __name__ == "__main__":
    main()
