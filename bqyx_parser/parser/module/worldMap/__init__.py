from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.worldMap import worldMap


def run(xml_dir: Path, output_dir: Path) -> None:
    world_map_out = output_dir / "worldMap"
    worldMap.run(xml_dir, world_map_out)

