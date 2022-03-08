"""查询 Bangumi 用户在看"""
import uuid
from typing import Literal

import telebot

from config import BOT_USERNAME
from model.page_model import CollectionsRequest, RequestSession
from utils.api import user_data_get


def send(message: telebot.types.Message, bot, subject_type):
    tg_id = message.from_user.id
    _user = user_data_get(tg_id)
    if _user is None:
        # 如果未绑定 直接报错
        bot.send_message(message.chat.id,
                         f"未绑定Bangumi，请私聊使用[/start](https://t.me/{BOT_USERNAME}?start=none)进行绑定",
                         parse_mode='Markdown', timeout=20)
        return
    msg = bot.send_message(message.chat.id, "正在查询请稍候...", reply_to_message_id=message.message_id,
                           parse_mode='Markdown', timeout=20)
    collection_type: Literal[1, 2, 3, 4, 5, None] = 3
    if message.text:
        text_sp = message.text.split(" ")
        if len(text_sp) > 1:
            # 1想看 2看过 3在看 4搁置 5抛弃
            param = message.text[len(text_sp[0]) + 1:]
            if "想" in param or "w" in param:
                collection_type = 1
            if "过" in param or "c" in param:
                collection_type = 2
            if "在" in param or "d" in param:
                collection_type = 3
            if "搁" in param or "o" in param:
                collection_type = 4
            if "抛" in param or "d" in param:
                collection_type = 5
            if "全" in param or "a" in param:
                collection_type = None

    session = RequestSession(uuid.uuid4().hex, request_message=message)
    request = CollectionsRequest(session, subject_type=subject_type, collection_type=collection_type)
    session.stack = [request]

    session.bot_message = msg
    from bot import consumption_request
    consumption_request(session)
