"""类型转换"""

def subject_type_to_emoji(type_: int) -> str:
    """将subject_type转emoji"""
    if type_ == 1:
        return "📚"
    elif type_ == 2:
        return "🌸"
    elif type_ == 3:
        return "🎵"
    elif type_ == 4:
        return "🎮"
    elif type_ == 6:
        return "📺"


def number_to_week(num: int) -> str:
    """将week day转换成星期"""
    if num == 1:
        return "星期一"
    if num == 2:
        return "星期二"
    if num == 3:
        return "星期三"
    if num == 4:
        return "星期四"
    if num == 5:
        return "星期五"
    if num == 6:
        return "星期六"
    if num == 7:
        return "星期日"
    else:
        return "未知"


def parse_markdown_v2(text: str) -> str:
    """markdown_v2 转译"""
    return text.translate(str.maketrans(
        {'_': '\\_',
         '*': '\\*',
         '[': '\\[',
         ']': '\\]',
         '(': '\\(',
         ')': '\\)',
         '~': '\\~',
         '`': '\\`',
         '>': '\\>',
         '#': '\\#',
         '+': '\\+',
         '-': '\\-',
         '=': '\\=',
         '|': '\\|',
         '{': '\\{',
         '}': '\\}',
         '.': '\\.',
         '!': '\\!'}))


def remove_duplicate_newlines(text: str) -> str:
    """删除重行 够用就行 懒的搞正则"""
    return text.translate(str.maketrans({'\n\n': '\n', '\n\n\n': '\n'}))
