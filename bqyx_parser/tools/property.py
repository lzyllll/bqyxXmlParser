from pathlib import Path
from lxml import etree as ET

def parse_property(xml_path: Path) -> list:
    """
    读取XML文件，返回属性字典列表，每个字典包含所有XML属性和dataArr
    例如
    <pro name="strengthen" cnName="强化" unit="" fixedNum="0">
        100%
        40%
        30%
    </pro>
    
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    result = []
    for pro_node in root.findall(".//pro"):  # 递归查找所有<pro>
        # 1. 复制所有XML属性（如 name, cnName, unit 等）
        item = dict(pro_node.attrib)
        # 强制int属性
        for int_attr in ["fixedNum",'maxLv']:
            if int_attr in item:
                try:
                    item[int_attr] = int(item[int_attr])
                except ValueError:
                    item[int_attr] = 0  # 如果无法转换为整数，设置为0
        # 2. 解析文本内容（多行数值）
        data_arr = []
        raw_text = pro_node.text or ""
        for line in raw_text.splitlines():
            line = line.strip()
            if not line:
                continue
            # 去除末尾的 %（如果有）
            if line.endswith("%"):
                line = line[:-1]
            try:
                # 转为浮点数（如果全是整数，可以改为 int）
                val = float(line)
                if val.is_integer():
                    data_arr.append(int(val))
                else:
                    data_arr.append(val)
            except ValueError:
                pass  # 忽略非数字行
        item["dataArr"] = data_arr
        
        result.append(item)

    return result