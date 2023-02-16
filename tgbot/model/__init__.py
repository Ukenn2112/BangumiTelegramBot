import logging
import pickle

from telebot.async_telebot import AsyncTeleBot
from telebot.types import InputMedia

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