"""查询/绑定 Bangumi"""
import json
import uuid

import telebot

from config import WEBSITE_BASE, BOT_USERNAME
from plugins import help, info
from utils.api import user_data_get, redis_cli, update_user_cookie


def send(message, bot):
    if message.chat.type != "private":
        if message.text == f'/start@{BOT_USERNAME}':
            bot.send_message(message.chat.id, '请私聊我进行Bangumi绑定', parse_mode='Markdown', timeout=20)
        return
    tg_id = message.from_user.id
    user_data = user_data_get(tg_id)
    data = message.text.split(' ')
    if not user_data:
        # 新用户 未绑定时总是提示绑定
        state = uuid.uuid4().hex
        params = {'tg_id': tg_id}
        if len(data) > 1:
            params['param'] = data[1]
        redis_cli.set("oauth:" + state, json.dumps(params), ex=3600)
        url = f'{WEBSITE_BASE}oauth_index?state={state}'
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='绑定Bangumi', url=url))
        bot.send_message(message.chat.id, text='请绑定您的Bangumi', parse_mode='Markdown', reply_markup=markup, timeout=20)
    else:
        if len(data) > 1 and 'chii_sid=' in message.text:
            if update_user_cookie(tg_id, message.text.replace('/start ', '')):
                bot.send_message(message.chat.id, "添加 Cookie 成功")
            else:
                bot.send_message(message.chat.id, "请输入正确的 Cookie")
            return
    if len(data) > 1 and data[1] == "help":
        help.send(message, bot)
    elif len(data) > 1 and data[1].isdecimal():  # 纯数字,查询Subject info
        info.send(message, bot)
    else:
        bot.send_message(message.chat.id, "已绑定", timeout=20)
