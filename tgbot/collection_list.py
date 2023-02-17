import uuid

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from utils.user_token import bgm_user_data

from .model import CollectionsRequest, RequestSession, consumption_request


async def send_collection_list(message: Message, bot: AsyncTeleBot):
    """处理用户收藏列表"""
    # 1: 书籍, 2: 动画 (默认), 3: 音乐, 4: 游戏, 6: 三次元
    text_sp = message.text.split(" ")
    subject_types = {
        "/book": 1,
        "/anime": 2,
        "/music": 3,
        "/game": 4,
        "/real": 6,
    }
    subject_type = subject_types.get(text_sp[0], 2)
    user_data = await bgm_user_data(message.from_user.id)
    if user_data is None:
        bot_data = await bot.get_me()
        return await bot.reply_to(message, f"发现您未绑定 Bangumi，快*[点我](https://t.me/{bot_data.username}?start=None)*进行绑定吧～", parse_mode="MarkdownV2", disable_web_page_preview=True)
    msg = await bot.reply_to(message, "正在获取收藏列表，请稍后...")
    collection_type = 3
    if message.text:
        if len(text_sp) > 1:
            # 1: 想看, 2: 看过, 3: 在看 (默认), 4: 搁置, 5: 抛弃
            param = message.text[len(text_sp[0]) + 1:]
            if "想" in param or "w" in param:
                collection_type = 1
            elif "过" in param or "c" in param:
                collection_type = 2
            elif "在" in param or "d" in param:
                collection_type = 3
            elif "搁" in param or "o" in param:
                collection_type = 4
            elif "抛" in param or "d" in param:
                collection_type = 5
            elif "全" in param or "a" in param:
                collection_type = None
    session = RequestSession(uuid.uuid4().hex, request_message=message, user_bgm_data=user_data)
    request = CollectionsRequest(
        session, subject_type=subject_type, collection_type=collection_type
    )
    session.stack = [request]
    session.bot_message = msg
    await consumption_request(bot, session)
