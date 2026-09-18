from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.drop import dropColor


def run(xml_dir: Path, output_dir: Path) -> None:
    drop_out = output_dir / "drop"
    dropColor.run(xml_dir, drop_out)

