
from pathlib import Path
import json

from bqyx_parser.tools.logger import get_logger
from bqyx_parser.tools.property import parse_property

logger = get_logger()


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\resource\things\strengthen")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "itemsStrengthen.xml"
    output_path = out_put_dir / "itemsStrengthen.json"

    logger.info("解析 %s", xml_path)
    data = parse_property(xml_path)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info("已保存 %s", output_path)


if __name__ == "__main__":
    run()
