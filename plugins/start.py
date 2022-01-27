"""查询/绑定 Bangumi"""
import telebot
from utils.api import data_seek_get
from config import WEBSITE_BASE, BOT_USERNAME

def send(message, bot):
    if message.chat.type == "private":  # 当私人聊天
        test_id = message.from_user.id
        if data_seek_get(test_id):
            bot.send_message(message.chat.id, "已绑定", timeout=20)
        else:
            text = '请绑定您的Bangumi'
            url = f'{WEBSITE_BASE}oauth_index?tg_id={test_id}'
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(text='绑定Bangumi', url=url))
            bot.send_message(message.chat.id, text=text, parse_mode='Markdown', reply_markup=markup, timeout=20)
    else:
        if message.text == f'/start@{BOT_USERNAME}':
            bot.send_message(message.chat.id, '请私聊我进行Bangumi绑定', parse_mode='Markdown', timeout=20)
        else:
            pass