"""源码驱动的 SWF 资源全自动提取器。

根据 decompiled AS3 源码 (Gaming.as) 中注册的 SWFLoader 配置，
动态提取所有对应的图标、装备(包含套装及部件)、武器等矢量 SVG 和图片资源，
导出至规范的 assets 目录 (例如 output/<version>/assets/img/<Category>/...)。
"""
from __future__ import annotations

import logging
import re
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from bqyx_parser.extractor.as3 import BqAS3Parser
from bqyx_parser.extractor.ffdec import FFDecExporter
from bqyx_parser.tools import load_FFDEC_path

logger = logging.getLogger(__name__)


class AssetExtractor:
    """全自动根据源码提取游戏资源。"""

    # 常见标准图标分类映射与对应 SWF 查找标签
    ICON_LABELS = {
        "AchieveIcon": "图标",
        "ThingsIcon": "图标",
        "SkillIcon": "图标",
        "NewIcon": "图标",
        "PartsIcon": "图标",
        "IconGather": "图标",
        "BodyImg": "图标",
        "FoodUI": "UI",
        "equipIcon": "装备图标",
    }

    # 枪械兵器分类
    WEAPON_LABELS = {
        "newGun": "武器",
        "specialGun": "武器",
        "weapon": "兵器",
    }

    def __init__(
        self,
        version: str = "v3680",
        swf_dir: str | Path | None = None,
        scripts_dir: str | Path | None = None,
        output_assets_dir: str | Path | None = None,
        ffdec_path: str | None = None,
    ):
        self.version = version
        self.swf_dir = Path(swf_dir or Path("swf_assets") / version)
        self.scripts_dir = Path(scripts_dir or Path("compiled") / version / "scripts")
        self.output_assets_dir = Path(output_assets_dir or Path("output") / version / "assets")
        self.img_output_dir = self.output_assets_dir / "img"

        self.ffdec_path = ffdec_path or load_FFDEC_path()
        FFDecExporter.set_ffdec_path(self.ffdec_path)
        self.as3_parser = BqAS3Parser()

    def clean_old_images(self) -> None:
        """根据需求清理旧的 images 输出目录。"""
        candidates = [
            Path("output") / self.version / "images",
            Path("output") / "v3671" / "images",
            Path("output") / "v3680" / "images",
        ]
        for p in candidates:
            if p.exists() and p.is_dir():
                logger.info("清理旧 images 目录: %s", p)
                try:
                    shutil.rmtree(p)
                except Exception as exc:
                    logger.warning("清理 %s 失败: %s", p, exc)

    def find_actual_swf(self, rel_path: str, label: str) -> Optional[Path]:
        """定位本地实际存在的 SWF 文件，支持版本号变动模糊匹配。"""
        direct_path = self.swf_dir / rel_path
        if direct_path.exists():
            return direct_path

        # 尝试按目录模糊匹配
        parent_rel = Path(rel_path).parent
        stem_prefix = re.sub(r"\d+$", "", Path(rel_path).stem)
        target_dir = self.swf_dir / parent_rel
        if target_dir.exists():
            candidates = list(target_dir.glob(f"{stem_prefix}*.swf"))
            if candidates:
                return candidates[0]

        # 全局扫描
        candidates = list(self.swf_dir.rglob(f"{label}*.swf"))
        if candidates:
            return candidates[0]

        return None

    def _read_symbols(self, folder: Path) -> Dict[str, str]:
        """读取导出目录中的 symbols.csv 符号映射。"""
        sym_paths = list(folder.rglob("symbols.csv"))
        for p in sym_paths:
            if p.exists():
                mapping = {}
                for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                    line = line.strip()
                    if not line or ";" not in line:
                        continue
                    parts = line.split(";", 1)
                    mapping[parts[0].strip()] = parts[1].strip()
                return mapping
        return {}

    def extract_icon_swfs(self, loaders: List[Tuple[str, str, str]]) -> Dict[str, int]:
        """从图标类 SWF 中提取全部矢量 SVG 资源。"""
        stats: Dict[str, int] = {}
        for rel_path, label, desc in loaders:
            if label not in self.ICON_LABELS and desc not in ("图标", "装备图标"):
                continue

            swf_path = self.find_actual_swf(rel_path, label)
            if not swf_path:
                logger.warning("未找到 SWF 文件: %s (label=%s)", rel_path, label)
                continue

            category_dir = self.img_output_dir / label
            category_dir.mkdir(parents=True, exist_ok=True)

            logger.info("正在导出 %s 资源 (来自 %s)...", label, swf_path.name)
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir)
                exporter = FFDecExporter(output_dir=tmp_path, input_swf=swf_path)
                exporter.export_sprites(formats="sprite:svg")

                count = 0
                sprite_dirs = [p for p in tmp_path.iterdir() if p.is_dir() and p.name.startswith("DefineSprite_")]
                for sdir in sprite_dirs:
                    parts = sdir.name.split("_", 2)
                    if len(parts) < 3:
                        continue
                    class_name = parts[2]
                    svg_file = sdir / "1.svg"
                    if svg_file.exists():
                        dest_file = category_dir / f"{class_name}.svg"
                        dest_file.write_bytes(svg_file.read_bytes())
                        count += 1

                logger.info("  ✓ %s 完成导出: %d 个矢量 SVG", label, count)
                stats[label] = count

        return stats

    def extract_equip_gather(self) -> int:
        """反编译 equipGather，提取所有套装各部位和时装的矢量 SVG。"""
        candidates = list(self.swf_dir.rglob("equipGather*.swf"))
        if not candidates:
            logger.warning("在 %s 未找到 equipGather*.swf", self.swf_dir)
            return 0

        equip_gather_swf = candidates[0]
        equip_output_base = self.img_output_dir / "EquipGather"
        equip_output_base.mkdir(parents=True, exist_ok=True)

        logger.info("正在反编译装备汇总包: %s...", equip_gather_swf.name)
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            # 1. 导出二进制数据
            exporter = FFDecExporter(output_dir=tmp_path, input_swf=equip_gather_swf)
            exporter.export_binary_data()

            bin_files = list(tmp_path.glob("*.bin"))
            logger.info("  从 equipGather 中提取到 %d 个子套装/装备二进制文件", len(bin_files))

            total_suits = 0
            for bin_file in bin_files:
                name = bin_file.name
                # 提取纯净套装名称
                # 例如 68_equipGather365_fla.MainTimeline_aintSuitClass_dataClass.bin -> aintSuit
                suit_name = re.sub(r"^\d+_equipGather\d+_fla\.MainTimeline_", "", name)
                suit_name = suit_name.replace("Class_dataClass.bin", "").replace(".bin", "")
                if not suit_name:
                    continue

                suit_swf = tmp_path / f"{suit_name}.swf"
                suit_swf.write_bytes(bin_file.read_bytes())

                # 先导出 symbolClass 查验该套装是否有图标，并获取精准 character ID
                sym_export_dir = tmp_path / f"sym_{suit_name}"
                sym_exporter = FFDecExporter(output_dir=sym_export_dir, input_swf=suit_swf)
                sym_exporter.export_symbol_class()

                suit_symbols = self._read_symbols(sym_export_dir)
                # 过滤出所有图标相关的 character ID
                target_ids = [
                    cid
                    for cid, sname in suit_symbols.items()
                    if "icon" in sname.lower() or sname in ("chip", "heart", "weapon", "arms")
                ]

                # 如果没有图标定义（例如纯动作特效 SWF 如 hundredGhostsHD），直接跳过
                if not target_ids:
                    continue

                # 精准只导出目标图标 sprite，避免反编译整套复杂人体骨骼动作（速度提升数十倍）
                suit_export_dir = tmp_path / f"export_{suit_name}"
                suit_exporter = FFDecExporter(output_dir=suit_export_dir, input_swf=suit_swf)
                suit_exporter.export_sprites(formats="sprite:svg", select_id=target_ids)

                suit_dest_dir = equip_output_base / suit_name
                suit_dest_dir.mkdir(parents=True, exist_ok=True)

                icon_mapping = {
                    "head_icon": f"{suit_name}_head.svg",
                    "coat_icon": f"{suit_name}_coat.svg",
                    "pants_icon": f"{suit_name}_pants.svg",
                    "belt_icon": f"{suit_name}_belt.svg",
                    "fashion_icon": f"{suit_name}.svg",
                }

                exported_files = 0
                sprite_dirs = [p for p in suit_export_dir.iterdir() if p.is_dir() and p.name.startswith("DefineSprite_")]
                for sdir in sprite_dirs:
                    parts = sdir.name.split("_", 2)
                    if len(parts) < 3:
                        continue
                    symbol_label = parts[2]
                    svg_file = sdir / "1.svg"
                    if not svg_file.exists():
                        continue

                    # 部件映射
                    if symbol_label in icon_mapping:
                        dest_name = icon_mapping[symbol_label]
                        (suit_dest_dir / dest_name).write_bytes(svg_file.read_bytes())
                        exported_files += 1
                    elif symbol_label.endswith("_icon") or symbol_label.startswith("head_icon"):
                        # 如 head_icon2 -> suit_head2.svg
                        suffix = symbol_label.replace("head_icon", "_head").replace("_icon", "")
                        dest_name = f"{suit_name}{suffix}.svg"
                        (suit_dest_dir / dest_name).write_bytes(svg_file.read_bytes())
                        exported_files += 1
                    elif symbol_label in ("chip", "heart", "weapon", "arms"):
                        (suit_dest_dir / f"{symbol_label}.svg").write_bytes(svg_file.read_bytes())
                        exported_files += 1

                if exported_files == 0:
                    try:
                        suit_dest_dir.rmdir()
                    except Exception:
                        pass
                else:
                    total_suits += 1

            logger.info("  ✓ EquipGather 完成导出: %d 个套装目录", total_suits)
            return total_suits

    def extract_weapon_swfs(self, loaders: List[Tuple[str, str, str]]) -> Dict[str, int]:
        """提取武器和特殊兵器的 SVG 与位图 PNG。"""
        stats: Dict[str, int] = {}
        for rel_path, label, desc in loaders:
            if label not in self.WEAPON_LABELS:
                continue

            swf_path = self.find_actual_swf(rel_path, label)
            if not swf_path:
                logger.warning("未找到武器 SWF: %s (label=%s)", rel_path, label)
                continue

            category_dir = self.img_output_dir / label
            category_dir.mkdir(parents=True, exist_ok=True)

            logger.info("正在导出武器类资源 %s (来自 %s)...", label, swf_path.name)
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir)
                exporter = FFDecExporter(output_dir=tmp_path, input_swf=swf_path)
                # 同时导出 sprite (SVG)、image (PNG) 及 symbolClass
                exporter.export(
                    export_types=["symbolClass", "sprite", "image"],
                    formats="sprite:svg",
                )

                symbols = self._read_symbols(tmp_path)
                count = 0

                # 1. 收集带有类名的 sprite SVG (递归查找 DefineSprite_*)
                sprite_dirs = [p for p in tmp_path.rglob("DefineSprite_*") if p.is_dir()]
                for sdir in sprite_dirs:
                    parts = sdir.name.split("_", 2)
                    if len(parts) < 3:
                        continue
                    class_name = parts[2]
                    svg_file = sdir / "1.svg"
                    if svg_file.exists():
                        dest_file = category_dir / f"{class_name}.svg"
                        dest_file.write_bytes(svg_file.read_bytes())
                        count += 1

                # 2. 收集带有符号映射的图像 (PNG)
                for img_file in tmp_path.rglob("*.png"):
                    clean_name = None
                    if "_" in img_file.stem:
                        parts = img_file.stem.split("_", 1)
                        clean_name = parts[1]
                    else:
                        cid = img_file.stem
                        if cid in symbols:
                            clean_name = symbols[cid]

                    if clean_name:
                        # 过滤掉通用无名图片，只保留有意义的类名
                        if clean_name.endswith("Bmp"):
                            clean_name = clean_name[:-3]
                        dest_file = category_dir / f"{clean_name}.png"
                        dest_file.write_bytes(img_file.read_bytes())
                        count += 1

                logger.info("  ✓ %s 完成导出: %d 个资源 (SVG/PNG)", label, count)
                stats[label] = count

    def extract_ui_system_icons(self, custom_dest_dir: Optional[Path] = None) -> int:
        """从 BasicUI 与图标库中提取前端/客户端系统通用图标与品质底框 (如 D:\\bqyx\\rs\\assets\\icons)。
        包括:
          - 根目录 SVG (achieve, active, arms, ask, blackMarket, head, pay, thingsBag)
          - arms/lock.png
          - back/arm_*.png (10 种品质底框)
          - back/equip_*.png (10 种品质底框)
          - stars/str_*.png (10 档强化星级图)
        """
        dest_dir = custom_dest_dir or (self.output_assets_dir / "icons")
        dest_dir.mkdir(parents=True, exist_ok=True)

        basic_ui_swf = self.find_actual_swf("swf/UI/BasicUI368.swf", "BasicUI")
        if not basic_ui_swf:
            logger.warning("未找到 BasicUI SWF，跳过通用系统底框与星级提取")
            return 0

        logger.info("正在提取系统通用图标、品质底框与强化星级 (来自 %s)...", basic_ui_swf.name)
        count = 0
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            exporter = FFDecExporter(output_dir=tmp_path, input_swf=basic_ui_swf)
            # 410: lockBmp, 383: equip back frames, 822: arm back frames, 397: star frames
            exporter.export(
                export_types=["sprite", "image"],
                formats="sprite:png",
                select_id="410,383,822,397",
            )

            # 1. arms/lock.png
            arms_dir = dest_dir / "arms"
            arms_dir.mkdir(parents=True, exist_ok=True)
            lock_files = list(tmp_path.rglob("*410*.png"))
            if lock_files:
                (arms_dir / "lock.png").write_bytes(lock_files[0].read_bytes())
                count += 1

            # 2. stars/str_*.png (DefineSprite_397 -> str_5.png ... str_50.png)
            stars_dir = dest_dir / "stars"
            stars_dir.mkdir(parents=True, exist_ok=True)
            d397_list = list(tmp_path.rglob("DefineSprite_397"))
            if d397_list:
                d397 = d397_list[0]
                for i in range(1, 11):
                    src = d397 / f"{i}.png"
                    if src.exists():
                        (stars_dir / f"str_{i * 5}.png").write_bytes(src.read_bytes())
                        count += 1

            # 3. back/equip_*.png 与 back/arm_*.png
            back_dir = dest_dir / "back"
            back_dir.mkdir(parents=True, exist_ok=True)
            colors = [
                "white", "green", "blue", "purple", "orange",
                "red", "black", "darkgold", "purgold", "yagold",
            ]

            d383_list = list(tmp_path.rglob("DefineSprite_383"))
            if d383_list:
                d383 = d383_list[0]
                for idx, color in enumerate(colors, start=1):
                    src = d383 / f"{idx}.png"
                    if src.exists():
                        (back_dir / f"equip_{color}.png").write_bytes(src.read_bytes())
                        count += 1

            d822_list = list(tmp_path.rglob("DefineSprite_822"))
            if d822_list:
                d822 = d822_list[0]
                for idx, color in enumerate(colors, start=1):
                    src = d822 / f"{idx}.png"
                    if src.exists():
                        (back_dir / f"arm_{color}.png").write_bytes(src.read_bytes())
                        count += 1

        # 4. 根目录导航 SVG
        svg_mapping = {
            "achieve.svg": self.img_output_dir / "IconGather" / "achieve.svg",
            "active.svg": self.img_output_dir / "IconGather" / "dailySign.svg",
            "arms.svg": self.img_output_dir / "ThingsIcon" / "arms.svg",
            "ask.svg": self.img_output_dir / "IconGather" / "ask.svg",
            "blackMarket.svg": self.img_output_dir / "IconGather" / "blackMarket.svg",
            "head.svg": self.img_output_dir / "IconGather" / "head.svg",
            "pay.svg": self.img_output_dir / "IconGather" / "pay.svg",
            "thingsBag.svg": self.img_output_dir / "IconGather" / "wear.svg",
        }

        for name, src in svg_mapping.items():
            if src.exists():
                (dest_dir / name).write_bytes(src.read_bytes())
                count += 1
            else:
                logger.warning("未找到源 SVG: %s，无法导出 %s", src, name)

        logger.info("  ✓ 系统通用图标提取完成: %d 个文件已保存至 %s", count, dest_dir)
        return count

    def run(self, sync_to_rs_icons: bool = True) -> Dict[str, any]:
        """一键全自动执行完整导出流程。"""
        logger.info("==========================================")
        logger.info("开始执行源码驱动的 SWF 图片资源全自动提取")
        logger.info("  版本: %s", self.version)
        logger.info("  SWF 资源目录: %s", self.swf_dir)
        logger.info("  AS3 源码目录: %s", self.scripts_dir)
        logger.info("  目标输出目录: %s", self.output_assets_dir)
        logger.info("==========================================")

        # 1. 清理旧的 images
        self.clean_old_images()

        # 2. 从源码 Gaming.as 中解析出 SWFLoader 列表
        loaders = self.as3_parser.extract_swf_loaders(self.scripts_dir)
        if not loaders:
            raise RuntimeError(f"未能从 {self.scripts_dir / 'Gaming.as'} 提取到 SWFLoader 配置")
        logger.info("从 Gaming.as 成功解析出 %d 个 SWF 模块配置", len(loaders))

        # 3. 提取所有标准图标 SWF
        icon_stats = self.extract_icon_swfs(loaders)

        # 4. 提取装备汇总包 (equipGather)
        suit_count = self.extract_equip_gather()

        # 5. 提取枪械/兵器类 SWF
        weapon_stats = self.extract_weapon_swfs(loaders)

        # 6. 提取系统通用图标、品质底框与星级 (icons 目录)
        ui_icon_count = self.extract_ui_system_icons()

        # 可选同步至 D:\bqyx\rs\assets\icons
        if sync_to_rs_icons:
            rs_icons_path = Path("D:/bqyx/rs/assets/icons")
            if rs_icons_path.parent.exists():
                logger.info("正在同步系统图标至 %s...", rs_icons_path)
                self.extract_ui_system_icons(custom_dest_dir=rs_icons_path)

        logger.info("==========================================")
        logger.info("SWF 资源全部提取完成！")
        logger.info("资源已保存到: %s", self.output_assets_dir)
        logger.info("==========================================")

        return {
            "icons": icon_stats,
            "equip_suits": suit_count,
            "weapons": weapon_stats,
            "ui_system_icons": ui_icon_count,
        }

