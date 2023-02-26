from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_filters import SimpleCustomFilter
from telebot.types import (BotCommand, BotCommandScopeAllGroupChats,
                           BotCommandScopeAllPrivateChats)

from utils.config_vars import BOT_USERNAME, config

from .collection_list import send_collection_list
from .help import send_help
from .info import send_info
from .inline import global_inline_handler
from .inline.anitabi import query_anitabi_text
from .inline.mybgm import query_mybgm_text
from .model import global_callback_handler
from .reply_processing import send_reply
from .start import send_start
from .unbind import send_unbind
from .unsubscribe import unaddsub
from .week import send_week

bot = AsyncTeleBot(config["BOT_TOKEN"], parse_mode="Markdown")

def bot_register():
    """注册Bot命令"""
    bot.add_custom_filter(IsPrivate())
    bot.add_custom_filter(IsRreply())
    # Commands
    bot.register_message_handler(send_start, commands=["start"], is_private=True, pass_bot=True)
    bot.register_message_handler(send_help, commands=["help"], is_private=True, pass_bot=True)
    bot.register_message_handler(send_week, commands=["week"], pass_bot=True)
    bot.register_message_handler(send_info, commands=["info"], pass_bot=True)
    bot.register_message_handler(send_unbind, commands=["unbind"], chat_types=["private"], pass_bot=True)
    bot.register_message_handler(send_collection_list, commands=["book", "anime", "game", "music", "real"], pass_bot=True)
    bot.register_message_handler(send_reply, chat_types=["private"], is_reply=True, pass_bot=True)
    # CallbackQuery
    bot.register_callback_query_handler(callback_none, func=lambda c: c.data == "None", pass_bot=True)
    bot.register_callback_query_handler(unaddsub, func=lambda c: c.data.startswith("unaddsub"), pass_bot=True)
    bot.register_callback_query_handler(global_callback_handler, func=lambda c: True, pass_bot=True)
    # InlineQuery
    bot.register_inline_handler(inline_none, func=lambda query: not query.query, pass_bot=True)
    bot.register_inline_handler(query_anitabi_text, func=lambda query: query.query.startswith("anitabi"), pass_bot=True)
    bot.register_inline_handler(query_mybgm_text, func=lambda query: query.query.startswith("mybgm"), pass_bot=True)
    bot.register_inline_handler(global_inline_handler, func=lambda query: True, pass_bot=True)


async def callback_none(call):
    return await bot.answer_callback_query(call.id)

async def inline_none(inline_query):
    return await bot.answer_inline_query(
        inline_query.id,
        [],
        switch_pm_text="@BGM条目ID或关键字搜索或使用mybgm查询数据",
        switch_pm_parameter="None",
        cache_time=0,
    )

async def set_bot_command():
    """设置Bot命令"""
    await bot.delete_my_commands(scope=None, language_code=None)
    private_commands_list = [
        BotCommand("help", "使用帮助"),
        BotCommand("start", "绑定Bangumi账号"),
        BotCommand("book", "书籍收藏列表"),
        BotCommand("anime", "动画收藏列表"),
        BotCommand("music", "音乐收藏列表"),
        BotCommand("game", "游戏收藏列表"),
        BotCommand("real", "三次元收藏列表"),
        BotCommand("week", "每日放送"),
        BotCommand("unbind", "解除 Bangumi 账号绑定"),
    ]
    group_commands_list = [
        BotCommand("book", "书籍收藏列表"),
        BotCommand("anime", "动画收藏列表"),
        BotCommand("music", "音乐收藏列表"),
        BotCommand("game", "游戏收藏列表"),
        BotCommand("real", "三次元收藏列表"),
        BotCommand("week", "每日放送"),
    ]
    try:
        await bot.set_my_commands(private_commands_list, scope=BotCommandScopeAllPrivateChats())
        await bot.set_my_commands(group_commands_list, scope=BotCommandScopeAllGroupChats())
        return
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
                await bot.reply_to(message, "请在私聊中使用此命令～")
            return False

class IsRreply(SimpleCustomFilter):
    """判断是否为回复"""
    key='is_reply'
    @staticmethod
    async def check(message):
        if message.reply_to_message and message.reply_to_message.from_user.username == BOT_USERNAME:
            return True
        else:
            return False

async def start_bot():
    bot_register()
    await set_bot_command()
    await bot.polling(non_stop=True)