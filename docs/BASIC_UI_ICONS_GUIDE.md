# BasicUI 系统通用图标与品质底框维护指南

## 1. 说明

游戏系统通用图标（武器/装备品质底框、强化星级、锁定图标、导航入口等）已固化在仓库根目录 **`resources/icons/`** 中。

- **为什么手动维护**：`BasicUI*.swf` 在游戏版本更新重新编译时，内部元件的 Character ID 会发生偏移（例如武器底框在 v3680 为 822，在 v3690 为 824）。但这些底框素材运营多年极少改动，因此日常解析直接复制 `resources/icons/` 目录，无需反编译 SWF。
- **何时需要更新**：仅在游戏真正更换底框美术设计，或新增品质等级时，才需要手动从新版 `BasicUI*.swf` 中重新导出并替换。

---

## 2. 目录规范 (`resources/icons/`)

```text
resources/icons/
├── arms/lock.png                     # 锁定角标 (12x12)
├── back/
│   ├── arm_white.png ~ yagold.png    # 武器长方形品质底框 (173x69，共 10 种品质)
│   └── equip_white.png ~ yagold.png  # 装备正方形品质底框 (56x56，共 10 种品质)
├── stars/str_5.png ~ str_50.png      # 强化星级 (46x10，共 10 档)
└── achieve.png, active.png...        # 根目录系统导航图标
```

品质底色文件名与帧号对应关系（1~10 帧）：
`white`(白), `green`(绿), `blue`(蓝), `purple`(紫), `orange`(橙), `red`(红), `black`(黑), `darkgold`(暗金), `purgold`(紫金), `yagold`(极品金)。

---

## 3. 手动查找元件 ID (FFDec)

使用 **FFDec (JPEXS Free Flash Decompiler)** 打开目标版本的 `BasicUI*.swf`：

1. **武器品质底框 (`arm_*.png`)**：
   - 在左侧展开 `sprites`，搜索并打开 `armsGrip`（如 `DefineSprite_845`）；
   - 在时间轴图层中选中底部的 `backMc` 元件，下方状态栏即可看到其引用的 Character ID（v3680 为 `822`，v3690 为 `824`）。
2. **装备品质底框 (`equip_*.png`)**：
   - 打开 `equipGrip`（如 `DefineSprite_451`），查看其内部 `backMc` 的 Character ID（通常为 `383`）。
3. **强化星级图 (`str_*.png`)**：
   - 查看 `armsGrip` 或 `equipGrip` 内部的 `starMc` 元件 ID（通常为 `397`）。
4. **锁定图标 (`lock.png`)**：
   - 在左侧展开 `images`，搜索 `lockBmp` 查看其 ID（通常为 `410`）。

---

## 4. 导出与替换步骤

确认 ID 后（以 410, 383, 824, 397 为例）：

1. **导出 PNG**：
   ```bash
   ffdec-cli -export sprite,image tmp_export/ -format sprite:png -selectid 410,383,824,397 swf_assets/<version>/swf/UI/BasicUI<version>.swf
   ```
2. **替换至 `resources/icons/`**：
   - 锁图标：`tmp_export/images/410_lockBmp.png` -> `resources/icons/arms/lock.png`
   - 装备底框：`tmp_export/sprites/DefineSprite_383/{1..10}.png` -> `resources/icons/back/equip_{color}.png`
   - 武器底框：`tmp_export/sprites/DefineSprite_824/{1..10}.png` -> `resources/icons/back/arm_{color}.png`
   - 强化星级：`tmp_export/sprites/DefineSprite_397/{1..10}.png` -> `resources/icons/stars/str_{5..50}.png`
3. **提交推送**：
   ```bash
   git add resources/icons/
   git commit -m "chore: 手动更新基础UI品质底框与图标素材"
   git push origin main
   ```
