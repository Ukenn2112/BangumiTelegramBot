import logging
import pickle

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, InputMedia

from utils.config_vars import config, redis, sql

from ..pages import (collection_list_page, subject_eps_page, subject_page,
                     summary_page, subject_relations_page, edit_rating_page)
from .exception import TokenExpired
from .page_model import (BackRequest, BaseRequest, CollectionsRequest, EditRatingPageRequest,
                         RefreshRequest, RequestSession, SubjectEpsPageRequest, SubjectRelationsPageRequest,
                         SubjectRequest, SummaryRequest)


async def consumption_request(bot: AsyncTeleBot, session: RequestSession):
    """Consumption 处理头"""
    callback_text = None
    try:
        callback_text = await request_handler(session)
        top = session.stack[-1]
    except TokenExpired:
        top = BaseRequest(session)
        top.page_text = "您的Token已过期,请重新绑定"
        sql.delete_user_data(session.request_message.from_user.id)
        from ..start import send_start
        send_start(session.request_message, bot)
    except Exception:
        top = BaseRequest(session)
        top.page_text = "发生了未知异常 QAQ"
        logging.exception(f"发生异常 session:{session.uuid}")
    if top.page_image: # 当前页面有图片
        if session.bot_message.content_type == "text": # 上一个页面是文字 则删除上一条消息发送新消息
            await bot.delete_message(
                message_id=session.bot_message.message_id, chat_id=session.request_message.chat.id
            )
            try:
                session.bot_message = await bot.send_photo(
                    photo=top.page_image,
                    caption=top.page_text,
                    reply_markup=top.page_markup,
                    chat_id=session.request_message.chat.id,
                    reply_to_message_id=session.request_message.message_id,
                )
            except Exception:
                session.bot_message = await bot.send_photo(
                    photo=top.page_image,
                    caption=top.page_text,
                    reply_markup=top.page_markup,
                    chat_id=session.request_message.chat.id,
                    reply_to_message_id=session.request_message.message_id,
                    parse_mode="HTML",
                )
        else: # 上一个页面是图片 则编辑上一条消息
            try:
                session.bot_message = await bot.edit_message_media(
                    media=InputMedia(
                        type="photo",
                        media=top.page_image,
                        caption=top.page_text,
                        parse_mode="Markdown",
                    ),
                    reply_markup=top.page_markup,
                    message_id=session.bot_message.message_id,
                    chat_id=session.request_message.chat.id,
                )
            except Exception:
                session.bot_message = await bot.edit_message_media(
                    media=InputMedia(
                        type="photo",
                        media=top.page_image,
                        caption=top.page_text,
                        parse_mode="HTML",
                    ),
                    reply_markup=top.page_markup,
                    message_id=session.bot_message.message_id,
                    chat_id=session.request_message.chat.id,
                )
        for stack in session.stack:
            if isinstance(stack, SubjectRequest) and session.bot_message.content_type == "photo":
                redis.set(f"subject_image:{stack.subject_id}", session.bot_message.photo[-1].file_id, ex = 60 * 60 * 24)
    else: # 当前页面没有图片
        if session.bot_message.content_type == "text": # 上一个页面是文字 则编辑上一条消息
            try:
                session.bot_message = await bot.edit_message_text(
                    text=top.page_text,
                    reply_markup=top.page_markup,
                    message_id=session.bot_message.message_id,
                    chat_id=session.request_message.chat.id,
                )
            except Exception:
                session.bot_message = await bot.edit_message_text(
                    text=top.page_text,
                    reply_markup=top.page_markup,
                    message_id=session.bot_message.message_id,
                    chat_id=session.request_message.chat.id,
                    parse_mode="HTML",
                )
        elif top.retain_image and session.bot_message.content_type == "photo": # 上一个页面同样是图片 则编辑上一条消息
            try:
                session.bot_message = await bot.edit_message_caption(
                    caption=top.page_text,
                    reply_markup=top.page_markup,
                    message_id=session.bot_message.message_id,
                    chat_id=session.request_message.chat.id,
                )
            except Exception:
                session.bot_message = await bot.edit_message_caption(
                    caption=top.page_text,
                    reply_markup=top.page_markup,
                    message_id=session.bot_message.message_id,
                    chat_id=session.request_message.chat.id,
                    parse_mode="HTML",
                )
        else: # 上一个页面是图片 且不保留图片 则删除上一条消息发送新消息
            await bot.delete_message(
                message_id=session.bot_message.message_id, chat_id=session.request_message.chat.id
            )
            try:
                session.bot_message = await bot.send_message(
                    text=top.page_text,
                    reply_markup=top.page_markup,
                    chat_id=session.request_message.chat.id,
                    reply_to_message_id=session.request_message.message_id,
                )
            except Exception:
                session.bot_message = await bot.send_message(
                    text=top.page_text,
                    reply_markup=top.page_markup,
                    chat_id=session.request_message.chat.id,
                    reply_to_message_id=session.request_message.message_id,
                    parse_mode="HTML",
                )
    stack_call = session.call
    session.call = None
    redis.set(session.uuid, pickle.dumps(session), ex=config["REDIS"]["SESSION_EXPIRES"])
    if stack_call:
        await bot.answer_callback_query(stack_call.id, text=callback_text)


async def global_callback_handler(call: CallbackQuery, bot: AsyncTeleBot):
    """CallBack 处理头"""
    data = call.data.split("|")
    redis_key, request_key = data[0], data[1]
    call_data = redis.get(redis_key)
    if not call_data: return await bot.answer_callback_query(call.id, "您的请求不存在或已过期", cache_time=1)
    # redis.delete(redis_key)  # TODO 没事务 多线程下可能出问题
    session: RequestSession = pickle.loads(call_data)
    next_page = session.stack[-1].possible_request.get(request_key, None)
    if not next_page:
        return await bot.answer_callback_query(call.id, "您的请求出错了", cache_time=3600)
    session.stack.append(next_page)
    session.call = call
    await consumption_request(bot, session)


async def request_handler(session: RequestSession):
    callback_text = None
    top = session.stack[-1] # 最后一个请求
    if isinstance(top, CollectionsRequest):
        await collection_list_page.generate_page(top)
    elif isinstance(top, SubjectRequest):
        await subject_page.generate_page(top)
    elif isinstance(top, SummaryRequest):
        await summary_page.generate_page(top)
    elif isinstance(top, SubjectEpsPageRequest):
        await subject_eps_page.generate_page(top)
        if len(session.stack) > 2 and isinstance(session.stack[-2], SubjectEpsPageRequest):
            del session.stack[-2]
    elif isinstance(top, SubjectRelationsPageRequest):
        await subject_relations_page.generate_page(top)
    elif isinstance(top, EditRatingPageRequest):
        edit_rating_page.generate_page(top)
    elif isinstance(top, BackRequest):
        del session.stack[-2:]  # 删除最后两个
        if top.needs_refresh:
            session.stack.append(RefreshRequest(session))
            await request_handler(session)
    elif isinstance(top, RefreshRequest):
        del session.stack[-1]  # 删除这个请求
        top = session.stack[-1]
        top.page_text = None
        top.page_image = None
        top.page_markup = None
        top.possible_request = {}
        await request_handler(session)
    return callback_text