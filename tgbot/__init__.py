from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import SimpleCustomFilter

from utils.config_vars import BOT_USERNAME, bot

from .start import send_start
from .help import send_help

def bot_register(bot: AsyncTeleBot):
    bot.add_custom_filter(IsPrivate())
    bot.register_message_handler(send_start, commands=["start"], is_private=True, pass_bot=True)
    bot.register_message_handler(send_help, commands=["help"], is_private=True, pass_bot=True)


class IsPrivate(SimpleCustomFilter):
    """仅私聊使用"""
    key="is_private"
    @staticmethod
    async def is_private(message):
        if message.chat.type != "private":
            if message.text == f"/start@{BOT_USERNAME}":
                bot.reply_to(message, "请在私聊中使用此命令~")
            return False
        else:
            return True