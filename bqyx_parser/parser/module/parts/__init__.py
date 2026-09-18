from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.parts import partsProperty, partsRarePro


def run(xml_dir: Path, output_dir: Path) -> None:
    parts_out = output_dir / "parts"
    partsProperty.run(xml_dir, parts_out)
    partsRarePro.run(xml_dir, parts_out)

