"""查询/绑定 Bangumi"""
import datetime
import json
import sqlite3
import uuid

import telebot

from config import WEBSITE_BASE, BOT_USERNAME
from model.page_model import SubjectRequest, RequestSession
from plugins import help
from utils.api import get_subject_info, sub_add, sub_repeat, user_data_get, redis_cli


def send(message, bot):
    if message.chat.type != "private":
        if message.text == f'/start@{BOT_USERNAME}':
            bot.send_message(message.chat.id, '请私聊我进行Bangumi绑定', parse_mode='Markdown', timeout=20)
        return
    tg_id = message.from_user.id
    user_data = user_data_get(tg_id)
    data = message.text.split(' ')
    if len(data) > 1 and data[1].startswith('addsub'):
        sub_data = data[1].lstrip('addsub').split('user')
        if len(sub_data) == 1:
            return
        subject_id = sub_data[0]
        user_id = sub_data[1]
        if sub_repeat(tg_id, subject_id, user_id):
            return bot.send_message(message.chat.id, '您已订阅过该番剧')
        else:
            sub_add(tg_id, subject_id, user_id)
            subject_info = get_subject_info(subject_id)
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(
                telebot.types.InlineKeyboardButton(text='取消订阅', callback_data=f'unaddsub|{subject_id}'),
                telebot.types.InlineKeyboardButton(text='查看详情', url=f"t.me/{BOT_USERNAME}?start={subject_info['id']}")
            )
            text = (
                f'\\[*#番剧成功*]\n\n'
                f'*{subject_info["name_cn"] or subject_info["name"]}*\n\n'
                f'*➤ 放送星期：*`{subject_info["_air_weekday"]}`\n'
            )
            return bot.send_message(message.chat.id, text, parse_mode='Markdown', reply_markup=markup)
    if user_data:
        if len(data) > 1 and data[1].isdecimal():
            msg = bot.send_message(
                message.chat.id,
                "正在搜索请稍候...",
                reply_to_message_id=message.message_id,
                parse_mode='Markdown',
                timeout=20,
            )
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
        elif len(data) > 1 and 'chii_sid=' in message.text:
            if 'chii_sec_id=' in message.text and 'chii_auth=' in message.text:
                sql_con = sqlite3.connect("data/bot.db", check_same_thread=False)
                sql_con.execute(
                    "update user set cookie=?,update_time=? where tg_id=?",
                    (
                        message.text.replace('/start ', ''),
                        datetime.datetime.now().timestamp() // 1000,
                        tg_id,
                    ),
                )
                sql_con.commit()
                bot.send_message(message.chat.id, "添加 Cookie 成功")
                return
            else:
                bot.send_message(message.chat.id, "请输入正确的 Cookie")
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
    bot.send_message(
        message.chat.id,
        text='请绑定您的Bangumi',
        parse_mode='Markdown',
        reply_markup=markup,
        timeout=20,
    )
