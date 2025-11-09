import json
from pathlib import Path


def save_to_json(data: dict, xml_path: Path, output_dir: str = 'output') -> Path:
    """
    将解析后的数据保存为JSON文件，可解决重名
    
    Args:
        data: 要保存的字典数据
        xml_path: 原始XML文件路径（用于生成JSON文件名）
        output_dir: 输出目录，默认为'output'
    
    Returns:
        保存的JSON文件路径
    """
    # 创建output目录
    output_path = Path(output_dir)
    
    # 生成JSON文件名（使用XML文件名，但改为.json扩展名）
    json_filename = xml_path.stem + '.json'
    json_path = output_path / json_filename
    
    # 如果文件已存在，添加数字后缀
    if json_path.exists():
        base_name = xml_path.stem
        counter = 1
        while json_path.exists():
            json_filename = f'{base_name}_{counter}.json'
            json_path = output_path / json_filename
            counter += 1
        print(f'文件重名，已重命名为: {json_path.name}')
    
    # 写入JSON文件
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return json_path