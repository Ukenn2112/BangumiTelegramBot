"""关闭会话"""
import time
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message


def send(message: Message, bot: AsyncTeleBot):
    if message.reply_to_message is None:
        return bot.send_message(
            message.chat.id,
            "错误使用, 请回复需要关闭的对话",
            parse_mode='Markdown',
            reply_to_message_id=message.message_id,
        )
    else:
        if bot.get_me().id == message.reply_to_message.from_user.id:
            bot.delete_message(message.chat.id, message_id=message.reply_to_message.message_id)
            msg = bot.send_message(
                message.chat.id,
                "已关闭该对话",
                parse_mode='Markdown',
                reply_to_message_id=message.message_id,
            )
            bot.delete_message(message.chat.id, message_id=message.message_id)
            time.sleep(5)
            return bot.delete_message(message.chat.id, message_id=msg.id)