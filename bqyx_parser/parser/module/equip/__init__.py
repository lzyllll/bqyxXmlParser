from __future__ import annotations

from pathlib import Path

from bqyx_parser.parser.module.equip import (
    blackEquip,
    darkgoldEquip,
    equipImage,
    equipRange,
    fashion,
    suitProperty,
)
from bqyx_parser.parser.module.equip.base import scan_father_equips
from bqyx_parser.parser.module.equip.device import device
from bqyx_parser.parser.module.equip.jewelry import jewelry
from bqyx_parser.parser.module.equip.shield import shield
from bqyx_parser.parser.module.equip.vehicle import vehicle, vehicleProperty
from bqyx_parser.parser.module.equip.weapon import weapon

__all__ = ["run", "scan_father_equips"]


def run(xml_dir: Path, output_dir: Path) -> None:
    equip_out = output_dir / "equip"
    blackEquip.run(xml_dir, equip_out)
    darkgoldEquip.run(xml_dir, equip_out)
    equipImage.run(xml_dir, equip_out)
    equipRange.run(xml_dir, equip_out)
    fashion.run(xml_dir, equip_out)
    suitProperty.run(xml_dir, equip_out)
    device.run(xml_dir, equip_out / "device")
    jewelry.run(xml_dir, equip_out / "jewelry")
    shield.run(xml_dir, equip_out / "shield")
    vehicle.run(xml_dir, equip_out / "vehicle")
    vehicleProperty.run(xml_dir, equip_out / "vehicle")
    weapon.run(xml_dir, equip_out / "weapon")

