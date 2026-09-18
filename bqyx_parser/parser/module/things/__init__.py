from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.things import item_strengthen, things


def run(xml_dir: Path, output_dir: Path) -> None:
    things_out = output_dir / "things"
    things.run(xml_dir, things_out)
    item_strengthen.run(xml_dir, things_out / "strengthen")

