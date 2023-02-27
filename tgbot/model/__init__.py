import logging
import pickle

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, InputMedia

from utils.config_vars import config, redis, sql

from ..pages import (collection_list_page, edit_collection_type_page,
                     edit_eps_page, edit_rating_page, subject_eps_page,
                     subject_page, subject_relations_page, summary_page,
                     week_page)
from .exception import TokenExpired, UserNotBound
from .page_model import (BackRequest, BaseRequest, CloseRequest, CollectionsRequest,
                         DoEditCollectionTypeRequest, DoEditEpisodeRequest,
                         DoEditRatingRequest, EditCollectionTagsPageRequest,
                         EditCollectionTypePageRequest, EditEpsPageRequest,
                         EditRatingPageRequest, RefreshRequest, RequestSession,
                         SubjectEpsPageRequest, SubjectRelationsPageRequest,
                         SubjectRequest, SummaryRequest, WeekRequest)


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
        await send_start(session.request_message, bot)
    except UserNotBound:
        top = BaseRequest(session)
        top.page_text = "此操作需要绑定 Bangumi 账户"
        from ..start import send_start
        await send_start(session.request_message, bot)
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
    if top.reply_process:
        redis.set(f"reply_process:{session.bot_message.id}", pickle.dumps(top), ex=config["REDIS"]["SESSION_EXPIRES"])
    else:
        redis.delete(f"reply_process:{session.bot_message.id}")
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
    if isinstance(next_page, CloseRequest): # 关闭会话
        if next_page.tg_id == call.from_user.id:
            await bot.delete_message(
                message_id=next_page.session.bot_message.message_id, chat_id=next_page.session.bot_message.chat.id
            )
            await bot.answer_callback_query(call.id, "已关闭对话", cache_time=1)
            return redis.delete(redis_key)
        else: return await bot.answer_callback_query(call.id, "您没有权限关闭对话", cache_time=1)
    session.stack.append(next_page)
    session.call = call
    await consumption_request(bot, session)


async def request_handler(session: RequestSession):
    callback_text = None
    top = session.stack[-1] # 最后一个请求
    if isinstance(top, CollectionsRequest): # 用户收藏列表
        await collection_list_page.generate_page(top)
    elif isinstance(top, SubjectRequest): # 条目详情页
        await subject_page.generate_page(top)
    elif isinstance(top, SummaryRequest): # 条目简介页
        await summary_page.generate_page(top)
    elif isinstance(top, SubjectEpsPageRequest): # 条目剧集页
        await subject_eps_page.generate_page(top)
        if len(session.stack) > 2 and isinstance(session.stack[-2], SubjectEpsPageRequest):
            del session.stack[-2]
    elif isinstance(top, SubjectRelationsPageRequest): # 条目关联页
        await subject_relations_page.generate_page(top)
    elif isinstance(top, EditRatingPageRequest): # 编辑评分页
        await edit_rating_page.generate_page(top)
    elif isinstance(top, EditCollectionTypePageRequest): # 编辑收藏状态页
        await edit_collection_type_page.generate_page(top)
    elif isinstance(top, EditEpsPageRequest): # 编辑剧集页
        await edit_eps_page.generate_page(top)
    elif isinstance(top, EditCollectionTagsPageRequest): # 编辑标签页
        await edit_collection_type_page.collection_tags_page(top)
    elif isinstance(top, WeekRequest): # 每日放送
        await week_page.generate_page(top)
    elif isinstance(top, DoEditRatingRequest): # 编辑评分
        await edit_rating_page.do(top)
        callback_text = top.callback_text
        del session.stack[-2:]  # 删除最后两个
        session.stack.append(BackRequest(session, True))
        await request_handler(session)
    elif isinstance(top, DoEditEpisodeRequest): # 编辑剧集收藏
        await edit_eps_page.do(top)
        callback_text = top.callback_text
        del session.stack[-1]
        session.stack.append(BackRequest(session, True))
        await request_handler(session)
    elif isinstance(top, DoEditCollectionTypeRequest): # 编辑收藏状态
        await edit_collection_type_page.do(top)
        callback_text = top.callback_text
        del session.stack[-1]
        session.stack.append(BackRequest(session, True))
        await request_handler(session)
    elif isinstance(top, BackRequest): # 返回上一页
        del session.stack[-2:]  # 删除最后两个
        if top.needs_refresh:
            session.stack.append(RefreshRequest(session))
            await request_handler(session)
    elif isinstance(top, RefreshRequest): # 刷新当前页
        del session.stack[-1]  # 删除这个请求
        top = session.stack[-1]
        top.page_text = None
        top.page_image = None
        top.page_markup = None
        top.possible_request = {}
        await request_handler(session)
    return callback_text