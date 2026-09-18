from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.pet import petStrengthen


def run(xml_dir: Path, output_dir: Path) -> None:
    pet_out = output_dir / "pet"
    petStrengthen.run(xml_dir, pet_out)

