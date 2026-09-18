from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.skin import armsSkin, weaponSkin


def run(xml_dir: Path, output_dir: Path) -> None:
    skin_out = output_dir / "skin"
    armsSkin.run(xml_dir, skin_out)
    weaponSkin.run(xml_dir, skin_out)

