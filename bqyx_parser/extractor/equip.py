"""复制并重命名装备 / 时装图标。"""
from pathlib import Path


def copy_dir(src_dir: Path, output_dir: Path, icon_dict: dict) -> None:
    """按映射表复制文件，例如 coat_icon -> aintSuit_coat。"""
    for file in src_dir.iterdir():
        if file.stem in icon_dict:
            new_path = file.with_stem(icon_dict.get(file.stem))
            dest = output_dir / new_path.name
            dest.write_bytes(file.read_bytes())


def copy_equip_svg(target: Path, output_dir: Path) -> None:
    """复制装备 SVG 图标。"""
    icons_dict = dict(
        zip(
            ["head_icon", "belt_icon", "coat_icon", "pants_icon"],
            [target.stem + "_head", target.stem + "_belt", target.stem + "_coat", target.stem + "_pants"],
        )
    )
    copy_dir(target / "shapes", output_dir, icons_dict)


def copy_equip_image(target: Path, output_dir: Path) -> None:
    """复制装备 PNG 图标。"""
    icons_dict = dict(
        zip(
            ["head_icon", "belt_icon", "coat_icon", "pants_icon"],
            [target.stem + "_head", target.stem + "_belt", target.stem + "_coat", target.stem + "_pants"],
        )
    )
    copy_dir(target / "images", output_dir, icons_dict)


def copy_fashion_svg(target: Path, output_dir: Path) -> None:
    """复制时装 SVG 图标。"""
    copy_dir(target / "shapes", output_dir, {"fashion_icon": target.stem})


def copy_fashion_image(target: Path, output_dir: Path) -> None:
    """复制时装 PNG 图标。"""
    copy_dir(target / "images", output_dir, {"fashion_icon": target.stem})
