from pathlib import Path
from lxml import etree
# from lxml_test import get_xml_root
from enum import Enum
from typing import Union
import xml.etree.ElementTree as ET
import shutil
class FatherStatus(Enum):
    """
    father元素属性状态枚举
    
    Attributes:
        BOTH_HAS: 同时具有name和type属性
        HAS_NAME: 只有name属性
        HAS_TYPE: 只有type属性  
        NO_ATTR: 没有name和type属性
    """
    BOTH_HAS = "both_has"
    HAS_NAME = "has_name"
    HAS_TYPE = "has_type"
    NO_ATTR = "no_attr"

def get_xml_root(input_file) -> ET.ElementTree:
    #保留 CDATA 注释，确保不被转义
    parser = etree.XMLParser(strip_cdata=False)
    tree = etree.parse(input_file, parser)
    root = tree.getroot()
    return root


def check_father_status(father: ET.Element) -> FatherStatus:
    """
    判断father元素的属性情况
    
    根据father元素是否具有name和type属性，返回对应的状态枚举值
    
    Args:
        father: lxml元素对象，期望是<father>标签元素
        
    Returns:
        FatherStatus: father元素的状态枚举
        
    """
    # 获取属性值，如果属性不存在则返回None
    name: Union[str, None] = father.attrib.get('name')
    type_name: Union[str, None] = father.attrib.get('type')
    
    # 判断属性组合情况
    if name is not None and type_name is not None:
        return FatherStatus.BOTH_HAS
    elif name is not None:
        return FatherStatus.HAS_NAME
    elif type_name is not None:
        return FatherStatus.HAS_TYPE
    else:
        return FatherStatus.NO_ATTR
    
def get_first_child(element:ET.Element|ET.ElementTree):
    #获取father的第一个元素，以判断这个father是用来做什么的
    return element.find('*')

def has_father(element:ET.Element):
    first_child = get_first_child(element)
    # xml中，无法使用真值测试
    # Truth-testing of elements was a source of confusion and will always return True in future versions. Use specific 'len(elem)' or 'elem is not None' test instead.
    if first_child is not None and first_child.tag == 'father':
        return True
    
def save_child_elements_to_xml(child_elements, output_path):
    """
    将子元素列表保存为XML文件
    
    Args:
        child_elements: 子元素列表
        output_path: 输出文件路径
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)  # 创建所有父目录

    if not child_elements:
        return
    new_root = etree.Element('data')
                
    # 将当所有节点添加到新根元素中
    for element in child_elements:
        new_root.append(element)
    
    # 生成XML字符串，保留CDATA
    xml_str = etree.tostring(
        new_root, 
        encoding='utf-8', 
        pretty_print=True,
        xml_declaration=True,
        
    ).decode('utf-8')
    

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(xml_str)



def ensure_dict_path(dic, keys, default_factory=list):
    """确保字典路径存在以便可以dic['abc']['abc']...任意层嵌套"""

    current = dic
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    if keys[-1] not in current:
        current[keys[-1]] = default_factory() if callable(default_factory) else default_factory
    return current[keys[-1]]

def generate_xml_files(dic, base_output_dir):
    """
    根据字典结构生成XML文件
    
    Args:
        dic: 包含分类数据的字典
        base_output_dir: 基础输出目录
    """
    base_dir = Path(base_output_dir)
    
    # 遍历father分类
    for first_child_tag, status_dict in dic.get('father', {}).items():
        
        # 处理name分类
        for name_value, child_elements in status_dict.get('name', {}).items():
            output_path = base_dir / 'father' / first_child_tag / 'name' / f"{name_value}.xml"
            save_child_elements_to_xml(child_elements, output_path)
        
        # 处理type分类  
        for type_value, child_elements in status_dict.get('type', {}).items():
            output_path = base_dir / 'father' / first_child_tag / 'type' / f"{type_value}.xml"
            save_child_elements_to_xml(child_elements, output_path)
        
        # 处理both分类
        if 'both' in status_dict:
            child_elements = status_dict['both']
            output_path = base_dir / 'father' / first_child_tag / 'both.xml'
            save_child_elements_to_xml(child_elements, output_path)
        
        # 处理no分类
        if 'no' in status_dict:
            child_elements = status_dict['no']
            output_path = base_dir / 'father' / first_child_tag / 'no.xml'
            save_child_elements_to_xml(child_elements, output_path)

def classify_xml(xml_dir:Path,output_dir:Path):
    dic = {}
    # father_cn_dic = {}
    
    for xml_file in xml_dir.iterdir():
        root = get_xml_root(xml_file)
        if has_father(root):
            fathers = root.findall('father')
            for father in fathers:
                if father is not None:
                    
                    father_status = check_father_status(father)
                    children = father.findall('*')
                    for child in children:
                        child_tag = child.tag
                   

                        if father_status == FatherStatus.HAS_NAME:
                            name = father.get('name')
                            # 中英文对照
                            # if father.get('cnName'):
                            #     if name in father_cn_dic:
                            #         print(f'{name}冲突了，从{father_cn_dic[name]}变为了{father.get('cnName')}')
                            #     father_cn_dic[name] = father.get('cnName')
                            target_list = ensure_dict_path(dic, ['father', child_tag, 'name', name], list)
                            target_list.append(child)
                            
                        elif father_status == FatherStatus.HAS_TYPE:
                            type_name = father.get('type')
                            target_list = ensure_dict_path(dic, ['father', child_tag, 'type', type_name], list)
                            target_list.append(child)
                            
                        elif father_status == FatherStatus.BOTH_HAS:
                            # father的name 和
                            #优先以name存储 
                            name = father.get('name')
                        
                            # if father.get('cnName'):
                            #     if name in father_cn_dic:
                            #         print(f'{name}冲突了，从{father_cn_dic[name]}变为了{father.get('cnName')}')
                            #     father_cn_dic[name] = father.get('cnName')
                            type_name = father.get('type')
                            target_list = ensure_dict_path(dic, ['father', child_tag, 'name', name], list)
                            target_list.append(child)
                            
                        else:  # NO_ATTR
                            target_list = ensure_dict_path(dic, ['father', child_tag, 'no'], list)
                        target_list.append(child)
        else:
            other_dir = Path(output_dir) / 'other'
            other_dir.mkdir(exist_ok=True, parents=True)
            shutil.copy2(xml_file, other_dir / xml_file.name)
    generate_xml_files(dic,output_dir)