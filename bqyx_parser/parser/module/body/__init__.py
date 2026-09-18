from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.body import hero, normal


def run(xml_dir: Path, output_dir: Path) -> None:
    body_out = output_dir / "body"
    hero.run(xml_dir, body_out)
    normal.run(xml_dir, body_out)

