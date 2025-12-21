import sys
sys.path.append(str(Path(__file__).parent.parent))
from pathlib import Path

from bqyx_parser.config.persistent_state import load_last_version


from pathlib import Path
from typing import Any, Dict
import shutil
from bqyx_parser.json.save_json import save_to_json
from bqyx_parser.parser.element.abstract import ElementParser
import xml.etree.ElementTree as ET

from bqyx_parser.parser.xml_to_json import parser_xml_root, get_default_factory, parse_element

class targetParser(ElementParser):
    def can_parse(self, element):
        return element.tag == 'target'
    def parse(self, element):
        # <target>me,range,enemy</target>
        return element.text.split(',')
    
class GrowthParser(ElementParser):
    def can_parse(self, element):
        return element.tag == 'growth'
    def parse(self, element):
        result = [] 
        # 把这里的skill，看成是列表，而不是字典
        # 因为他没有name什么的
        # 和father的skill解析不同,例如，无疆之章
        for skill in element:
            skill_obj = self.factory.parse_element(skill)
            if skill_obj !=None:
                result.append(skill_obj)
        return result
    
class SkillFatherParser(ElementParser):
    def can_parse(self, element: ET.Element) -> bool:
        '''
        有没有子元素bullet,
        必定为
     
            <bullet/><bullet/>
            ....多个bullet

        '''

        # 字典的模式
        # father不能为growth
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
        for skill in element:
            skill_dict = self.factory.parse_element(skill)

            #主键
            #bullet的name
        
            name = skill_dict.get('name')
            #father的cnName
            father_cn_name = element.get('cnName')
            father_name = element.get('name')
            
            # wiki的特判  但我现在用的是分类好的，没有father的cnName没用了
            # if father_name == "godArmsSkill":
            #     if father_cn_name == "神级武器技能-参加随机":
            #         name = "randomGodArmsSkill"
            #         result['name'] = name
            result['skills'][name] = skill_dict
        return result



factory = get_default_factory()
factory.register_parser(targetParser(),120)
factory.register_parser(GrowthParser(),110)
factory.register_parser(SkillFatherParser(),100)


 
if __name__ == '__main__':
    # XML文件夹路径
    version = load_last_version()
    xml_dir = Path('output',version,'xml','father','skill')
    output_dir = Path('output')/ version / 'json' / 'skills'
    # 清理输出目录
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # # walk
    for root_dir, dirs, files in xml_dir.walk():
        for file in files:
            xml_path = root_dir / file
            root = parser_xml_root(xml_path)
            try:
                ele_dict = parse_element(root, element_factory=factory)
            except Exception as e:
                print(xml_path,e)
                continue
            json_path = save_to_json(
                ele_dict, 
                xml_path,
                output_dir
            )
    print(f'skill生成json完毕{output_dir}')