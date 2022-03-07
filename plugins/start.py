"""查询/绑定 Bangumi"""
import json
import uuid

import telebot

from config import WEBSITE_BASE, BOT_USERNAME
from model.page_model import SubjectRequest, RequestSession
from plugins import help
from utils.api import user_data_get, redis_cli


def send(message, bot):
    if message.chat.type != "private":
        if message.text == f'/start@{BOT_USERNAME}':
            bot.send_message(message.chat.id, '请私聊我进行Bangumi绑定', parse_mode='Markdown', timeout=20)
        return
    tg_id = message.from_user.id
    user_data = user_data_get(tg_id)
    data = message.text.split(' ')
    if user_data:
        if len(data) > 1 and data[1].isdecimal():
            msg = bot.send_message(message.chat.id,
                                   "正在搜索请稍候...",
                                   reply_to_message_id=message.message_id,
                                   parse_mode='Markdown',
                                   timeout=20)
            subject_id = int(data[1])  # 剧集ID

            session = RequestSession(uuid.uuid4().hex, message)
            subject_request = SubjectRequest(session, subject_id, True)
            session.stack = [subject_request]
            session.bot_message = msg

            from bot import consumption_request
            consumption_request(session)
            return
        elif len(data) > 1 and data[1] == "help":
            help.send(message, bot)
            return
        else:
            bot.send_message(message.chat.id, "已绑定", timeout=20)
            return
    state = uuid.uuid4().hex
    params = {'tg_id': tg_id}
    if len(data) > 1:
        params['param'] = data[1]
    redis_cli.set("oauth:" + state, json.dumps(params), ex=3600)
    url = f'{WEBSITE_BASE}oauth_index?state={state}'
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='绑定Bangumi', url=url))
    bot.send_message(message.chat.id, text='请绑定您的Bangumi', parse_mode='Markdown', reply_markup=markup, timeout=20)
