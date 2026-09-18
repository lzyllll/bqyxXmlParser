from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.arms import arms, armsCharger, armsName


def run(xml_dir: Path, output_dir: Path) -> None:
    arms_out = output_dir / "arms"
    arms.run(xml_dir, arms_out)
    armsCharger.run(xml_dir, arms_out)
    armsName.run(xml_dir, arms_out)

