
import json
from pathlib import Path

from bqyx_parser.tools.property import parse_property



from bqyx_parser.tools.compare import compare_data
from bqyx_parser.tools.logger import get_logger

logger = get_logger()

if __name__ == "__main__":
    xml_dir = Path(r"compiled\v3671\xml")
    out_put_dir = Path(r"output\v3671\json\union")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "unionBuildingProperty.xml"
    output_path = out_put_dir / "unionBuildingProperty.json"

    # 解析并生成 JSON
    data = parse_property(xml_path)
    

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s", output_path)
    resource_path = Path(r"D:\bqyx\rs\resource\union\unionBuildingProperty.json")
    with open(resource_path, "r", encoding="utf-8") as f:
        old = json.load(f)
    logger.info("对比 %s", resource_path)
    compare_data(old, data)
