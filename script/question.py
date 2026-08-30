"""导出每日问答 JSON。"""
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from bqyx_parser.parser.question import main


if __name__ == "__main__":
    main()
