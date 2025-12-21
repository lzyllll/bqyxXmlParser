from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from bqyx_parser.config.persistent_state import load_last_version

import json
from bqyx_parser.parser.xml_to_json import parser_xml_root, parse_element




version = load_last_version() # v3xxx

#关卡掉落的
common_suit = Path('output',version,'xml' ,'other' ,'equipImageClass.xml')
#黑色
black_suit = Path('output',version,'xml','other','blackEquipClass.xml')
#暗金
darkgold_suit = Path('output' ,version ,'xml' ,'other' ,'darkgoldEquipClass.xml')

suit_output_dir = Path("output",version,"json",'equip')
suit_output_file = suit_output_dir / 'suit.json'
equip_output_file = suit_output_dir / 'equip.json'
''
suit_output_dir.mkdir(parents=True,exist_ok=True)
def parse_suitPro(suit_attr_str:str):
    attr_dict = {}
    attrs = suit_attr_str.split(',')
    for attr in attrs:
        # 可能为hurtAll:1.15 也可能为 hurtAll_1.15
    
        key,value = attr.split(':') if ':' in attr else attr.split('_')
        attr_dict[key] = float(value)
    return attr_dict


black_xml = parser_xml_root(black_suit)
common_xml = parser_xml_root(common_suit)
dargold_xml = parser_xml_root(darkgold_suit)

#套装加成逻辑

#套装统计
suit_result = {}
#对照表
equip_result = {}
for xml in [black_xml,common_xml,dargold_xml]:
    fathers = xml.findall('.//father')
    for father in fathers: 
        if father.get('suitPro'):
            suit_result[father.get('name')] = {
                 "RoleBonus":parse_suitPro(father.get('suitPro')),
                 "cnName":father.get("cnName")
                }
        range = father.getparent().attrib.get('range')
 
        #拼装 例：madmor _ pants 作为主键
        for image in father.findall('image'):
            name = father.get('name') + '_' + image.find('type').text
            equip_result[name] = parse_element(image)
            if range:
                 #开始等级，最大等级1，最大等级2，结束等级
                 start,mx1,mx2,end = list(map(int,range.split(',')))
                 equip_result[name]['level'] = {}
                 equip_result[name]['level']['startLv'] = start
                 equip_result[name]['level']['maxLv1'] = mx1
                 equip_result[name]['level']['maxLv2'] = mx2
                 equip_result[name]['level']['endLv'] = end
# 装备四件，衣服，裤，腰带，头盔 的中英文对照表



with open(suit_output_file ,'w', encoding='utf-8') as f:
        json.dump(suit_result, f, ensure_ascii=False, indent=2)


with open(equip_output_file ,'w', encoding='utf-8') as f:
        json.dump(equip_result, f, ensure_ascii=False, indent=2)
    