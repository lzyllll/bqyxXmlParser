from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.head import head, headHonor


def run(xml_dir: Path, output_dir: Path) -> None:
    head_out = output_dir / "head"
    head.run(xml_dir, head_out)
    headHonor.run(xml_dir, head_out)

