import uuid

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from utils.config_vars import BOT_USERNAME
from utils.user_token import bgm_user_data

from .model import consumption_request
from .model.page_model import RequestSession, SubjectRequest


async def send_info(message: Message, bot: AsyncTeleBot, subject_id: int = None):
    if subject_id is None:
        if message.chat.type != "private":
            if not message.text.startswith(f"/info@{BOT_USERNAME}"):
                return
        msg_data = message.text.split(' ')
        if len(msg_data) != 2 or not msg_data[1].isdecimal():
            return await bot.reply_to(message, "错误使用 `/info BGM_Subject_ID`")
        subject_id = int(msg_data[1])
    msg = await bot.reply_to(message, "正在搜索请稍候...")
    session = RequestSession(uuid.uuid4().hex, message)
    subject_request = SubjectRequest(session, subject_id, is_root=True)
    session.stack = [subject_request]
    session.bot_message = msg
    session.user_bgm_data = await bgm_user_data(message.from_user.id)
    await consumption_request(bot, session)