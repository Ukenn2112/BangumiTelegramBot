from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import SimpleCustomFilter

from utils.config_vars import BOT_USERNAME, config

from .help import send_help
from .start import send_start

bot = AsyncTeleBot(config["BOT_TOKEN"], parse_mode="Markdown")

def bot_register(bot: AsyncTeleBot):
    bot.add_custom_filter(IsPrivate())
    bot.register_message_handler(send_start, commands=["start"], is_private=True, pass_bot=True)
    bot.register_message_handler(send_help, commands=["help"], is_private=True, pass_bot=True)


class IsPrivate(SimpleCustomFilter):
    key='is_private'
    @staticmethod
    async def check(message):
        if message.chat.type == "private":
            return True
        else:
            if BOT_USERNAME in message.text:
                await bot.reply_to(message, "请在私聊中使用此命令~")
            return False

async def start_bot():
    bot_register(bot)
    await bot.polling(non_stop=True)