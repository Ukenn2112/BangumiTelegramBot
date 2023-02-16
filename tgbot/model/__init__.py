import logging
import pickle

from telebot.async_telebot import AsyncTeleBot
from telebot.types import InputMedia, CallbackQuery

from utils.config_vars import config, redis, sql

from ..pages import collection_list_page
from .exception import TokenExpired
from .page_model import (BackRequest, BaseRequest, CollectionsRequest,
                         RefreshRequest, RequestSession, SubjectRequest)


async def consumption_request(bot: AsyncTeleBot, session: RequestSession):
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
        top.page_text = "发生了未知异常QAQ"
        logging.exception(f"发生异常 session:{session.uuid}")
    if top.page_image:
        if session.bot_message.content_type == 'text':
            await bot.delete_message(
                message_id=session.bot_message.message_id, chat_id=session.request_message.chat.id
            )
            session.bot_message = await bot.send_photo(
                photo=top.page_image,
                caption=top.page_text,
                parse_mode='markdown',
                reply_markup=top.page_markup,
                chat_id=session.request_message.chat.id,
                reply_to_message_id=session.request_message.message_id,
            )
        else:
            session.bot_message = await bot.edit_message_media(
                media=InputMedia(
                    type='photo',
                    media=top.page_image,
                    caption=top.page_text,
                    parse_mode="markdown",
                ),
                reply_markup=top.page_markup,
                message_id=session.bot_message.message_id,
                chat_id=session.request_message.chat.id,
            )
    else:
        if session.bot_message.content_type == 'text':
            session.bot_message = await bot.edit_message_text(
                text=top.page_text,
                reply_markup=top.page_markup,
                parse_mode='markdown',
                message_id=session.bot_message.message_id,
                chat_id=session.request_message.chat.id,
            )
        elif top.retain_image and session.bot_message.content_type == 'photo':
            session.bot_message = await bot.edit_message_caption(
                caption=top.page_text,
                reply_markup=top.page_markup,
                parse_mode='markdown',
                message_id=session.bot_message.message_id,
                chat_id=session.request_message.chat.id,
            )
        else:
            await bot.delete_message(
                message_id=session.bot_message.message_id, chat_id=session.request_message.chat.id
            )
            session.bot_message = await bot.send_message(
                text=top.page_text,
                reply_markup=top.page_markup,
                parse_mode='markdown',
                chat_id=session.request_message.chat.id,
                reply_to_message_id=session.request_message.message_id,
            )
    stack_call = session.call
    session.call = None
    redis.set(session.uuid, pickle.dumps(session), ex=config["REDIS"]["SESSION_EXPIRES"])
    if stack_call:
        await bot.answer_callback_query(stack_call.id, text=callback_text)


async def global_callback_handler(call: CallbackQuery, bot: AsyncTeleBot):
    data = call.data.split("|")
    redis_key = data[0]
    request_key = data[1]
    call_data = redis.get(redis_key)
    if not call_data:
        return await bot.answer_callback_query(call.id, "您的请求不存在或已过期", cache_time=1)
    redis.delete(redis_key)  # TODO 没事务 多线程下可能出问题
    session: RequestSession = pickle.loads(call_data)
    next_page = session.stack[-1].possible_request.get(request_key, None)
    if not next_page:
        return await bot.answer_callback_query(call.id, "您的请求出错了", cache_time=3600)
    session.stack.append(next_page)
    session.call = call
    await consumption_request(bot, session)


async def request_handler(session: RequestSession):
    callback_text = None
    top = session.stack[-1]
    if isinstance(top, CollectionsRequest):
        await collection_list_page.generate_page(top)
    elif isinstance(top, BackRequest):
        del session.stack[-2:]  # 删除最后两个
        if top.needs_refresh:
            session.stack.append(RefreshRequest(session))
            request_handler(session)
    elif isinstance(top, RefreshRequest):
        del session.stack[-1]  # 删除这个请求
        top = session.stack[-1]
        top.page_text = None
        top.page_image = None
        top.page_markup = None
        top.possible_request = {}
        request_handler(session)
    return callback_text