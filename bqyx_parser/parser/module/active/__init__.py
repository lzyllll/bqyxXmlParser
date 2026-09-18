from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.active import active


def run(xml_dir: Path, output_dir: Path) -> None:
    active_out = output_dir / "active"
    active.run(xml_dir, active_out)

