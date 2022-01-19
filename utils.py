import json

import math
import requests
import telebot


def gender_week_message(msg, bot, day):
    """每日放送查询页"""
    try:
        r = requests.get(url='https://api.bgm.tv/calendar')
    except requests.ConnectionError:
        r = requests.get(url='https://api.bgm.tv/calendar')
    if r.status_code != 200:
        bot.edit_message_text(text="出错了!", chat_id=msg.chat.id, message_id=msg.message_id)
        return
    week_data = json.loads(r.text)
    for i in week_data:
        if i.get('weekday', {}).get('id') == int(day):
            items = i.get('items')
            subject_id_li = [i['id'] for i in items]
            name_li = [i['name'] for i in items]
            name_cn_li = [i['name_cn'] for i in items]
            air_weekday = i.get('weekday', {}).get('cn')
            anime_count = len(subject_id_li)
            markup = telebot.types.InlineKeyboardMarkup()
            week_text_data = ""
            nums = list(range(1, len(subject_id_li) + 1))
            button_list = []
            for subject_id_li, name_li, name_cn_li, nums in zip(subject_id_li, name_li, name_cn_li, nums):
                week_text_data += f'*[{nums}]* {name_cn_li if name_cn_li else name_li}\n\n'
                button_list.append(telebot.types.InlineKeyboardButton(text=nums, callback_data=
                f"animesearch|week|{subject_id_li}|{day}|0"))
            text = f'*在{air_weekday}放送的节目*\n\n{week_text_data}' \
                   f'共{anime_count}部'
            markup.add(*button_list, row_width=4)
    return {'text': text, 'markup': markup}

def gander_anime_do_message(call_tg_id, tg_id, subject_id, back_page, subject_info, user_rating, eps_data):
    """动画在看详情页"""
    unwatched_id = eps_data['unwatched_id']
    text = f"*{subject_info['name_cn']}*\n" \
           f"{subject_info['name']}\n\n" \
           f"BGM ID：`{subject_id}`\n" \
           f"➤ BGM 平均评分：`{subject_info['score']}`🌟\n" \
           f"➤ 您的评分：`{user_rating['user_rating']}`🌟\n" \
           f"➤ 放送类型：`{subject_info['platform']}`\n" \
           f"➤ 放送开始：`{subject_info['air_date']}`\n" \
           f"➤ 放送星期：`{subject_info['air_weekday']}`\n" \
           f"➤ 观看进度：`{eps_data['progress']}`\n\n" \
           f"💬 [吐槽箱](https://bgm.tv/subject/{subject_id}/comments)\n"
    markup = telebot.types.InlineKeyboardMarkup()
    if unwatched_id == []:
        markup.add(telebot.types.InlineKeyboardButton(text='返回',callback_data=f'anime_do_page|{tg_id}|{back_page}'),
        telebot.types.InlineKeyboardButton(text='评分',callback_data=f'rating|{tg_id}|0|{subject_id}|{back_page}'))
        markup.add(telebot.types.InlineKeyboardButton(text='收藏管理',callback_data=f'collection|{call_tg_id}|{subject_id}|anime_do|0|null|{back_page}'))
    else:
        markup.add(telebot.types.InlineKeyboardButton(text='返回',callback_data=f'anime_do_page|{tg_id}|{back_page}'),
        telebot.types.InlineKeyboardButton(text='评分',callback_data=f'rating|{tg_id}|0|{subject_id}|{back_page}'),
        telebot.types.InlineKeyboardButton(text='已看最新',callback_data=f'anime_eps|{tg_id}|{unwatched_id[0]}|{subject_id}|{back_page}'))
        markup.add(telebot.types.InlineKeyboardButton(text='收藏管理',callback_data=f'collection|{call_tg_id}|{subject_id}|anime_do|0|null|{back_page}'))
    return {'text': text, 'markup': markup}

def gender_anime_page_message(user_data, offset, tg_id):
    bgm_id = user_data.get('user_id')
    access_token = user_data.get('access_token')
    # 查询用户名 TODO 将用户数据放入数据库
    r2 = requests.get(url=f'https://api.bgm.tv/user/{bgm_id}')
    user_data = json.loads(r2.text)
    if r2.status_code != 200:
        return {'text': '出错了', 'markup': None}
    if isinstance(user_data, dict) and user_data.get('code') == 404:
        return {'text': '出错了，没有查询到该用户', 'markup': None}
    nickname = user_data.get('nickname')
    username = user_data.get('username')
    limit = 5

    params = {
        'subject_type': 2,
        'type': 3,
        'limit': limit,  # 每页条数
        'offset': offset  # 开始页
    }
    headers = {'Authorization': 'Bearer ' + access_token}
    url = f'https://api.bgm.tv/v0/users/{username}/collections'
    try:
        r = requests.get(url=url, params=params, headers=headers)
    except requests.ConnectionError:
        r = requests.get(url=url, params=params, headers=headers)
    if r.status_code != 200:
        return {'text': '出错了', 'markup': None}
    response = json.loads(r.text)
    anime_count = response.get('total')  # 总在看数 int
    subject_list = response['data']
    if subject_list is None or len(subject_list) == 0:  # 是否有数据
        return {'text': '出错啦，您貌似没有收藏的在看', 'markup': None}
        # 循环查询 将条目信息数据存进去 TODO 多线程获取
    for info in subject_list:
        from bot import subject_info_get
        subject_info = subject_info_get(info['subject_id'])
        info['subject_info'] = subject_info
    # 开始处理Telegram消息
    # 拼接字符串
    markup = telebot.types.InlineKeyboardMarkup()
    anime_text_data = ""
    nums = list(range(1, len(subject_list) + 1))
    nums_unicode = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
    button_list = []
    for info, num, nums_unicode in zip(subject_list, nums, nums_unicode):
        anime_text_data += f'*{nums_unicode}* {info["subject_info"]["name_cn"] if info["subject_info"]["name_cn"] else info["subject_info"]["name"]}' \
                           f' `[{info["ep_status"]}/{info["subject_info"]["eps_count"]}]`\n\n'
        button_list.append(telebot.types.InlineKeyboardButton(text=num, callback_data=
        f"anime_do|{tg_id}|{info['subject_id']}|0|{offset}"))
    text = f'*{nickname} 在看的动画*\n\n{anime_text_data}' \
           f'共{anime_count}部'
    markup.add(*button_list, row_width=5)
    # 只有数量大于分页时 开启分页
    if anime_count > limit:
        button_list2 = []
        if offset - limit >= 0:
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='上一页', callback_data=f'anime_do_page|{tg_id}|{offset - limit}'))
        else:
            button_list2.append(telebot.types.InlineKeyboardButton(text='这是首页', callback_data="None"))
        button_list2.append(telebot.types.InlineKeyboardButton(
            text=f'{int(offset / limit) + 1}/{math.ceil(anime_count / limit)}', callback_data="None"))
        if offset + limit < anime_count:
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='下一页', callback_data=f'anime_do_page|{tg_id}|{offset + limit}'))
        else:
            button_list2.append(telebot.types.InlineKeyboardButton(text='这是末页', callback_data="None"))
        markup.add(*button_list2)
    return {'text': text, 'markup': markup}


def search_anime(anime_search_keywords, message, bot):
    """临时方法 TODO 修改"""
    msg = bot.send_message(message.chat.id, "正在搜索请稍候...", reply_to_message_id=message.message_id, parse_mode='Markdown',
                           timeout=20)
    subject_type = 2  # 条目类型 1 = book 2 = anime 3 = music 4 = game 6 = real
    start = 0
    from bot import search_get
    search_results_n = search_get(anime_search_keywords, subject_type, start)['search_results_n']  # 搜索结果数量
    if search_results_n == 0:
        bot.send_message(message.chat.id, text='抱歉，没能搜索到您想要的内容', parse_mode='Markdown', timeout=20)
    else:
        search_subject_id_li = search_get(anime_search_keywords, subject_type, start)['subject_id_li']  # 所有查询结果id列表
        search_name_li = search_get(anime_search_keywords, subject_type, start)['name_li']  # 所有查询结果名字列表
        markup = telebot.types.InlineKeyboardMarkup()
        for item in list(zip(search_name_li, search_subject_id_li)):
            markup.add(telebot.types.InlineKeyboardButton(text=item[0], callback_data='animesearch' + '|' + str(
                anime_search_keywords) + '|' + str(item[1]) + '|' + '0' + '|0'))
        if search_results_n > 5:
            markup.add(telebot.types.InlineKeyboardButton(text='下一页', callback_data='spage' + '|' + str(
                anime_search_keywords) + '|' + '5'))

        text = {'*关于您的 “*`' + str(anime_search_keywords) + '`*” 搜索结果*\n\n' +

                '🔍 共' + str(search_results_n) + '个结果'}

        bot.delete_message(message.chat.id, message_id=msg.message_id, timeout=20)
        bot.send_message(message.chat.id, text=text, parse_mode='Markdown', reply_markup=markup, timeout=20)


def get_collection(subject_id: str, token: str = "", tg_id=""):
    """获取用户指定条目收藏信息 token 和tg_id须传一个"""
    if token == "":
        if tg_id == "":
            raise ValueError("参数错误,token 和tg_id须传一个")
        from bot import user_data_get
        token = user_data_get(tg_id).get('access_token')
    if subject_id is None or subject_id == "":
        raise ValueError("subject_id不能为空")
    params = {'subject_id': subject_id}
    headers = {'Authorization': 'Bearer ' + token}
    url = f"https://api.bgm.tv/collection/{subject_id}"
    try:
        r = requests.get(url=url, params=params, headers=headers)
    except requests.ConnectionError:
        r = requests.get(url=url, params=params, headers=headers)
    return json.loads(r.text)
