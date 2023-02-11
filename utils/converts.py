"""类型转换"""
from collections import defaultdict
from typing import Literal, List

import telebot.types


def subject_type_to_emoji(type_: Literal[1, 2, 3, 4, 6]) -> str:
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
    return text.translate(
        str.maketrans(
            {
                '_': '\\_',
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
                '!': '\\!',
            }
        )
    )


def number_to_episode_type(type_: Literal[0, 1, 2, 3]) -> str:
    if type_ == 0:
        return "ep"
    if type_ == 1:
        return "sp"
    if type_ == 2:
        return "op"
    if type_ == 3:
        return "ed"


def collection_type_subject_type_str(
    subject_type: Literal[1, 2, 3, 4, 6], collection_type: Literal[1, 2, 3, 4, 5, None]
) -> str:
    if collection_type is None:
        return "收藏"
    if collection_type == 5:
        return "抛弃"
    if collection_type == 4:
        return "搁置"
    if collection_type == 3:
        if subject_type == 1:
            return "在读"
        if subject_type == 2:
            return "在看"
        if subject_type == 3:
            return "在听"
        if subject_type == 4:
            return "在玩"
        if subject_type == 6:
            return "在看"
    if collection_type == 2:
        if subject_type == 1:
            return "读过"
        if subject_type == 2:
            return "看过"
        if subject_type == 3:
            return "听过"
        if subject_type == 4:
            return "玩过"
        if subject_type == 6:
            return "看过"
    if collection_type == 1:
        if subject_type == 1:
            return "想读"
        if subject_type == 2:
            return "想看"
        if subject_type == 3:
            return "想听"
        if subject_type == 4:
            return "想玩"
        if subject_type == 6:
            return "想看"
    return "????"


def collection_type_markup_text_list(subject_type: Literal[1, 2, 3, 4, 6]) -> list:
    if subject_type == 1:
        return ["想读", "读过", "在读"]
    if subject_type == 2:
        return ["想看", "看过", "在看"]
    if subject_type == 3:
        return ["想听", "听过", "在听"]
    if subject_type == 4:
        return ["想玩", "玩过", "在玩"]
    if subject_type == 6:
        return ["想看", "看过", "在看"]


def subject_type_to_str(type_: Literal[1, 2, 3, 4, 6]) -> str:
    """将subject_type转文字"""
    if type_ == 1:
        return "书籍"
    elif type_ == 2:
        return "动画"
    elif type_ == 3:
        return "音乐"
    elif type_ == 4:
        return "游戏"
    elif type_ == 6:
        return "剧集"
    else:
        return "???"


def score_to_str(score: float) -> str:
    if score is None:
        return "暂无评分"
    if score < 1.5:
        return "不忍直视"
    if score < 2.5:
        return "很差"
    if score < 3.5:
        return "差"
    if score < 4.5:
        return "较差"
    if score < 5.5:
        return "不过不失"
    if score < 6.5:
        return "还行"
    if score < 7.5:
        return "推荐"
    if score < 8.5:
        return "力荐"
    if score < 9.5:
        return "神作"
    if score < 10.5:
        return "超神作"
    return "???"


def convert_telegram_message_to_bbcode(
    text: str, entities: List[telebot.types.MessageEntity]
) -> str:
    if not entities:
        return text
    new_text = bytearray()
    encode = text.encode('utf-16-le')
    for i in range((len(encode) // 2) + 1):
        for entity in entities[::-1]:
            if i == entity.offset + entity.length:
                if entity.type == 'bold':
                    new_text += "[/b]".encode('utf-16-le')
                elif entity.type == 'italic':
                    new_text += "[/i]".encode('utf-16-le')
                elif entity.type == 'underline':
                    new_text += "[/u]".encode('utf-16-le')
                elif entity.type == 'strikethrough':
                    new_text += "[/s]".encode('utf-16-le')
                elif entity.type == 'spoiler':
                    new_text += "[/mask]".encode('utf-16-le')
                elif entity.type == 'code':
                    new_text += "[/code]".encode('utf-16-le')
                elif entity.type == 'pre':
                    new_text += "[/code]".encode('utf-16-le')
                elif entity.type == 'text_link':
                    new_text += "[/url]".encode('utf-16-le')
        for entity in entities:
            if i == entity.offset:
                if entity.type == 'bold':
                    new_text += "[b]".encode('utf-16-le')
                elif entity.type == 'italic':
                    new_text += "[i]".encode('utf-16-le')
                elif entity.type == 'underline':
                    new_text += "[u]".encode('utf-16-le')
                elif entity.type == 'strikethrough':
                    new_text += "[s]".encode('utf-16-le')
                elif entity.type == 'spoiler':
                    new_text += "[mask]".encode('utf-16-le')
                elif entity.type == 'code':
                    new_text += "[code]".encode('utf-16-le')
                elif entity.type == 'pre':
                    new_text += "[code]".encode('utf-16-le')
                elif entity.type == 'text_link':
                    new_text += (
                        "[url=".encode('utf-16-le')
                        + entity.url.encode('utf-16-le')
                        + "]".encode('utf-16-le')
                    )

        if i < len(encode) / 2:
            new_text += encode[i * 2 : i * 2 + 2]
    return new_text.decode('utf-16-le')


def remove_duplicate_newlines(text: str) -> str:
    """删除重行 够用就行 懒的搞正则"""
    return text.translate(str.maketrans({'\n\n': '\n', '\n\n\n': '\n'}))


def full_group_by(items, key=lambda x: x):
    d = defaultdict(list)
    for item in items:
        d[key(item)].append(item)
    return d