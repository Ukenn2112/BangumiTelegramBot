from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from utils.before_api import get_user_token
from utils.config_vars import sql

async def send_start(message: Message, bot: AsyncTeleBot):
    data = message.text.split(" ")
    if len(data) > 1 and data[1].startswith("addsub"):
        sub_data = data[1].lstrip("addsub").split("-")
        if len(sub_data) < 2: return
        subject_id, bgm_id = sub_data[0], sub_data[1]
        if not subject_id.isdigit() or not bgm_id.isdigit(): return
        if sql.check_subscribe(subject_id, message.from_user.id):
            return await bot.reply_to(message, "你已经订阅过这个番剧了哦~")
        else:
            sql.insert_subscribe_data(message.from_user.id, bgm_id, subject_id)
            return await bot.reply_to(message, "订阅成功~") # TODO: 通知用户
    access_token = await get_user_token(message.from_user.id)