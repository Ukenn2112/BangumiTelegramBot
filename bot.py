#!/usr/bin/python
"""
https://bangumi.github.io/api/
"""
import logging
import pickle
import time

import telebot

from config import BOT_TOKEN
from model.page_model import RequestStack, WeekRequest, SubjectRequest, CollectionsRequest, SummaryRequest, BackRequest, \
    EditCollectionTypePageRequest, DoEditCollectionTypeRequest, EditRatingPageRequest, DoEditRatingRequest, \
    RefreshRequest, BaseRequest, SubjectEpsPageRequest, EditEpsPageRequest, DoEditEpisodeRequest
from plugins import start, help, week, info, search, collection_list
from plugins.callback import edit_rating_page, week_page, subject_page, \
    collection_list_page, summary_page, edit_collection_type_page, subject_eps_page, edit_eps_page
from plugins.inline import sender, public, mybgm
from utils.api import run_continuously, redis_cli

logger = telebot.logger
try:
    from config import LOG_LEVEL
except ImportError:
    LOG_LEVEL = "info"
if LOG_LEVEL == "info":
    telebot.logger.setLevel(logging.INFO)
if LOG_LEVEL == "debug":
    telebot.logger.setLevel(logging.DEBUG)
logging.basicConfig(filename='run.log',
                    format='%(asctime)s - %(filename)s & %(funcName)s[line:%(lineno)d] - %(levelname)s: %(message)s')
# 请求TG Bot api
bot = telebot.TeleBot(BOT_TOKEN)


# 查询/绑定 Bangumi ./plugins/start
@bot.message_handler(commands=['start'])
def send_start(message):
    start.send(message, bot)


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


# 关闭对话 ./pigins/close
@bot.message_handler(commands=['close'])
def close_message(message):
    if message.reply_to_message is None:
        return bot.send_message(message.chat.id, "错误使用, 请回复需要关闭的对话", parse_mode='Markdown', reply_to_message_id=message.message_id)
    else:
        if bot.get_me().id == message.reply_to_message.from_user.id:
            bot.delete_message(
                message.chat.id, message_id=message.reply_to_message.message_id)
            msg = bot.send_message(
                message.chat.id, "已关闭该对话", parse_mode='Markdown', reply_to_message_id=message.message_id)
            bot.delete_message(message.chat.id, message_id=message.message_id)
            time.sleep(5)
            return bot.delete_message(message.chat.id, message_id=msg.id)


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
@bot.inline_handler(lambda query: query.query and (query.chat_type == 'sender' or str.startswith(query.query, '@')) and not str.startswith(query.query, 'mybgm'))
def sender_query_text(inline_query):
    sender.query_sender_text(inline_query, bot)


# inline 方式公共搜索 ./plugins/inline/public
@bot.inline_handler(lambda query: query.query and query.chat_type != 'sender' and not str.startswith(query.query, '@') and not str.startswith(query.query, 'mybgm'))
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
        telebot.types.BotCommand("week", "空格加数字查询每日放送"),
        telebot.types.BotCommand("search", "搜索条目"),
        telebot.types.BotCommand("close", "关闭此对话"),
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
    stack: RequestStack = pickle.loads(call_data)
    next_page = stack.stack[-1].possible_request.get(request_key, None)
    if not next_page:
        bot.answer_callback_query(call.id, "您的请求出错了", cache_time=3600)
        return
    stack.stack.append(next_page)
    stack.call = call
    consumption_request(stack)


def consumption_request(stack: RequestStack):
    callback_text = None
    try:
        callback_text = request_handler(stack)
        top = stack.stack[-1]
    except:
        top = BaseRequest()
        top.page_text = "发生了未知异常😖"

    if top.page_image:
        if stack.bot_message.content_type == 'text':
            bot.delete_message(
                message_id=stack.bot_message.message_id,
                chat_id=stack.request_message.chat.id
            )
            stack.bot_message = bot.send_photo(
                photo=top.page_image,
                caption=top.page_text,
                parse_mode='markdown',
                reply_markup=top.page_markup,
                chat_id=stack.request_message.chat.id,
                reply_to_message_id=stack.request_message.message_id
            )
        else:
            stack.bot_message = bot.edit_message_media(
                media=telebot.types.InputMedia(type='photo', media=top.page_image,
                                               caption=top.page_text, parse_mode="markdown"),
                reply_markup=top.page_markup,
                message_id=stack.bot_message.message_id,
                chat_id=stack.request_message.chat.id
            )
    else:
        if stack.bot_message.content_type == 'text':
            stack.bot_message = bot.edit_message_text(
                text=top.page_text,
                reply_markup=top.page_markup,
                parse_mode='markdown',
                message_id=stack.bot_message.message_id,
                chat_id=stack.request_message.chat.id
            )
        else:
            bot.delete_message(
                message_id=stack.bot_message.message_id,
                chat_id=stack.request_message.chat.id
            )
            stack.bot_message = bot.send_message(
                text=top.page_text,
                reply_markup=top.page_markup,
                parse_mode='markdown',
                chat_id=stack.request_message.chat.id,
                reply_to_message_id=stack.request_message.message_id
            )
    stack_call = stack.call
    stack.call = None
    redis_cli.set(stack.uuid, pickle.dumps(stack), ex=3600)
    if stack_call:
        bot.answer_callback_query(stack_call.id, text=callback_text)


def request_handler(stack: RequestStack):
    callback_text = None
    top = stack.stack[-1]
    if isinstance(top, WeekRequest):
        week_page.generate_page(top, stack.uuid)
    elif isinstance(top, CollectionsRequest):
        collection_list_page.generate_page(top, stack.uuid)
    elif isinstance(top, SubjectRequest):
        is_private_tg_id = stack.request_message.from_user.id if stack.bot_message.chat.type == 'private' else 0
        subject_page.generate_page(top, stack.uuid, is_private_tg_id)
    elif isinstance(top, SummaryRequest):
        summary_page.generate_page(top, stack.uuid)
    elif isinstance(top, EditCollectionTypePageRequest):
        edit_collection_type_page.generate_page(top, stack.uuid)
    elif isinstance(top, EditRatingPageRequest):
        edit_rating_page.generate_page(top, stack.uuid)
    elif isinstance(top, SubjectEpsPageRequest):
        subject_eps_page.generate_page(top, stack.uuid)
        if len(stack.stack) > 2 and isinstance(stack.stack[-2], SubjectEpsPageRequest):
            del stack.stack[-2]
    elif isinstance(top, EditEpsPageRequest):
        edit_eps_page.generate_page(top, stack.uuid)
    elif isinstance(top, DoEditCollectionTypeRequest):
        edit_collection_type_page.do(top, stack.request_message.from_user.id)
        callback_text = top.callback_text
        del stack.stack[-1]
        stack.stack.append(BackRequest(True))
        request_handler(stack)
    elif isinstance(top, DoEditRatingRequest):
        edit_rating_page.do(top, stack.request_message.from_user.id)
        callback_text = top.callback_text
        del stack.stack[-1]
        stack.stack.append(BackRequest(True))
        request_handler(stack)
    elif isinstance(top, DoEditEpisodeRequest):
        edit_eps_page.do(top, stack.request_message.from_user.id)
        callback_text = top.callback_text
        del stack.stack[-1]
        stack.stack.append(BackRequest(True))
        request_handler(stack)
    elif isinstance(top, BackRequest):
        del stack.stack[-2:]  # 删除最后两个
        if top.needs_refresh:
            stack.stack.append(RefreshRequest())
            request_handler(stack)
    elif isinstance(top, RefreshRequest):
        del stack.stack[-1]  # 删除这个请求
        top = stack.stack[-1]
        top.page_text = None
        top.page_image = None
        top.page_markup = None
        top.possible_request = {}
        request_handler(stack)
    return callback_text


# 开始启动
if __name__ == '__main__':
    set_bot_command(bot)
    stop_run_continuously = run_continuously()
    bot.infinity_polling()
