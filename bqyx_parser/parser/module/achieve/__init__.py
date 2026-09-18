from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.achieve import achieve, medel


def run(xml_dir: Path, output_dir: Path) -> None:
    achieve_out = output_dir / "achieve"
    achieve.run(xml_dir, achieve_out)
    medel.run(xml_dir, achieve_out)

