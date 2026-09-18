# 模块解析计划

XML 目录：`compiled/v3671/xml`  
对照资源：`D:\bqyx\rs\resource`

| 模块 | 状态 | 脚本 | XML | 输出 JSON |
| --- | --- | --- | --- | --- |
| achieve | 已完成 | `achieve/achieve.py`<br>`achieve/medel.py` | `achieve.xml`<br>`medelProperty.xml` | `achieve/achieveClass.json`<br>`achieve/achieveFatherClass.json`<br>`achieve/medelPropertyClass.json` |
| things | 已完成 | `things/things.py`<br>`things/item_strengthen.py`<br>`things/chip.py` | `things.xml`<br>`things90.xml`<br>`parts.xml`<br>`chip.xml`<br>`itemsStrengthen.xml` | `things/thingsClass.json`<br>`things/things90Class.json`<br>`things/partsClass.json`<br>`things/chipClass.json`<br>`things/strengthen/itemsStrengthenData.json`<br>`things/blackArmsChip.json`<br>`things/blackEquipChip.json`<br>`things/rareArmsChip.json` |
| union | 已完成 | `union/military.py`<br>`union/unionBattle.py`<br>`union/unionBuilding.py`<br>`union/unionBuildingProperty.py`<br>`union/unionData.py`<br>`union/unionTask.py` | `military.xml`<br>`unionBattle.xml`<br>`unionBuilding.xml`<br>`unionBuildingProperty.xml`<br>`unionData.xml`<br>`unionTask.xml` | `union/military.json`<br>`union/unionBattle.json`<br>`union/unionBuilding.json`<br>`union/unionBuildingProperty.json`<br>`union/unionData.json`<br>`union/unionTask.json` |
| top | 已完成 | `top.py` | `top.xml` | `topClass.json` |
| active | 待做 | `active/active.py` | `active.xml` | `active/activeClass.json` |
| arms | 待做 | `arms/arms.py`<br>`arms/armsCharger.py`<br>`arms/armsName.py` | 武器多文件（现挂 `rifle.xml`）<br>`armsCharger.xml`<br>`armsName.xml` | `arms/armsClass.json`<br>`arms/armsChargerClass.json`<br>`arms/armsName.json` |
| armsSkill | 待做 | `armsSkill.py` | `armsSkill.xml` | `armsSkillClass.json` |
| ask | 待做 | `ask/lifeAsk.py`<br>`ask/otherAsk.py`<br>`ask/extraAsk.py` | `lifeAsk.xml`<br>`otherAsk.xml`<br>`extraAsk.xml`（不存在，内容在 `lifeAsk.xml`） | `ask/lifeAskClass.json`<br>`ask/otherAskClass.json`<br>`ask/extraAskClass.json` |
| blackMarket | 待做 | `blackMarket/blackMarket.py`<br>`blackMarket/blackMarketPrice.py`<br>`blackMarket/blackMarketThings.py` | `blackMarket.xml`<br>`blackMarketPrice.xml`<br>`blackMarketThings.xml` | `blackMarket/blackMarketClass.json`<br>`blackMarket/blackMarketPrice.json`<br>`blackMarket/blackMarketThings.json` |
| body | 待做 | `body/hero.py`<br>`body/normal.py` | `hero.xml`<br>怪物多文件（现挂 `normal.xml`） | `body/hero.json`<br>`body/normal.json` |
| drop | 已完成 | `drop/dropColor.py` | `dropColor.xml` | `drop/dropColor.json` |
| equip | 已完成 | `equip/blackEquip.py`<br>`equip/darkgoldEquip.py`<br>`equip/equipImage.py`<br>`equip/equipRange.py`<br>`equip/fashion.py`<br>`equip/suitProperty.py`<br>`equip/device/device.py`<br>`equip/jewelry/jewelry.py`<br>`equip/shield/shield.py`<br>`equip/vehicle/vehicle.py`<br>`equip/vehicle/vehicleProperty.py`<br>`equip/weapon/weapon.py` | `blackEquip.xml`<br>`darkgoldEquip.xml`<br>`equipImage.xml`<br>`equipRange.xml`<br>`fashion.xml`<br>`suitProperty.xml`<br>`device.xml`<br>`jewelry.xml`<br>`shield.xml`<br>`vehicle.xml`<br>`vehicleProperty.xml`<br>`weapon.xml` | `equip/blackEquip.json`<br>`equip/darkgoldEquip.json`<br>`equip/equipImage.json`<br>`equip/equipRangeClass.json`<br>`equip/fashionData.json`<br>`equip/suitPropertyClass.json`<br>`equip/device/deviceData.json`<br>`equip/jewelry/jewelryData.json`<br>`equip/shield/shieldData.json`<br>`equip/vehicle/vehicleData.json`<br>`equip/vehicle/vehicleProperty.json`<br>`equip/weapon/weaponData.json` |
| head | 待做 | `head/head.py`<br>`head/headHonor.py` | `head.xml`<br>`headHonor.xml` | `head/headData.json`<br>`head/headHonor.json` |
| parts | 待做 | `parts/partsProperty.py`<br>`parts/partsRarePro.py` | `partsProperty.xml`<br>`partsRarePro.xml` | `parts/partsProperty.json`<br>`parts/partsRarePro.json` |
| pay | 待做 | `pay/pay.py` | `goods.xml`（另有 `otherGoods.xml`） | `pay/payData.json` |
| peak | 待做 | `peak/peakPro.py`<br>`peak/craftPro.py` | `peakPro.xml`<br>`craftPro.xml`（不存在） | `peak/peakPro.json`<br>`peak/craftPro.json` |
| pet | 待做 | `pet/petStrengthen.py` | `petStrengthen.xml` | `pet/petStrengthen.json` |
| post | 待做 | `post/post.py`<br>`post/postPro.py` | `post.xml`<br>`postData.xml` | `post/postData.json`<br>`post/postPro.json` |
| skin | 待做 | `skin/armsSkin.py` | `armsSkin.xml` | `skin/armsSkin.json` |
| vip | 待做 | `vip/vip.py` | `vip.xml` | `vip/vipLevel.json` |
| worldMap | 已完成 | `worldMap/worldMap.py` | `worldMap.xml`<br>`bossMatchList.xml`<br>关卡族 XML（Boss 解析）<br>`demonSkill.xml`（词缀翻译） | `worldMap/worldMap.json` |

备注：

- `things` 模块已包含 `blackArmsChip.json`、`blackEquipChip.json`、`rareArmsChip.json` 的生成（基于 `thingsDefineGroup.ts`，由 `things/chip.py` 处理）。
- `worldMap` 模块已彻底统一为单一真实源：由 `worldMap.py` 一站式解析关卡 Boss（含 `<fixed target>` 递归继承）与修罗词缀中英文，直接输出自洽的 `worldMap.json`，外部冗余的 `lastLevelName.json`、`lastLevelBoss.json` 与 `skillCn.json` 已全部删除，`bqyx_api` 也已直接改为加载单一 `worldMap.json`。
- 状态「已完成」指自定义解析已写好；「待做」目前只是默认 factory 骨架。



需要用到的json文件，目前ts做的存档解析
loaded json files:

  achieve/achieveClass.json
  achieve/achieveFatherClass.json
  achieve/medelPropertyClass.json

  things/chipClass.json
  things/partsClass.json
  things/strengthen/itemsStrengthenData.json
  things/things90Class.json
  things/thingsClass.json

  union/military.json
  union/unionBattle.json
  union/unionBuilding.json
  union/unionBuildingProperty.json
  union/unionData.json
  union/unionTask.json
  vip/vipLevel.json

  arms/armsChargerClass.json
  arms/armsClass.json
  arms/armsName.json

  active/activeClass.json
  ask/extraAskClass.json
  ask/lifeAskClass.json
  ask/otherAskClass.json
  blackMarket/blackMarketClass.json
  blackMarket/blackMarketPrice.json
  blackMarket/blackMarketThings.json
  body/hero.json
  body/normal.json
  drop/dropColor.json
  equip/blackEquip.json
  equip/darkgoldEquip.json
  equip/device/deviceData.json
  equip/equipImage.json
  equip/equipRangeClass.json
  equip/fashionData.json
  equip/jewelry/jewelryData.json
  equip/shield/shieldData.json
  equip/suitPropertyClass.json
  equip/vehicle/vehicleData.json
  equip/vehicle/vehicleProperty.json
  equip/weapon/weaponData.json
  head/headData.json
  head/headHonor.json
  parts/partsProperty.json
  parts/partsRarePro.json
  pay/payData.json
  peak/craftPro.json
  peak/peakPro.json
  pet/petStrengthen.json
  post/postData.json
  post/postPro.json
  skin/armsSkin.json

