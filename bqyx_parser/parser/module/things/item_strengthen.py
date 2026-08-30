import json
from pathlib import Path
import xml.etree.ElementTree as ET
from bqyx_parser.tools.property import parse_property

# ---------- 主程序 ----------
if __name__ == "__main__":
    xml_dir = Path(r"compiled\v3671\xml")
    out_put_dir = Path(r"output\v3671\json\things\strengthen")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "itemsStrengthen.xml"
    output_path = out_put_dir / "itemsStrengthen.json"

    # 解析并生成 JSON
    data = parse_property(xml_path)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)