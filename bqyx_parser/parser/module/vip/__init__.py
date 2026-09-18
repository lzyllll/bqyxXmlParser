from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.vip import vip


def run(xml_dir: Path, output_dir: Path) -> None:
    vip_out = output_dir / "vip"
    vip.run(xml_dir, vip_out)

