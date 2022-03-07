"""查询 Bangumi 用户在看"""
import uuid

from config import BOT_USERNAME
from model.page_model import CollectionsRequest, RequestSession
from utils.api import user_data_get


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
    session = RequestSession(uuid.uuid4().hex, request_message=message)
    request = CollectionsRequest(session, subject_type=subject_type)
    session.stack = [request]

    session.bot_message = msg
    from bot import consumption_request
    consumption_request(session)
