from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from utils.config_vars import sql


async def send_unbind(message: Message, bot: AsyncTeleBot):
    if sql.inquiry_user_data(message.from_user.id):
        if message.text == "/unbind 确认":
            sql.delete_user_data(message.from_user.id)
            return await bot.reply_to(message, "已解绑QAQ, 期待下次与你见面！")
        else:
            return await bot.reply_to(message,
                text=(
                    "*⚠注意！您正在执行解除 Bangumi 账号绑定操作：\n\n"
                    "解绑后您将无法继续使用：收藏管理，章节进度更新，发送评论，展示账户个人收藏，等一系列需要操作或读取账户功能。*\n\n"
                    "如需继续解绑请输入 \\[`/unbind 确认`]\n"
                )
            )
    else:
        return await bot.reply_to(message, "你还没有绑定你解绑个啥？")
