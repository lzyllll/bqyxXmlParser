


GIFT_KEYS = ['type', 'name', 'num', 'color', 'lv', 'childType', 'numExtra', 'tipB', 'dropName', 'pro', 'sp']

# 整数属性
INT_ATTRS = {'unlockLv', 'achieveDiff'}


def parse_gift_string(gift_str):
    """解析 <gift> 标签内的分号分隔字符串，返回字典或 None"""
    if not gift_str or not gift_str.strip():
        return None

    parts = gift_str.strip().split(';')
    gift_obj = {}

    for i, prop_name in enumerate(GIFT_KEYS):
        if i >= len(parts):
            break
        value_str = parts[i].strip()
        if not value_str:
            continue

        if prop_name == 'tipB':
            gift_obj[prop_name] = value_str.lower() in ('true', '1')
        elif prop_name in ('num', 'pro', 'sp', 'lv'):
            try:
                gift_obj[prop_name] = float(value_str) if '.' in value_str else int(value_str)
            except ValueError:
                gift_obj[prop_name] = value_str
        else:
            gift_obj[prop_name] = value_str

    return gift_obj if gift_obj else None

