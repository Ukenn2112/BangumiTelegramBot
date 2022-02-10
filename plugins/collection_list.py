"""查询 Bangumi 用户在看"""
import json
import uuid

from config import BOT_USERNAME
from model.page_model import CollectionsRequest, RequestStack
from utils.api import get_user, user_data_get


def send(message, bot, subject_type):
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
    try:
        user_data = get_user(_user.get('user_id'))
    except FileNotFoundError:
        bot.edit_message_text(text="出错了，没有查询到该用户",
                              chat_id=msg.chat.id,
                              message_id=msg.message_id)
        return
    except json.JSONDecodeError:
        bot.edit_message_text(text="出错了，无法获取到您的个人信息",
                              chat_id=msg.chat.id,
                              message_id=msg.message_id)
        return
    user_data['_user'] = _user
    page = CollectionsRequest(user_data, subject_type)
    stack = RequestStack(page, uuid.uuid4().hex)
    stack.request_message = message
    stack.bot_message = msg
    from bot import consumption_request
    consumption_request(stack)
