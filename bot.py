#!/usr/bin/python
"""
https://bangumi.github.io/api/
"""
import logging
import pickle

import telebot

from config import BOT_TOKEN
from model.page_model import RequestStack, WeekRequest, SubjectRequest, CollectionsRequest, SummaryRequest, BackRequest, \
    EditCollectionTypePageRequest, DoEditCollectionTypeRequest, EditRatingPageRequest, DoEditRatingRequest, \
    RefreshRequest
from plugins import start, my, week, info, search, collection_list
from plugins.callback import edit_rating_page, week_page, subject_page, \
    collection_list_page, summary_page, edit_collection_type_page
from plugins.inline import sender, public
from utils.api import run_continuously, redis_cli

logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)  # Outputs debug messages to console.
logging.basicConfig(level=logging.INFO,
                    filename='run.log',
                    format='%(asctime)s - %(filename)s & %(funcName)s[line:%(lineno)d] - %(levelname)s: %(message)s')
# 请求TG Bot api
bot = telebot.TeleBot(BOT_TOKEN)


# 查询/绑定 Bangumi ./plugins/start
@bot.message_handler(commands=['start'])
def send_start(message):
    start.send(message, bot)


# 查询 Bangumi 用户收藏统计 ./plugins/my
@bot.message_handler(commands=['my'])
def send_my(message):
    my.send(message, bot)


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
@bot.inline_handler(lambda query: query.query and (query.chat_type == 'sender' or str.startswith(query.query, '@')))
def sender_query_text(inline_query):
    sender.query_sender_text(inline_query, bot)


# inline 方式公共搜索 ./plugins/inline/public
@bot.inline_handler(lambda query: query.query and query.chat_type != 'sender' and not str.startswith(query.query, '@'))
def public_query_text(inline_query):
    public.query_public_text(inline_query, bot)


@bot.inline_handler(lambda query: not query.query)
def query_empty(inline_query):
    bot.answer_inline_query(
        inline_query.id, [], switch_pm_text="@BGM条目ID获取信息或关键字搜索", switch_pm_parameter="None")


def set_bot_command(bot):
    """设置Bot命令"""
    commands_list = [
        telebot.types.BotCommand("my", "Bangumi收藏统计/空格加username或uid不绑定查询"),
        telebot.types.BotCommand("book", "Bangumi用户在读书籍"),
        telebot.types.BotCommand("anime", "Bangumi用户在看动画"),
        telebot.types.BotCommand("game", "Bangumi用户在玩动画"),
        telebot.types.BotCommand("real", "Bangumi用户在看剧集"),
        telebot.types.BotCommand("week", "空格加数字查询每日放送"),
        telebot.types.BotCommand("search", "搜索条目"),
        telebot.types.BotCommand("start", "绑定Bangumi账号"),
    ]
    try:
        return bot.set_my_commands(commands_list)
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
    callback_text = request_handler(stack)
    top = stack.stack[-1]

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
        subject_page.generate_page(top, stack.uuid)
    elif isinstance(top, SummaryRequest):
        summary_page.generate_page(top, stack.uuid)
    elif isinstance(top, EditCollectionTypePageRequest):
        edit_collection_type_page.generate_page(top, stack.uuid)
    elif isinstance(top, EditRatingPageRequest):
        edit_rating_page.generate_page(top, stack.uuid)
    elif isinstance(top, DoEditCollectionTypeRequest):
        edit_collection_type_page.do(top, stack.request_message.from_user.id)
        callback_text = top.callback_text
        stack.stack = stack.stack[:-1]
        stack.stack.append(BackRequest())
        request_handler(stack)
    elif isinstance(top, DoEditRatingRequest):
        edit_rating_page.do(top, stack.request_message.from_user.id)
        callback_text = top.callback_text
        stack.stack = stack.stack[:-1]
        stack.stack.append(BackRequest(True))
        request_handler(stack)
    elif isinstance(top, BackRequest):
        stack.stack = stack.stack[:-2]
        if top.needs_refresh:
            stack.stack.append(RefreshRequest())
            request_handler(stack)
    elif isinstance(top, RefreshRequest):
        stack.stack = stack.stack[:-1]
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
