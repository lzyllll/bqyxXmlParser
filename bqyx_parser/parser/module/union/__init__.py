from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.union import (
    military,
    unionBattle,
    unionBuilding,
    unionBuildingProperty,
    unionData,
    unionTask,
)


def run(xml_dir: Path, output_dir: Path) -> None:
    union_out = output_dir / "union"
    military.run(xml_dir, union_out)
    unionBattle.run(xml_dir, union_out)
    unionBuilding.run(xml_dir, union_out)
    unionBuildingProperty.run(xml_dir, union_out)
    unionData.run(xml_dir, union_out)
    unionTask.run(xml_dir, union_out)

