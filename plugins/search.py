"""搜索引导指令"""
import telebot

def send(message, bot):
    message_data = message.text.split(' ')
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        text='开始搜索', switch_inline_query_current_chat=message.text[len(message_data[0]) + 1:]))
    bot.send_message(chat_id=message.chat.id, text='请点击下方按钮进行搜索', parse_mode='Markdown', reply_markup=markup,
                     timeout=20)