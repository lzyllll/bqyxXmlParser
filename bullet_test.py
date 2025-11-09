

from pathlib import Path
from typing import Any, Dict
from utils import attrib_factory
from utils.json.save_json import save_to_json
from utils.parser.tag.abstract import ElementParser
import xml.etree.ElementTree as ET

from utils.xml_parse import direct_parse_xml, get_default_attrib_registr, get_default_factory, parse_element

class BulletFatherParser(ElementParser):
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
            if element.find('bullet') is not None:
                return True
        return False
        
    def parse(self, element: ET.Element) -> Dict[str, Any]:
        result = {}
        # 解析属性
        self.attrib_registr.parse(element, result)
        # 按标签分组处理子元素
        # {name:{武器数据}}
        result['bullet'] = {}
        for bullet in element:
            bullet_dict = self.factory.parse_element(bullet)
            #添加类别属性
            bullet_dict['armsType'] = element.get('type')
            #主键
            name = bullet_dict.get('name')
            result['bullet'][name] = bullet_dict

        return result


class EndWithUrlParser(ElementParser):
    '''针对以url结尾的  只要text bullet/gaiaFit
    <bulletImgUrl raNum="30" con="filter">bullet/gaiaFit</bulletImgUrl>
    '''
    def can_parse(self, element: ET.Element) -> Any:
        if element.tag.endswith('Url'):
            return True
        return False
    def parse(self, element: ET.Element) -> Any:
        return element.text
    

# attrib_factory = get_default_attrib_registr()

factory = get_default_factory()
factory.register_parser(BulletFatherParser(),100)
factory.register_parser(EndWithUrlParser(),110)


if __name__ == '__main__':
    # XML文件夹路径
    xml_dir = Path(r'C:\Users\lzy\Desktop\dev-bqyx\python\py_bq_xml_to_json\3521_xml')
        
    # walk
    for root_dir, dirs, files in xml_dir.walk():
        for file in files:
            xml_path = root_dir / file
            root = direct_parse_xml(xml_path)
            ele_dict = parse_element(root, element_factory=factory)
            # 保存为JSON文件
            json_path = save_to_json(
                ele_dict, 
                xml_path,
                Path('output') / 'bullet'
            )
