
from pathlib import Path
import json

from bqyx_parser.tools.compare import compare_data
from bqyx_parser.tools.logger import get_logger
from bqyx_parser.tools.property import parse_property

logger = get_logger()

# ---------- 主程序 ----------
if __name__ == "__main__":
    xml_dir = Path(r"compiled\v3671\xml")
    out_put_dir = Path(r"output\v3671\json\things\strengthen")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "itemsStrengthen.xml"
    output_path = out_put_dir / "itemsStrengthen.json"
    resource_path = Path(r"D:\bqyx\rs\resource\things\strengthen\itemsStrengthenData.json")

    data = parse_property(xml_path)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s", output_path)
    with open(resource_path, "r", encoding="utf-8") as f:
        old = json.load(f)
    logger.info("对比 %s", resource_path)
    compare_data(old, data)
