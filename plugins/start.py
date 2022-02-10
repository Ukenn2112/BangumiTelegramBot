"""查询/绑定 Bangumi"""
import uuid

import telebot

from config import WEBSITE_BASE, BOT_USERNAME
from model.page_model import SubjectRequest, RequestStack
from utils.api import user_data_get


def send(message, bot):
    if message.chat.type == "private":  # 当私人聊天
        test_id = message.from_user.id
        user_data = user_data_get(test_id)
        if user_data:
            data = message.text.split(' ')
            if len(data) > 1:
                msg = bot.send_message(message.chat.id, "正在搜索请稍候...",
                                       reply_to_message_id=message.message_id,
                                       parse_mode='Markdown',
                                       timeout=20)
                subject_id = data[1]  # 剧集ID
                subject_request = SubjectRequest(subject_id)
                subject_request.is_root = True
                stack = RequestStack(subject_request, uuid.uuid4().hex)
                stack.request_message = message
                stack.bot_message = msg
                from bot import consumption_request
                consumption_request(stack)
            else:
                bot.send_message(message.chat.id, "已绑定", timeout=20)
        else:
            text = '请绑定您的Bangumi'
            url = f'{WEBSITE_BASE}oauth_index?tg_id={test_id}'
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(
                text='绑定Bangumi', url=url))
            bot.send_message(message.chat.id, text=text,
                             parse_mode='Markdown', reply_markup=markup, timeout=20)
    else:
        if message.text == f'/start@{BOT_USERNAME}':
            bot.send_message(message.chat.id, '请私聊我进行Bangumi绑定',
                             parse_mode='Markdown', timeout=20)
