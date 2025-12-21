# 有人不知道 开发链接 直接链这个项目，或者没有了解过uv
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
print(sys.path)
from bqyx_parser.config.persistent_state import load_last_version
from bqyx_parser.parser.element.abstract import ElementParser
from pathlib import Path
import shutil
from typing import Any, Dict
from bqyx_parser.json.save_json import save_to_json
import xml.etree.ElementTree as ET
from bqyx_parser.parser.xml_to_json import parser_xml_root, get_default_factory, parse_element
class BulletFatherParser(ElementParser):
    def can_parse(self, element: ET.Element) -> bool:
        '''
        看看father有没有子元素bullet,
        必定为
     
        <bullet/><bullet/>
        ....多个bullet
       
        '''
        
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
        # text 和 attrib.name 必有一个
        if element.tag == 'bulletImgUrl':
            return element.get('name') or element.text
        return element.text



# attrib_factory = get_default_attrib_registr()
factory = get_default_factory()
# factory.set_attrib_registr(attrib_registr)
factory.register_parser(BulletFatherParser(),100)
factory.register_parser(EndWithUrlParser(),110)
# factory.register_parser(EndWithArrParser(),120)

if __name__ == '__main__':
    # XML文件夹路径
    version = load_last_version()
    xml_dir = Path('output', version,'xml','father','bullet')
    output_dir = Path('output') / version /'json' /'bullet'
    # 清理输出目录
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    # walk
    for root_dir, dirs, files in xml_dir.walk():
        for file in files:
            xml_path = root_dir / file
            root = parser_xml_root(xml_path)
            ele_dict = parse_element(root, element_factory=factory)
            # 保存为JSON文件
            json_path = save_to_json(
                ele_dict, 
                xml_path,
                output_dir
            )
    print(f'生成的json文件在{output_dir}')
