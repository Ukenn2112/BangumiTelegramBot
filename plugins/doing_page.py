"""查询 Bangumi 用户在看"""
import math
import json
import telebot
import requests
import threading

from config import BOT_USERNAME
from utils.api import get_user, user_data_get, requests_get, get_subject_info


def send(message, bot, subject_type):
    tg_id = message.from_user.id
    offset = 0
    user_data = user_data_get(tg_id)
    if user_data is None:
        # 如果未绑定 直接报错
        bot.send_message(message.chat.id,
                         f"未绑定Bangumi，请私聊使用[/start](https://t.me/{BOT_USERNAME}?start=none)进行绑定",
                         parse_mode='Markdown', timeout=20)
        return
    msg = bot.send_message(message.chat.id, "正在查询请稍候...", reply_to_message_id=message.message_id,
                           parse_mode='Markdown', timeout=20)
    try:
        page = gender_page_message(user_data, offset, tg_id, subject_type)
    except:
        bot.edit_message_text(
            text="出错了!请看日志", chat_id=message.chat.id, message_id=msg.message_id)
        raise
    bot.edit_message_text(text=page['text'], chat_id=msg.chat.id, message_id=msg.message_id, parse_mode='Markdown',
                          reply_markup=page['markup'])


def gender_page_message(user_data, offset, tg_id, subject_type: int):
    bgm_id = user_data.get('user_id')
    access_token = user_data.get('access_token')
    # 查询用户名 TODO 将用户数据放入数据库
    try:
        user_data = get_user(bgm_id)
    except FileNotFoundError:
        return {'text': "出错了，没有查询到该用户", 'markup': None}
    except json.JSONDecodeError:
        return {'text': "出错了，无法获取到您的个人信息", 'markup': None}
    nickname = user_data.get('nickname')
    username = user_data.get('username')
    limit = 10

    params = {
        'subject_type': subject_type,
        'type': 3,
        'limit': limit,  # 每页条数
        'offset': offset  # 开始页
    }
    url = f'https://api.bgm.tv/v0/users/{username}/collections'
    try:
        response = requests_get(url=url, params=params,
                                access_token=access_token)
    except requests.exceptions.BaseHTTPError:
        return {'text': '出错啦，您貌似没有此状态类型的收藏', 'markup': None}
    if response is None:
        return {'text': '出错啦，您貌似没有此状态类型的收藏', 'markup': None}
    count = response.get('total')  # 总在看数 int
    subject_list = response['data']
    if subject_list is None or len(subject_list) == 0:  # 是否有数据
        return {'text': '出错啦，您貌似没有此状态类型的收藏', 'markup': None}
    # 循环查询 将条目信息数据存进去 多线程获取
    thread_list = []
    for info in subject_list:
        th = threading.Thread(target=get_subject_info, args=[
                              info['subject_id'], info])
        th.start()
        thread_list.append(th)
    for th in thread_list:
        th.join()
    # 开始处理Telegram消息
    # 拼接字符串
    markup = telebot.types.InlineKeyboardMarkup()
    text_data = ""
    nums = range(1, len(subject_list) + 1)
    nums_unicode = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
    button_list = []
    for info, num, nums_unicode in zip(subject_list, nums, nums_unicode):
        if info.get('subject_info') is not None:
            text_data += f'*{nums_unicode}* {info["subject_info"]["name_cn"] if info["subject_info"]["name_cn"] else info["subject_info"]["name"]}' \
                f' `[{info["ep_status"]}/{info["subject_info"]["total_episodes"]}]`\n\n'
            button_list.append(telebot.types.InlineKeyboardButton(
                text=num, callback_data=f"now_do|{tg_id}|{info['subject_id']}|0|{offset}"))
    if subject_type == 1:
        text = f'*{nickname} 在读的书籍*\n\n{text_data}' \
               f'共{count}本'
    elif subject_type == 2:
        text = f'*{nickname} 在看的动画*\n\n{text_data}' \
               f'共{count}部'
    elif subject_type == 3:
        text = f'*{nickname} 在听的音乐*\n\n{text_data}' \
               f'共{count}张'
    elif subject_type == 4:
        text = f'*{nickname} 在玩的游戏*\n\n{text_data}' \
               f'共{count}部'
    elif subject_type == 6:
        text = f'*{nickname} 在看的剧集*\n\n{text_data}' \
               f'共{count}部'
    else:
        raise
    markup.add(*button_list, row_width=5)
    # 只有数量大于分页时 开启分页
    if count > limit:
        button_list2 = []
        if offset - limit >= 0:
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='上一页', callback_data=f'do_page|{tg_id}|{offset - limit}|{subject_type}'))
        else:
            button_list2.append(telebot.types.InlineKeyboardButton(
                text='这是首页', callback_data="None"))
        button_list2.append(telebot.types.InlineKeyboardButton(
            text=f'{int(offset / limit) + 1}/{math.ceil(count / limit)}', callback_data="None"))
        if offset + limit < count:
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='下一页', callback_data=f'do_page|{tg_id}|{offset + limit}|{subject_type}'))
        else:
            button_list2.append(telebot.types.InlineKeyboardButton(
                text='这是末页', callback_data="None"))
        markup.add(*button_list2)
    return {'text': text, 'markup': markup}
