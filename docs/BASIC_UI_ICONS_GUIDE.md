# BasicUI 系统通用图标与品质底框查找与维护指南

## 1. 背景与架构决策

### 1.1 为什么采用静态固化目录 (`resources/icons`)？
在早期版本中，系统通用图标（武器/装备品质底色、强化星级、背包锁图标、主导航图标等）是通过调用 FFDec 命令行，实时从 `BasicUI*.swf` 中反编译提取出来的。

然而，Flash 编译器在每次游戏版本编译发布时，会对未显式绑定的内部 MovieClip 元件自动重新分配递增 ID（Character ID）。例如：
- 在 `BasicUI368.swf` (v3680) 中，武器品质底框的 Character ID 为 `822` (`DefineSprite_822`)；
- 在 `BasicUI369.swf` (v3690) 中，由于前端界面新增了其他元件，武器品质底框被重新分配为 `824` (`DefineSprite_824`)。

如果每次都在提取代码中硬编码 Character ID，游戏版本更新后就会因为 ID 偏移导致素材漏提或提取错误。

**核心决策：**
这些系统 UI 底框与通用图标属于游戏底层最稳定的基石素材（10 种品质底色、强化星级指示器、锁图标、导航入口等，运营多年从未变动）。
因此，我们将这套标准的完整素材（共 40 个 PNG 文件）单独固化存放在仓库的 **`resources/icons/`** 文件夹中并纳入 Git 版本控制：
> [!IMPORTANT]
> **版本更新维护警示**：
> `AssetExtractor.extract_ui_system_icons` 中的 SWF 动态提取生成函数**会随游戏版本更新（SWF 重新编译）产生 Character ID 偏移，若需从新版本 SWF 重新提取生成，必须手动核对并更新代码中的对应 ID**。
> 平常日常解析中，默认优先直接使用 `resources/icons` 静态目录快速复制，以彻底规避版本更新带来的维护负担。

---

## 2. 静态图标库目录规范 (`resources/icons/`)

固化在仓库根目录 `resources/icons/` 下的文件结构如下：

```text
resources/icons/
├── arms/
│   └── lock.png                 # 装备/武器锁定角标 (12x12)
├── back/                        # 武器与装备品质底色框 (各 10 种品质)
│   ├── arm_white.png ~ yagold.png    # 武器槽位长方形品质底框 (173x69)
│   └── equip_white.png ~ yagold.png  # 装备槽位正方形品质底框 (56x56)
├── stars/                       # 强化星级显示图 (46x10)
│   └── str_5.png ~ str_50.png   # 10 档强化星级
├── achieve.png                  # 成就系统图标
├── active.png                   # 活动/签到图标
├── arms.png                     # 兵装库图标
├── ask.png                      # 问答系统图标
├── blackMarket.png              # 黑市商人图标
├── check.png                    # 复选框勾选图标
├── head.png                     # 称号/头像图标
├── pay.png                      # 充值福利图标
└── thingsBag.png                # 角色背包图标
```

品质底色文件名与帧号的对应关系（标准 10 档色系）：
| 帧号 (Frame) | 品质标识 (Color) | 对应装备底框 | 对应武器底框 |
| :---: | :---: | :---: | :---: |
| 1 | `white` | `equip_white.png` | `arm_white.png` |
| 2 | `green` | `equip_green.png` | `arm_green.png` |
| 3 | `blue` | `equip_blue.png` | `arm_blue.png` |
| 4 | `purple` | `equip_purple.png` | `arm_purple.png` |
| 5 | `orange` | `equip_orange.png` | `arm_orange.png` |
| 6 | `red` | `equip_red.png` | `arm_red.png` |
| 7 | `black` | `equip_black.png` | `arm_black.png` |
| 8 | `darkgold` | `equip_darkgold.png` | `arm_darkgold.png` |
| 9 | `purgold` | `equip_purgold.png` | `arm_purgold.png` |
| 10 | `yagold` | `equip_yagold.png` | `arm_yagold.png` |

---

## 3. 未来如何从新版本 BasicUI 中查找素材（逆向定位指南）

如果游戏未来进行了真正的大规模 UI 重构，修改了底框尺寸或风格，需要从新版本 `BasicUI*.swf` 中重新提取时，可依照以下方法快速定位。

### 3.1 符号与元件映射原理
游戏客户端的 AS3 代码中，界面元件与类名具有严谨的绑定关系：
- **`SymbolClass` (SWF Tag 76)**：
  - 类 `armsGrip`：武器槽位主容器 MovieClip。
  - 类 `equipGrip`：装备槽位主容器 MovieClip。
  - 类 `lockBmp`：背包锁定小位图。
- **`PlaceObject2` (SWF Tag 26)**：
  - `armsGrip` 内部放置了一个实例名为 **`backMc`** 的 MovieClip，这就是武器品质底框！
  - `equipGrip` 内部放置了一个实例名为 **`backMc`** 的 MovieClip，这就是装备品质底框！
  - 两者内部都放置了一个名为 **`starMc`** 的 MovieClip，这就是强化星级图！
- **`FrameLabel` (SWF Tag 43)**：
  - 武器底框与装备底框均具有 10 个命名的帧标签：`white`、`green`、`blue`、`purple`、`orange`、`red`、`black`、`darkgold`、`purgold`、`yagold`。

### 3.2 查找方法一：使用 FFDec 图形界面 (GUI) 查找
1. 启动 FFDec (JPEXS Free Flash Decompiler)，打开目标 SWF（如 `swf_assets/v3690/swf/UI/BasicUI369.swf`）。
2. 在左侧树形结构中找到 **`scripts`** -> 展开搜索 `armsGrip.as` 与 `equipGrip.as`：
   - 可以看到 `public var backMc: MovieClip;` 和 `public var starMc: MovieClip;`。
3. 在左侧展开 **`sprites`** (影片剪辑)：
   - 找到带有 `armsGrip` 类名后缀的 Sprite（如 `DefineSprite_845 (armsGrip)`）；
   - 单击该 Sprite，在右侧时间轴上展开图层，点击底部的背景图层（`backMc`），下方状态栏即可看到其引用的 Character ID（例如 `824`）；
   - 同理点击 `starMc` 图层，查看星级条的 Character ID（例如 `397`）；
   - 在 `equipGrip` 中点击 `backMc`，查看装备底框的 Character ID（例如 `383`）。
4. 在左侧展开 **`images`**：
   - 搜索 `lockBmp`，即可直接看到锁图标的 Character ID（例如 `410`）。

### 3.3 查找方法二：使用 Python 一键自动探测脚本（推荐）
在终端运行以下脚本，即可秒级直接打印出任意版本 `BasicUI*.swf` 中所有相关元件的准确 ID：

```python
import struct
import zlib
from pathlib import Path


def inspect_basic_ui_ids(swf_path: str | Path):
    data = Path(swf_path).read_bytes()
    body = zlib.decompress(data[8:]) if data[:3] == b"CWS" else data[8:]

    # 跳过 SWF Header (RECT + frameRate + frameCount)
    nbits = body[0] >> 3
    rect_bytes = (5 + 4 * nbits + 7) // 8
    idx = rect_bytes + 4

    symbols = {}
    sprites = {}

    while idx < len(body):
        t_cl = struct.unpack("<H", body[idx : idx + 2])[0]
        idx += 2
        tt, tl = t_cl >> 6, t_cl & 0x3F
        if tl == 0x3F:
            tl = struct.unpack("<I", body[idx : idx + 4])[0]
            idx += 4
        td = body[idx : idx + tl]
        idx += tl

        if tt == 0:
            break
        elif tt == 76:  # SymbolClass
            num = struct.unpack("<H", td[:2])[0]
            s_idx = 2
            for _ in range(num):
                cid = struct.unpack("<H", td[s_idx : s_idx + 2])[0]
                s_idx += 2
                end_str = td.find(b"\x00", s_idx)
                symbols[td[s_idx:end_str].decode("utf-8", errors="ignore")] = cid
                s_idx = end_str + 1
        elif tt == 39:  # DefineSprite
            sid = struct.unpack("<H", td[:2])[0]
            sprites[sid] = td[4:]

    def parse_placed(sprite_id):
        if sprite_id not in sprites:
            return {}
        s_body = sprites[sprite_id]
        s_idx, named = 0, {}
        while s_idx < len(s_body):
            t_cl = struct.unpack("<H", s_body[s_idx : s_idx + 2])[0]
            s_idx += 2
            stt, stl = t_cl >> 6, t_cl & 0x3F
            if stl == 0x3F:
                stl = struct.unpack("<I", s_body[s_idx : s_idx + 4])[0]
                s_idx += 4
            std = s_body[s_idx : s_idx + stl]
            s_idx += stl
            if stt == 26:  # PlaceObject2
                flags = std[0]
                if flags & 0x02:  # has character
                    cid = struct.unpack("<H", std[3:5])[0]
                    # 检测是否含有常见实例名
                    for target in [b"backMc", b"starMc", b"lockSp"]:
                        if target in std:
                            named[target.decode()] = cid
        return named

    arms_grip_id = symbols.get("armsGrip")
    equip_grip_id = symbols.get("equipGrip")
    lock_bmp_id = symbols.get("lockBmp")

    arms_placed = parse_placed(arms_grip_id) if arms_grip_id else {}
    equip_placed = parse_placed(equip_grip_id) if equip_grip_id else {}

    print(f"=== 分析结果: {Path(swf_path).name} ===")
    print(f"  武器品质底框 (arm_*.png): Character ID = {arms_placed.get('backMc')}")
    print(f"  装备品质底框 (equip_*.png): Character ID = {equip_placed.get('backMc')}")
    print(f"  强化星级指示器 (str_*.png): Character ID = {arms_placed.get('starMc') or equip_placed.get('starMc')}")
    print(f"  锁定图标 (lock.png): Character ID = {lock_bmp_id}")


# 使用示例：
# inspect_basic_ui_ids("swf_assets/v3690/swf/UI/BasicUI369.swf")
```

---

## 4. 重新导出与素材更新流程

若未来确认需要更新 `resources/icons` 下的这批素材：
1. 运行上述 Python 脚本或 FFDec，确认新版 SWF 中的目标 ID（假设武器底框为 `826`，装备底框为 `383`，锁为 `410`，星级为 `397`）。
2. 调用 FFDec CLI 导出目标资源：
   ```bash
   ffdec-cli -export sprite,image output_tmp/ -format sprite:png -selectid 410,383,826,397 path/to/BasicUI.swf
   ```
3. 将导出得到的图片重命名并替换到 `resources/icons/` 对应子目录中：
   - `410_lockBmp.png` -> `resources/icons/arms/lock.png`
   - `DefineSprite_383/{1..10}.png` -> `resources/icons/back/equip_{color}.png`
   - `DefineSprite_826/{1..10}.png` -> `resources/icons/back/arm_{color}.png`
   - `DefineSprite_397/{1..10}.png` -> `resources/icons/stars/str_{5..50}.png`
4. 提交并推送到 Git 仓库：
   ```bash
   git add resources/icons/
   git commit -m "chore: 更新基础 UI 系统品质底框与图标资源"
   git push origin main
   ```
5. 完成后，无论是本地还是云端服务器运行解析器，均会自动使用最新的静态素材，无需调整任何业务解析代码。

