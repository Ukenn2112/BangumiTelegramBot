from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message


async def send_start(message: Message, bot: AsyncTeleBot):
    await bot.send_message()