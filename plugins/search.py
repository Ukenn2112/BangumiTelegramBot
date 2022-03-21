"""搜索引导指令"""
import telebot


def send(message, bot):
    message_data = message.text.split(' ')
    markup = telebot.types.InlineKeyboardMarkup()
    is_at = '@' if message.chat.type == 'supergroup' or message.chat.type == 'supergroup' == 'group' else ''
    markup.add(telebot.types.InlineKeyboardButton(
        text='所有条目', switch_inline_query_current_chat=message.text[len(message_data[0]) + 1:]))
    markup.add(telebot.types.InlineKeyboardButton(
        text='动画🌸', switch_inline_query_current_chat=is_at + '🌸' + message.text[len(message_data[0]) + 1:]))
    markup.add(telebot.types.InlineKeyboardButton(
        text='游戏🎮', switch_inline_query_current_chat=is_at + '🎮' + message.text[len(message_data[0]) + 1:]))
    markup.add(telebot.types.InlineKeyboardButton(
        text='剧集📺', switch_inline_query_current_chat=is_at + '📺' + message.text[len(message_data[0]) + 1:]))
    markup.add(telebot.types.InlineKeyboardButton(
        text='音乐🎵', switch_inline_query_current_chat=is_at + '🎵' + message.text[len(message_data[0]) + 1:]))
    markup.add(telebot.types.InlineKeyboardButton(
        text='书籍📚', switch_inline_query_current_chat=is_at + '📚' + message.text[len(message_data[0]) + 1:]))

    bot.send_message(chat_id=message.chat.id, text='请点击下方按钮进行搜索', parse_mode='Markdown', reply_markup=markup,
                     timeout=20)
