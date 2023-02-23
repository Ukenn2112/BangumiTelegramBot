"""每日放送查询"""
import datetime
import uuid

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from utils.user_token import bgm_user_data

from .model import RequestSession, WeekRequest, consumption_request


async def send_week(message: Message, bot: AsyncTeleBot):
    data = message.text.split(' ')
    if len(data) == 1:
        # 如果未传参数
        now_week = int(datetime.datetime.now().strftime("%w"))
        day = 7 if now_week == 0 else now_week
    else:
        if data[1].isdecimal() and 1 <= int(data[1]) <= 7:
            day = int(data[1])
        else:
            return await bot.reply_to(message, "输入错误 请输入：`/week 1~7`")
    msg = await bot.reply_to(message, "正在搜索请稍候...")
    user_data = await bgm_user_data(message.from_user.id)
    session = RequestSession(uuid.uuid4().hex, message, user_data)
    request = WeekRequest(session, day)
    session.stack = [request]
    session.bot_message = msg

    await consumption_request(bot, session)
