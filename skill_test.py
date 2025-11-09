
from pathlib import Path
from typing import Any, Dict
import shutil
from utils import attrib_factory
from utils.json.save_json import save_to_json
from utils.parser.tag.abstract import ElementParser
import xml.etree.ElementTree as ET

from utils.xml_parse import direct_parse_xml, get_default_attrib_registr, get_default_factory, parse_element



class SkillFatherParser(ElementParser):
    def can_parse(self, element: ET.Element) -> bool:
        '''
        看看father有没有子元素bullet,
        必定为
        <father>
            <bullet/><bullet/>
            ....多个bullet
        <father>
        '''
        if element.tag == 'father':
            if element.find('skill') is not None:
                return True
        return False
        
    def parse(self, element: ET.Element) -> Dict[str, Any]:
        result = {} 
        # 解析属性
        self.attrib_registr.parse(element, result)
        # 按标签分组处理子元素
        # {name:{武器数据}}
        result['skills'] = {}
        for bullet in element:
            bullet_dict = self.factory.parse_element(bullet)
            #主键
            #bullet的name
            name = bullet_dict.get('name')
            #father的cnName
            father_cn_name = element.get('cnName')
            father_name = element.get('name')
            
            # wiki的特判
            if father_name == "godArmsSkill":
                if father_cn_name == "神级武器技能-参加随机":
                    name = "randomGodArmsSkill"
                    result['name'] = name
            result['skills'][name] = bullet_dict
        return result

class GrowthObjParser(ElementParser):
    def can_parse(self, element: ET.Element) -> bool:
        if element.tag == 'obj' and element.text:
            return True
        return False
    def parse(self, element: ET.Element) -> Any:
        '''
        <obj>"pro":0.35</obj>
        特殊处理"pro":0.35 -> 转为{"pro":0.35 }
        <obj>"name":"hurtMineBullet","site":"meMid","minYB":true</obj>
        '''
        text_value = element.text
        # 特殊处理"pro":0.35 -> 转为{"pro":0.35 }
        json_text = text_value if text_value.startswith('{') else f"{{{text_value}}}"
        return self.save_eval(json_text)

factory = get_default_factory()
factory.register_parser(SkillFatherParser(),100)
factory.register_parser(GrowthObjParser(),110)

 
if __name__ == '__main__':
    # XML文件夹路径
    xml_dir = Path(r'C:\Users\lzy\Desktop\dev-bqyx\python\py_bq_xml_to_json\3521_xml')
    output_dir = Path('output') / 'skills'
    # 清理输出目录
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # walk
    for root_dir, dirs, files in xml_dir.walk():
        for file in files:
            xml_path = root_dir / file
            root = direct_parse_xml(xml_path)
            ele_dict = parse_element(root, element_factory=factory)
            json_path = save_to_json(
                ele_dict, 
                xml_path,
                output_dir
            )
