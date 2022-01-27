"""简介页"""
import telebot
from typing import Optional

from utils.api import get_subject_info
from utils.converts import subject_type_to_emoji


def callback(call, bot):
    call_data = call.data.split('|')
    subject_id = call_data[1]  # subject_id
    if len(call_data) > 2:
        week_day = call_data[2]
    else:
        week_day = 0
    summary_data = grnder_summary_message(subject_id, week_day)
    if call.message.content_type == 'photo':
        bot.edit_message_caption(caption=summary_data['text'], chat_id=call.message.chat.id,
                                 message_id=call.message.message_id,
                                 parse_mode='Markdown',
                                 reply_markup=summary_data['markup'])
    else:
        bot.edit_message_text(text=summary_data['text'],
                              parse_mode='Markdown',
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=summary_data['markup'])
    bot.answer_callback_query(call.id)


def grnder_summary_message(subject_id, week_day: Optional[str] = None):
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
