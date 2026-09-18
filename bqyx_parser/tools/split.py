

def clean_split_text(raw_text: str, delimiter: str = ',') -> list[str]:
    """
    将原始文本按分隔符切割，并清理每个元素的空白字符，
    同时过滤掉因换行、缩进导致的空字符串。


    例：专门解决这样的，防止出现换行、制表符
    standStop,...die2
    ,__fill1_Up,...
    """
    if not raw_text:
        return []
    # split 后逐项 strip，并过滤掉空串
    return [item.strip() for item in raw_text.split(delimiter) if item.strip()]