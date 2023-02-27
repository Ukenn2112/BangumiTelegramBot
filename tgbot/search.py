"""搜索引导指令"""

from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message


async def send_search(message: Message, bot: AsyncTeleBot):
    message_data = message.text.split(" ")
    markup = InlineKeyboardMarkup()
    is_at = (
        "@"
        if message.chat.type == "supergroup" or message.chat.type == "supergroup" == "group"
        else ""
    )
    keywords = message.text[len(message_data[0]) + 1 :]
    button_list = [
        [
            InlineKeyboardButton(text="所有条目", switch_inline_query_current_chat=keywords),
            InlineKeyboardButton(
                text="动画🌸", switch_inline_query_current_chat=is_at + "🌸" + keywords
            ),
            InlineKeyboardButton(
                text="游戏🎮", switch_inline_query_current_chat=is_at + "🎮" + keywords
            ),
            InlineKeyboardButton(
                text="剧集📺", switch_inline_query_current_chat=is_at + "📺" + keywords
            ),
            InlineKeyboardButton(
                text="音乐🎵", switch_inline_query_current_chat=is_at + "🎵" + keywords
            ),
            InlineKeyboardButton(
                text="书籍📚", switch_inline_query_current_chat=is_at + "📚" + keywords
            ),
        ],
        [
            InlineKeyboardButton(text="现实人物", switch_inline_query_current_chat="p " + keywords),
            InlineKeyboardButton(text="虚拟人物", switch_inline_query_current_chat="c " + keywords),
        ],
    ]
    markup.add(*button_list[0], row_width=3)
    markup.add(*button_list[1], row_width=2)
    await bot.reply_to(message, text="请点击下方按钮进行搜索", reply_markup=markup)
