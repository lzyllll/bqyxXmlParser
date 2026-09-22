from __future__ import annotations

from pathlib import Path
import pytest

from bqyx_parser.parser.module.equip.base import scan_father_equips
from bqyx_parser.parser.module.equip.device.device import create_device_factory
from bqyx_parser.parser.module.equip.jewelry.jewelry import create_jewelry_factory
from bqyx_parser.parser.module.equip.shield.shield import create_shield_factory
from bqyx_parser.parser.module.equip.vehicle.vehicle import VEHICLE_FATHER_NAMES, create_vehicle_factory
from bqyx_parser.parser.module.equip.weapon.weapon import create_weapon_factory


@pytest.fixture
def xml_dir():
    base = Path(__file__).resolve().parents[1]
    dir_3690 = base / "compiled" / "v3690" / "xml"
    if dir_3690.exists():
        return dir_3690
    return base / "compiled" / "v3671" / "xml"


def test_scan_weapon_by_father_name(xml_dir):
    factory = create_weapon_factory()
    weapons = scan_father_equips(xml_dir, "weapon", factory, inject_father_name=True)
    assert len(weapons) >= 50
    assert all(w.get("fatherName") == "weapon" for w in weapons)
    assert any(w.get("baseLabel") == "butcherBlade" for w in weapons)


def test_scan_vehicle_by_father_name(xml_dir):
    factory = create_vehicle_factory()
    vehicles = scan_father_equips(
        xml_dir,
        VEHICLE_FATHER_NAMES,
        factory,
        inject_father_name=True,
        primary_file="vehicle.xml",
    )
    assert len(vehicles) >= 50
    assert all(v.get("fatherName") in VEHICLE_FATHER_NAMES for v in vehicles)
    assert any(v.get("name") == "GaiaFit" for v in vehicles)


def test_scan_device_by_father_name(xml_dir):
    factory = create_device_factory()
    devices = scan_father_equips(xml_dir, "device", factory, inject_father_name=False)
    assert len(devices) >= 20
    assert any(d.get("name") == "earthquakeGenerator" for d in devices)


def test_scan_jewelry_by_father_name(xml_dir):
    factory = create_jewelry_factory()
    jewelries = scan_father_equips(xml_dir, "jewelry", factory, inject_father_name=True)
    assert len(jewelries) >= 6
    assert all(j.get("fatherName") == "jewelry" for j in jewelries)
    assert any(j.get("baseLabel") == "boneRing" for j in jewelries)


def test_scan_shield_by_father_name(xml_dir):
    factory = create_shield_factory()
    shields = scan_father_equips(xml_dir, "shield", factory, inject_father_name=True)
    assert len(shields) >= 3
    assert all(s.get("fatherName") == "shield" for s in shields)
    assert any(s.get("baseLabel") == "crabShell" for s in shields)

