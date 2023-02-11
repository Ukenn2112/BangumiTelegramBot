from telebot.async_telebot import AsyncTeleBot

from .start import send_start

def bot_register(bot: AsyncTeleBot):
    bot.register_message_handler(send_start, commands=['start'], pass_bot=True)