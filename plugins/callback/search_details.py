"""搜索详情页"""
from utils.api import anime_img
from plugins.info import gander_info_message


def callback(call, bot):
    call_tg_id = call.from_user.id
    call_data = call.data.split('|')
    back_type = call_data[1]  # 返回类型
    subject_id = call_data[2]  # 剧集ID
    back_week_day = int(call_data[3])  # 如是从week请求则为week day
    back = int(call_data[4])  # 是否是从收藏/简介页返回 是则为1 否则为2
    img_url = anime_img(subject_id)
    search_message = gander_info_message(
        call_tg_id, subject_id, back_week_day=back_week_day, back_type=back_type)
    if back == 1:
        if call.message.content_type == 'photo':
            bot.edit_message_caption(caption=search_message['text'],
                                     chat_id=call.message.chat.id,
                                     message_id=call.message.message_id,
                                     parse_mode='Markdown',
                                     reply_markup=search_message['markup'])
        else:
            bot.edit_message_text(text=search_message['text'],
                                  parse_mode='Markdown',
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=search_message['markup'])
    else:
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id, timeout=20)
        if img_url == 'None__' or not img_url:
            bot.send_message(chat_id=call.message.chat.id,
                             text=search_message['text'],
                             parse_mode='Markdown',
                             reply_markup=search_message['markup'],
                             timeout=20)
        else:
            bot.send_photo(chat_id=call.message.chat.id,
                           photo=img_url,
                           caption=search_message['text'],
                           parse_mode='Markdown',
                           reply_markup=search_message['markup'])
    bot.answer_callback_query(call.id)
