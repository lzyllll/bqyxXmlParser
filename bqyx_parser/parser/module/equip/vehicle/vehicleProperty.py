from __future__ import annotations

import json
from pathlib import Path

from bqyx_parser.tools.logger import get_logger
from bqyx_parser.tools.property import parse_property

logger = get_logger()


def run(xml_dir: Path | None = None, out_put_dir: Path | None = None) -> None:
    if xml_dir is None:
        xml_dir = Path(r"compiled\v3671\xml")
    if out_put_dir is None:
        out_put_dir = Path(r"output\v3671\json\equip\vehicle")
    out_put_dir.mkdir(parents=True, exist_ok=True)

    xml_path = xml_dir / "vehicleProperty.xml"
    output_path = out_put_dir / "vehicleProperty.json"


if __name__ == "__main__":
    run()
