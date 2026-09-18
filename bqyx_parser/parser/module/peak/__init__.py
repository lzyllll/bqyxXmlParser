from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.peak import craftPro, peakPro


def run(xml_dir: Path, output_dir: Path) -> None:
    peak_out = output_dir / "peak"
    peakPro.run(xml_dir, peak_out)
    craftPro.run(xml_dir, peak_out)

