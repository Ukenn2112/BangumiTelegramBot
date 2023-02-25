from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery

from utils.config_vars import sql

async def unaddsub(call: CallbackQuery, bot: AsyncTeleBot):
    """取消订阅"""
    call_data = call.data.split("|")
    if sql.check_subscribe(call_data[1], call.from_user.id):
        sql.delete_subscribe_data(call_data[1], call.from_user.id)
        await bot.answer_callback_query(call.id, "取消订阅成功", cache_time=1)
    else:
        await bot.answer_callback_query(call.id, "你已经取消订阅了这个条目", cache_time=3600)