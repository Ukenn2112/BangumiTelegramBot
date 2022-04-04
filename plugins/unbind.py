"""查询/绑定 Bangumi"""

from utils.api import data_seek_get, user_data_delete


def send(message, bot):
    if data_seek_get(message.from_user.id):
        if message.text == "/unbind 确认":
            user_data_delete(message.from_user.id)
            bot.send_message(message.chat.id, text='已解绑QAQ, 期待下次与你见面！',
                             parse_mode='Markdown', reply_to_message_id=message.message_id, timeout=20)
        else:
            bot.send_message(
                message.chat.id, text='*⚠注意！您正在执行解除 Bangumi 账号绑定操作：\n\n解绑后您将无法继续使用：收藏管理，章节进度更新，发送评论，展示账户个人收藏，等一系列需要操作或读取账户功能。*\n\n如需继续解绑请输入 \\[`/unbind 确认`]\n', reply_to_message_id=message.message_id, parse_mode='Markdown', timeout=20)
    else:
        bot.send_message(message.chat.id, text='你还没有绑定你解绑个啥？', parse_mode='Markdown',
                         reply_to_message_id=message.message_id, timeout=20)
