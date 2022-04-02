"""查询/绑定 Bangumi"""

from utils.api import user_data_delete


def send(message, bot):
    if message.text == "/unbind 确认":
        user_data_delete(message.from_user.id)
        bot.send_message(message.chat.id, text='已解绑QAQ', parse_mode='Markdown', timeout=20)
