import pickle

from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from utils.config_vars import redis, bgm
from utils.converts import convert_telegram_message_to_bbcode

from .model.page_model import EditCollectionTypePageRequest, EditCollectionTagsPageRequest, EditEpsPageRequest
from .pages.edit_collection_type_page import collection_tags_page


async def send_reply(message: Message, bot: AsyncTeleBot):
    """处理回复消息"""
    call_data = redis.get(f"reply_process:{message.reply_to_message.id}")
    if not call_data:
        return await bot.reply_to(message, "此消息未被标记处理，可能缓存已过期，请尝试重新刷新需要回复的操作页面")
    request = pickle.loads(call_data)
    if isinstance(request, EditCollectionTypePageRequest):
        await bgm.patch_user_subject_collection(
            request.session.user_bgm_data["accessToken"],
            request.subject_info["id"],
            comment=message.text,
        )
        return await bot.reply_to(message, f"`{request.subject_info['name']}`的评论已更新")
    elif isinstance(request, EditEpsPageRequest):
        if request.session.user_bgm_data["Cookie"] is None:
            return await bot.reply_to(message, "发送章节评论需要使用 Web 端 API 操作，如需使用章节评论功能请先使用 /unbind 解绑账号，再使用 /start 的*登录绑定 Bangumi*进行绑定")
        try:
            bgm.post_episode_reply(
                request.session.user_bgm_data["Cookie"],
                request.episode_info["id"],
                convert_telegram_message_to_bbcode(message.text, message.entities)
            )
            return await bot.reply_to(message, f"已发送至 EP:{request.episode_info['sort']} 的评论")
        except Exception as e:
            return await bot.reply_to(message, f"发送失败，错误信息：{e}")
    elif isinstance(request, EditCollectionTagsPageRequest):
        tags = message.text.replace(" ", "").split("#")
        await bgm.patch_user_subject_collection(
            request.session.user_bgm_data["accessToken"],
            request.user_collection["subject_id"],
            tags=tags
        )
        request.user_collection["tags"] = tags
        edit_msg = await collection_tags_page(request)
        await bot.reply_to(message, f"`{request.user_collection['subject']['name']}`的{len(tags)}个标签已更新")

    if request.retain_image and request.session.bot_message.content_type == "photo": # 上一个页面同样是图片 则编辑上一条消息
        try:
            await bot.edit_message_caption(
                caption=edit_msg.page_text,
                reply_markup=edit_msg.page_markup,
                message_id=request.session.bot_message.message_id,
                chat_id=request.session.request_message.chat.id,
            )
        except Exception:
            await bot.edit_message_caption(
                caption=edit_msg.page_text,
                reply_markup=edit_msg.page_markup,
                message_id=request.session.bot_message.message_id,
                chat_id=request.session.request_message.chat.id,
                parse_mode="HTML",
            )
    else:
        try:
            await bot.edit_message_text(
                text=edit_msg.page_text,
                reply_markup=edit_msg.page_markup,
                message_id=request.session.bot_message.message_id,
                chat_id=request.session.request_message.chat.id,
            )
        except Exception:
            await bot.edit_message_text(
                text=edit_msg.page_text,
                reply_markup=edit_msg.page_markup,
                message_id=request.session.bot_message.message_id,
                chat_id=request.session.request_message.chat.id,
                parse_mode="HTML",
            )