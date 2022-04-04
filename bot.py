#!/usr/bin/python
"""
BangumiTelegramBot 在 Telegram 上简单操作 Bangumi

https://github.com/Ukenn2112/BangumiTelegramBot

"""
import logging
import pickle
import re
import time

import telebot

import config
from config import BOT_TOKEN
from model.exception import TokenExpired
from model.page_model import RequestSession, WeekRequest, SubjectRequest, CollectionsRequest, SummaryRequest, \
    BackRequest, \
    EditCollectionTypePageRequest, DoEditCollectionTypeRequest, EditRatingPageRequest, DoEditRatingRequest, \
    RefreshRequest, BaseRequest, SubjectEpsPageRequest, EditEpsPageRequest, DoEditEpisodeRequest, \
    SubjectRelationsPageRequest
from plugins import start, help, week, info, search, collection_list, unbind
from plugins.callback import edit_rating_page, week_page, subject_page, \
    collection_list_page, summary_page, edit_collection_type_page, subject_eps_page, edit_eps_page, \
    subject_relations_page
from plugins.inline import sender, public, mybgm
from utils.api import create_sql, post_eps_reply, run_continuously, redis_cli, user_data_delete
from utils.converts import convert_telegram_message_to_bbcode

logger = telebot.logger
if 'LOG_LEVEL' in dir(config):
    telebot.logger.setLevel(config.LOG_LEVEL.upper())
    logging.getLogger().setLevel(config.LOG_LEVEL.upper())
else:
    telebot.logger.setLevel(logging.INFO)
    logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s - %(filename)s & %(funcName)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                    handlers=[logging.FileHandler("run.log", encoding="UTF-8"), logging.StreamHandler()])
# 请求TG Bot api
bot = telebot.TeleBot(BOT_TOKEN)


# 查询/绑定 Bangumi ./plugins/start
@bot.message_handler(commands=['start'])
def send_start(message):
    start.send(message, bot)


@bot.message_handler(commands=['unbind'])
def send_unbind(message):
    unbind.send(message, bot)


# 使用帮助 ./plugins/help
@bot.message_handler(commands=['help'])
def send_help(message):
    help.send(message, bot)


# 查询 Bangumi 用户在看book ./plugins/doing_page
@bot.message_handler(commands=['book'])
def send_book(message):
    collection_list.send(message, bot, 1)


# 查询 Bangumi 用户在看anime ./plugins/doing_page
@bot.message_handler(commands=['anime'])
def send_anime(message):
    collection_list.send(message, bot, 2)


# 查询 Bangumi 用户在玩 game ./plugins/doing_page
@bot.message_handler(commands=['game'])
def send_game(message):
    collection_list.send(message, bot, 4)


# 查询 Bangumi 用户在看 real ./plugins/doing_page
@bot.message_handler(commands=['real'])
def send_real(message):
    collection_list.send(message, bot, 6)


# 每日放送查询 ./plugins/week
@bot.message_handler(commands=['week'])
def send_week(message):
    week.send(message, bot)


# 搜索引导指令 ./plugins/search
@bot.message_handler(commands=['search'])
def send_search_details(message):
    search.send(message, bot)


# 根据subjectId 返回对应条目信息 ./plugins/info
@bot.message_handler(commands=['info'])
def send_subject_info(message):
    info.send(message, bot)


# 关闭对话
@bot.message_handler(commands=['close'])
def close_message(message):
    if message.reply_to_message is None:
        return bot.send_message(message.chat.id, "错误使用, 请回复需要关闭的对话", parse_mode='Markdown',
                                reply_to_message_id=message.message_id)
    else:
        if bot.get_me().id == message.reply_to_message.from_user.id:
            bot.delete_message(
                message.chat.id, message_id=message.reply_to_message.message_id)
            msg = bot.send_message(
                message.chat.id, "已关闭该对话", parse_mode='Markdown', reply_to_message_id=message.message_id)
            bot.delete_message(message.chat.id, message_id=message.message_id)
            time.sleep(5)
            return bot.delete_message(message.chat.id, message_id=msg.id)


@bot.message_handler(regexp=r'(bgm\.tv|bangumi\.tv|chii\.in)/subject/([0-9]+)')
def link_subject_info(message):
    for i in re.findall(r'(bgm\.tv|bangumi\.tv|chii\.in)/subject/([0-9]+)', message.text, re.I | re.M):
        info.send(message, bot, i[1])


# 章节评论
@bot.message_handler(chat_types=['private'], func=lambda message: message.reply_to_message is not None)
def send_reply(message):
    if message.reply_to_message.from_user.username != config.BOT_USERNAME:
        return
    for i in re.findall(r'(EP ID： )([0-9]+)', str(message.reply_to_message.text), re.I | re.M):
        try:
            text = message.text
            text = convert_telegram_message_to_bbcode(text, message.entities)
            post_eps_reply(message.from_user.id, i[1], text)
        except:
            bot.send_message(message.chat.id,
                             "*发送评论失败\n(可能未添加 Cookie 或者 Cookie 已过期)* \n请使用 `/start <Cookie>` 来添加或更新 Cookie",
                             parse_mode='Markdown', reply_to_message_id=message.message_id)
            raise
        bot.send_message(message.chat.id, "发送评论成功",
                         reply_to_message_id=message.message_id)


# 空按钮回调处理
@bot.callback_query_handler(func=lambda call: call.data == 'None')
def callback_none(call):
    bot.answer_callback_query(call.id)


# # 已看最新 ./plugins/callback/add_new_eps
# @bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'add_new_eps')
# def add_new_eps_callback(call):
#     add_new_eps.callback(call, bot)


@bot.chosen_inline_handler(func=lambda chosen_inline_result: True)
def test_chosen(chosen_inline_result):
    logger.info(chosen_inline_result)


# inline 方式私聊搜索或者在任何位置搜索前使用@ ./plugins/inline/sender
@bot.inline_handler(lambda query: query.query and query.chat_type == 'sender' and not query.query.startswith('mybgm'))
def sender_query_text(inline_query):
    sender.query_sender_text(inline_query, bot)


# inline 方式公共搜索 ./plugins/inline/public
@bot.inline_handler(lambda query: query.query and query.chat_type != 'sender' and not query.query.startswith('mybgm'))
def public_query_text(inline_query):
    public.query_public_text(inline_query, bot)


# inline 方式查询个人统计 ./plugins/inline/mybgm
@bot.inline_handler(lambda query: query.query and 'mybgm' in query.query)
def mybgm_query_text(inline_query):
    mybgm.query_mybgm_text(inline_query, bot)


@bot.inline_handler(lambda query: not query.query)
def query_empty(inline_query):
    bot.answer_inline_query(
        inline_query.id, [], switch_pm_text="@BGM条目ID或关键字搜索或使用mybgm查询数据", switch_pm_parameter="None", cache_time=0)


def set_bot_command(bot_):
    """设置Bot命令"""
    commands_list = [
        telebot.types.BotCommand("help", "使用帮助"),
        telebot.types.BotCommand("start", "绑定Bangumi账号"),
        telebot.types.BotCommand("book", "Bangumi用户在读书籍"),
        telebot.types.BotCommand("anime", "Bangumi用户在看动画"),
        telebot.types.BotCommand("game", "Bangumi用户在玩游戏"),
        telebot.types.BotCommand("real", "Bangumi用户在看剧集"),
        telebot.types.BotCommand("week", "每日放送"),
        telebot.types.BotCommand("search", "搜索条目"),
        telebot.types.BotCommand("close", "关闭此对话"),
        telebot.types.BotCommand("unbind", "解除 Bangumi 账号绑定"),
    ]
    try:
        return bot_.set_my_commands(commands_list)
    except:
        pass


@bot.callback_query_handler(lambda call: True)
def global_callback_handler(call):
    data = call.data.split("|")
    redis_key = data[0]
    request_key = data[1]
    call_data = redis_cli.get(redis_key)
    if not call_data:
        bot.answer_callback_query(call.id, "您的请求不存在或已过期", cache_time=1)
        return
    # redis_cli.delete(redis_key)  # TODO 没事务 多线程下可能出问题
    session: RequestSession = pickle.loads(call_data)
    next_page = session.stack[-1].possible_request.get(request_key, None)
    if not next_page:
        bot.answer_callback_query(call.id, "您的请求出错了", cache_time=3600)
        return
    session.stack.append(next_page)
    session.call = call
    consumption_request(session)


def consumption_request(session: RequestSession):
    callback_text = None
    try:
        callback_text = request_handler(session)
        top = session.stack[-1]
    except TokenExpired:
        top = BaseRequest(session)
        top.page_text = "您的Token已过期,请重新绑定"
        user_data_delete(session.request_message.from_user.id)
        start.send(session.request_message, bot)
    except Exception as e:
        top = BaseRequest(session)
        top.page_text = "发生了未知异常QAQ"
        logging.exception(f"发生异常 session:{session.uuid}")
    if top.page_image:
        if session.bot_message.content_type == 'text':
            bot.delete_message(
                message_id=session.bot_message.message_id,
                chat_id=session.request_message.chat.id
            )
            session.bot_message = bot.send_photo(
                photo=top.page_image,
                caption=top.page_text,
                parse_mode='markdown',
                reply_markup=top.page_markup,
                chat_id=session.request_message.chat.id,
                reply_to_message_id=session.request_message.message_id
            )
        else:
            session.bot_message = bot.edit_message_media(
                media=telebot.types.InputMedia(type='photo', media=top.page_image,
                                               caption=top.page_text, parse_mode="markdown"),
                reply_markup=top.page_markup,
                message_id=session.bot_message.message_id,
                chat_id=session.request_message.chat.id
            )
    else:
        if session.bot_message.content_type == 'text':
            session.bot_message = bot.edit_message_text(
                text=top.page_text,
                reply_markup=top.page_markup,
                parse_mode='markdown',
                message_id=session.bot_message.message_id,
                chat_id=session.request_message.chat.id
            )
        else:
            bot.delete_message(
                message_id=session.bot_message.message_id,
                chat_id=session.request_message.chat.id
            )
            session.bot_message = bot.send_message(
                text=top.page_text,
                reply_markup=top.page_markup,
                parse_mode='markdown',
                chat_id=session.request_message.chat.id,
                reply_to_message_id=session.request_message.message_id
            )
    stack_call = session.call
    session.call = None
    redis_cli.set(session.uuid, pickle.dumps(session), ex=3600 * 24)
    if stack_call:
        bot.answer_callback_query(stack_call.id, text=callback_text)


def request_handler(session: RequestSession):
    callback_text = None
    top = session.stack[-1]
    if isinstance(top, WeekRequest):
        week_page.generate_page(top)
    elif isinstance(top, CollectionsRequest):
        collection_list_page.generate_page(top)
    elif isinstance(top, SubjectRequest):
        subject_page.generate_page(top)
    elif isinstance(top, SummaryRequest):
        summary_page.generate_page(top)
    elif isinstance(top, EditCollectionTypePageRequest):
        edit_collection_type_page.generate_page(top)
    elif isinstance(top, EditRatingPageRequest):
        edit_rating_page.generate_page(top)
    elif isinstance(top, SubjectEpsPageRequest):
        subject_eps_page.generate_page(top)
        if len(session.stack) > 2 and isinstance(session.stack[-2], SubjectEpsPageRequest):
            del session.stack[-2]
    elif isinstance(top, SubjectRelationsPageRequest):
        subject_relations_page.generate_page(top)
    elif isinstance(top, EditEpsPageRequest):
        edit_eps_page.generate_page(top)
    elif isinstance(top, DoEditCollectionTypeRequest):
        edit_collection_type_page.do(top, session.request_message.from_user.id)
        callback_text = top.callback_text
        del session.stack[-1]
        session.stack.append(BackRequest(session, True))
        request_handler(session)
    elif isinstance(top, DoEditRatingRequest):
        edit_rating_page.do(top, session.request_message.from_user.id)
        callback_text = top.callback_text
        del session.stack[-1]
        session.stack.append(BackRequest(session, True))
        request_handler(session)
    elif isinstance(top, DoEditEpisodeRequest):
        edit_eps_page.do(top, session.request_message.from_user.id)
        callback_text = top.callback_text
        del session.stack[-1]
        session.stack.append(BackRequest(session, True))
        request_handler(session)
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


# 开始启动
if __name__ == '__main__':
    create_sql()
    set_bot_command(bot)
    stop_run_continuously = run_continuously()
    bot.infinity_polling()
