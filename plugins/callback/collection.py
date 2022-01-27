"""收藏页"""
import telebot
from utils.api import get_subject_info, data_seek_get, user_collection_get, collection_post

def callback(call, bot):
    call_tg_id = call.from_user.id
    call_data = call.data.split('|')
    tg_id = int(call_data[1])  # 被更新用户 Telegram ID
    subject_id = call_data[2]  # 剧集ID
    back_type = call_data[3]  # 返回类型
    back_week_day = call_data[4]  # 如是从week请求则为week day 不是则为0
    collection_type = call_data[5]  # 用户请求收藏状态 初始进入收藏页则为 null
    name = get_subject_info(subject_id)['name']
    if collection_type == 'null':
        if not data_seek_get(call_tg_id):
            bot.answer_callback_query(call.id, text='您未绑定Bangumi，请私聊我使用/start进行绑定', show_alert=True)
        else:
            text = f'*您想将 “*`{name}`*” 收藏为*\n\n'
            markup = telebot.types.InlineKeyboardMarkup()
            button_list = []
            if back_type == 'now_do':
                back_page = call_data[6]  # 返回在看列表页数
                button_list.append(telebot.types.InlineKeyboardButton(
                    text='返回', callback_data=f'now_do|{tg_id}|{subject_id}|1|{back_page}'))
            else:
                button_list.append(telebot.types.InlineKeyboardButton(
                    text='返回', callback_data=f'search_details|{back_type}|{subject_id}|{back_week_day}|1'))
            button_list.append(telebot.types.InlineKeyboardButton(
                text='想看', callback_data=f'collection|{call_tg_id}|{subject_id}|{back_type}|{back_week_day}|wish'))
            button_list.append(telebot.types.InlineKeyboardButton(
                text='看过', callback_data=f'collection|{call_tg_id}|{subject_id}|{back_type}|{back_week_day}|collect'))
            button_list.append(telebot.types.InlineKeyboardButton(
                text='在看', callback_data=f'collection|{call_tg_id}|{subject_id}|{back_type}|{back_week_day}|do'))
            button_list.append(telebot.types.InlineKeyboardButton(
                text='搁置', callback_data=f'collection|{call_tg_id}|{subject_id}|{back_type}|{back_week_day}|on_hold'))
            button_list.append(telebot.types.InlineKeyboardButton(
                text='抛弃', callback_data=f'collection|{call_tg_id}|{subject_id}|{back_type}|{back_week_day}|dropped'))
            markup.add(*button_list, row_width=3)
            if call.message.content_type == 'photo':
                bot.edit_message_caption(caption=text, chat_id=call.message.chat.id,
                                         message_id=call.message.message_id,
                                         parse_mode='Markdown',
                                         reply_markup=markup)
            else:
                bot.edit_message_text(text=text,
                                      parse_mode='Markdown',
                                      chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      reply_markup=markup)
            bot.answer_callback_query(call.id)
    if call_tg_id == tg_id:
        rating = str(user_collection_get(tg_id, subject_id).get('rating'))
        if collection_type == 'wish':  # 想看
            collection_post(tg_id, subject_id, collection_type, rating)
            bot.send_message(chat_id=call.message.chat.id,
                             text=f'已将 “`{name}`” 收藏更改为想看', parse_mode='Markdown', timeout=20)
            bot.answer_callback_query(call.id, text='已将收藏更改为想看')
        if collection_type == 'collect':  # 看过
            collection_post(tg_id, subject_id, collection_type, rating)
            bot.send_message(chat_id=call.message.chat.id,
                             text=f'已将 “`{name}`” 收藏更改为看过', parse_mode='Markdown', timeout=20)
            bot.answer_callback_query(call.id, text='已将收藏更改为看过')
        if collection_type == 'do':  # 在看
            collection_post(tg_id, subject_id, collection_type, rating)
            bot.send_message(chat_id=call.message.chat.id,
                             text=f'已将 “`{name}`” 收藏更改为在看', parse_mode='Markdown', timeout=20)
            bot.answer_callback_query(call.id, text='已将收藏更改为在看')
        if collection_type == 'on_hold':  # 搁置
            collection_post(tg_id, subject_id, collection_type, rating)
            bot.send_message(chat_id=call.message.chat.id,
                             text=f'已将 “`{name}`” 收藏更改为搁置', parse_mode='Markdown', timeout=20)
            bot.answer_callback_query(call.id, text='已将收藏更改为搁置')
        if collection_type == 'dropped':  # 抛弃
            collection_post(tg_id, subject_id, collection_type, rating)
            bot.send_message(chat_id=call.message.chat.id,
                             text=f'已将 “`{name}`” 收藏更改为抛弃', parse_mode='Markdown', timeout=20)
            bot.answer_callback_query(call.id, text='已将收藏更改为抛弃')
    else:
        bot.answer_callback_query(call.id, text='和你没关系，别点了~', show_alert=True)