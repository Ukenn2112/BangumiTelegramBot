"""每日放送查询"""
import datetime
import uuid

from model.page_model import WeekRequest, RequestSession


def send(message, bot):
    data = message.text.split(' ')
    if len(data) == 1:
        # 如果未传参数
        now_week = int(datetime.datetime.now().strftime("%w"))
        day = 7 if now_week == 0 else now_week
    else:
        if data[1].isdecimal() and 1 <= int(data[1]) <= 7:
            day = int(data[1])
        else:
            bot.send_message(message.chat.id, "输入错误 请输入：`/week 1~7`",
                             parse_mode='Markdown', timeout=20)
            return
    msg = bot.send_message(message.chat.id, "正在搜索请稍候...", reply_to_message_id=message.message_id, parse_mode='Markdown',
                           timeout=20)

    session = RequestSession(uuid.uuid4().hex, message)
    request = WeekRequest(session, day)
    session.stack = [request]
    session.bot_message = msg
    from bot import consumption_request
    consumption_request(session)
