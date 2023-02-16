from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import SimpleCustomFilter
from telebot.types import BotCommand

from utils.config_vars import BOT_USERNAME, config

from .help import send_help
from .start import send_start

bot = AsyncTeleBot(config["BOT_TOKEN"], parse_mode="Markdown")

def bot_register():
    """注册Bot命令"""
    bot.add_custom_filter(IsPrivate())
    bot.register_message_handler(send_start, commands=["start"], is_private=True, pass_bot=True)
    bot.register_message_handler(send_help, commands=["help"], is_private=True, pass_bot=True)


async def set_bot_command():
    """设置Bot命令"""
    await bot.delete_my_commands(scope=None, language_code=None)
    commands_list = [
        BotCommand("help", "使用帮助"),
        BotCommand("start", "绑定Bangumi账号"),
    ]
    try:
        return await bot.set_my_commands(commands_list)
    except Exception:
        pass


class IsPrivate(SimpleCustomFilter):
    """判断是否为私聊"""
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
    bot_register()
    await set_bot_command()
    await bot.polling(non_stop=True)