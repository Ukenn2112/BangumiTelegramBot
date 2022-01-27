import telebot
from typing import Optional

from utils.api import get_subject_info
from utils.converts import subject_type_to_emoji

def grnder_summary_message(subject_id, week_day: Optional[str] = None):
    """简介页"""
    subject_info = get_subject_info(subject_id)
    text = {f"{subject_type_to_emoji(subject_info['type'])} *{subject_info['name_cn']}*\n"
            f"{subject_info['name']}\n\n"
            f"*➤ 简介：*\n"
            f"{subject_info['summary']}\n"
            f"\n📖 [详情](https://bgm.tv/subject/{subject_id})"
            f"\n💬 [吐槽箱](https://bgm.tv/subject/{subject_id}/comments)"}
    markup = telebot.types.InlineKeyboardMarkup()
    if week_day != 0:
        markup.add(telebot.types.InlineKeyboardButton(
            text='返回', callback_data=f'search_details|week|{subject_id}|{week_day}|1'))
    else:
        markup.add(telebot.types.InlineKeyboardButton(
            text='返回', callback_data=f'search_details|search|{subject_id}|0|1'))
    return {'text': text, 'markup': markup}