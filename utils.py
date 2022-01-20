import json
import random
import threading
from typing import Optional

import math
import redis
import requests
import telebot

from config import REDIS_HOST, REDIS_PORT, REDIS_DATABASE

# FIXME 似乎不应该在这里创建对象
redis_cli = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DATABASE)


def gender_week_message(day):
    """每日放送查询页"""
    try:
        r = requests.get(url='https://api.bgm.tv/calendar')
    except requests.ConnectionError:
        r = requests.get(url='https://api.bgm.tv/calendar')
    if r.status_code != 200:
        return {'text': "出错了!", 'markup': None}
    week_data = json.loads(r.text)
    for i in week_data:
        if i.get('weekday', {}).get('id') == int(day):
            items = i.get('items')
            air_weekday = i.get('weekday', {}).get('cn')
            anime_count = len(items)
            markup = telebot.types.InlineKeyboardMarkup()
            week_text_data = ""
            nums = range(1, anime_count + 1)
            button_list = []
            for item, num in zip(items, nums):
                week_text_data += f'*[{num}]* {item["name_cn"] if item["name_cn"] else item["name"]}\n\n'
                button_list.append(telebot.types.InlineKeyboardButton(
                    text=str(num), callback_data=f"animesearch|week|{item['id']}|{day}|0"))
            text = f'*在{air_weekday}放送的节目*\n\n{week_text_data}' \
                   f'共{anime_count}部'
            markup.add(*button_list, row_width=5)
            return {'text': text, 'markup': markup}


def gander_anime_message(call_tg_id, subject_id, tg_id: Optional[int] = None, user_rating: Optional[dict] = None,
                         eps_data: Optional[dict] = None, back_page: Optional[str] = None,
                         eps_id: Optional[int] = None, start: Optional[int] = None,
                         anime_search_keywords: Optional[str] = None):
    """动画详情页"""
    subject_info = get_subject_info(subject_id)
    text = f"*{subject_info['name_cn']}*\n" \
           f"{subject_info['name']}\n\n" \
           f"BGM ID：`{subject_id}`\n"
    if subject_info and 'rating' in subject_info and 'score' in subject_info['rating']:
        text += f"➤ BGM 平均评分：`{subject_info['rating']['score']}`🌟\n"
    else:
        text += f"➤ BGM 平均评分：暂无评分\n"
    if user_rating:
        if 'rating' in user_rating:
            if user_rating['rating'] == 0:
                text += f"➤ 您的评分：暂未评分\n"
            else:
                text += f"➤ 您的评分：`{user_rating['rating']}`🌟\n"
    else:
        text += f"➤ 集数：共`{subject_info['eps']}`集\n"
    text += f"➤ 放送类型：`{subject_info['platform']}`\n" \
            f"➤ 放送开始：`{subject_info['date']}`\n"
    if subject_info["_air_weekday"]:
        text += f"➤ 放送星期：`{subject_info['_air_weekday']}`\n"
    if eps_data is not None:
        text += f"➤ 观看进度：`{eps_data['progress']}`\n"
    if user_rating and user_rating['tag'] and len(user_rating['tag']) == 1 and user_rating['tag'][0] == "":
        user_rating['tag'] = []  # 鬼知道为什么没标签会返回个空字符串
    if subject_info['tags'] and len(subject_info['tags']) == 1 and subject_info['tags'][0] == "":
        subject_info['tags'] = []
    if (user_rating and user_rating['tag']) or (subject_info['tags']):
        text += f"➤ 标签："
    if user_rating and user_rating['tag']:
        for tag in user_rating['tag'][:10]:
            text += f"#{'x' if tag.isdecimal() else ''}{tag} "
        if subject_info['tags']:
            tag_not_click = [i for i in subject_info['tags'] if i['name'] not in user_rating['tag']]
        else:
            tag_not_click = []
    else:
        tag_not_click = subject_info['tags']
    if tag_not_click and tag_not_click[0]:
        # 如果有列表
        if not (user_rating and user_rating['tag']):
            # 如果没有用户标签
            if tag_not_click and tag_not_click[0]:
                for tag in tag_not_click[:10]:
                    text += f"`{tag['name']}` "
        if user_rating and user_rating['tag'] and len(user_rating['tag']) < 10:
            # 有用户标签 但 用户标签数小于10
                for tag in tag_not_click[:10 - len(user_rating['tag'])]:
                    text += f"`{tag['name']}` "
        if (user_rating and user_rating['tag']) or (subject_info['tags']):
            text += "\n"
    text += f"\n📖 [详情](https://bgm.tv/subject/{subject_id})" \
            f"\n💬 [吐槽箱](https://bgm.tv/subject/{subject_id}/comments)"
    markup = telebot.types.InlineKeyboardMarkup()
    if eps_data is not None:
        unwatched_id = eps_data['unwatched_id']
        if not unwatched_id:
            markup.add(telebot.types.InlineKeyboardButton(
                text='返回', callback_data=f'anime_do_page|{tg_id}|{back_page}'),
                telebot.types.InlineKeyboardButton(
                    text='评分', callback_data=f'rating|{tg_id}|0|{subject_id}|{back_page}'))
            if eps_id is not None:
                markup.add(telebot.types.InlineKeyboardButton(text='收藏管理', callback_data=f'collection|{call_tg_id}|{subject_id}|anime_do|0|null|{back_page}'),
                           telebot.types.InlineKeyboardButton(text='撤销最新观看', callback_data=f'anime_eps|{tg_id}|{eps_id}|{subject_id}|{back_page}|remove'))
            else:
                markup.add(telebot.types.InlineKeyboardButton(text='收藏管理', callback_data=f'collection|{call_tg_id}|{subject_id}|anime_do|0|null|{back_page}'))
        else:
            markup.add(telebot.types.InlineKeyboardButton(text='返回', callback_data=f'anime_do_page|{tg_id}|{back_page}'),
                       telebot.types.InlineKeyboardButton(text='评分', callback_data=f'rating|{tg_id}|0|{subject_id}|{back_page}'),
                       telebot.types.InlineKeyboardButton(text='已看最新', callback_data=f'anime_eps|{tg_id}|{unwatched_id[0]}|{subject_id}|{back_page}'))
            if eps_id is not None and eps_data['watched'] != 1:
                markup.add(telebot.types.InlineKeyboardButton(text='收藏管理', callback_data=f'collection|{call_tg_id}|{subject_id}|anime_do|0|null|{back_page}'),
                           telebot.types.InlineKeyboardButton(text='撤销最新观看', callback_data=f'anime_eps|{tg_id}|{eps_id}|{subject_id}|{back_page}|remove'))
            else:
                markup.add(telebot.types.InlineKeyboardButton(text='收藏管理', callback_data=f'collection|{call_tg_id}|{subject_id}|anime_do|0|null|{back_page}'))
        if eps_id is not None:
            text += f"\n📝 [第{eps_data['watched']}话评论](https://bgm.tv/ep/{eps_id})\n"
    elif anime_search_keywords is not None:
        if anime_search_keywords == 'week':
            markup.add(telebot.types.InlineKeyboardButton(text='返回', callback_data=f'back_week|{start}'),
                       telebot.types.InlineKeyboardButton(text='收藏', callback_data=f'collection|{call_tg_id}|{subject_id}|{anime_search_keywords}|{start}|null'))
        else:
            markup.add(telebot.types.InlineKeyboardButton(text='返回', callback_data=f'spage|{anime_search_keywords}|{start}'),
                       telebot.types.InlineKeyboardButton(text='收藏', callback_data=f'collection|{call_tg_id}|{subject_id}|{anime_search_keywords}|{start}|null'))
    return {'text': text, 'markup': markup}


def grnder_rating_message(tg_id, subject_id, eps_data, user_rating, back_page):
    """评分页"""
    subject_info = get_subject_info(subject_id)
    text = {f"*{subject_info['name_cn']}*\n"
            f"{subject_info['name']}\n\n"
            f"BGM ID：`{subject_id}`\n\n"
            f"➤ BGM 平均评分：`{subject_info['rating']['score']}`🌟\n"
            f"➤ 您的评分：`{user_rating['rating']}`🌟\n\n"
            f"➤ 观看进度：`{eps_data['progress']}`\n\n"
            f"💬 [吐槽箱](https://bgm.tv/subject/{subject_id}/comments)\n\n"
            f"请点按下列数字进行评分"}
    markup = telebot.types.InlineKeyboardMarkup()
    nums = range(1, 11)
    button_list = []
    for num in nums:
        button_list.append(telebot.types.InlineKeyboardButton(
            text=str(num), callback_data=f'rating|{tg_id}|{num}|{subject_id}|{back_page}'))
    markup.add(*button_list, row_width=5)
    markup.add(telebot.types.InlineKeyboardButton(
        text='返回', callback_data=f'anime_do|{tg_id}|{subject_id}|1|{back_page}'))
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
    # 循环查询 将条目信息数据存进去 多线程获取
    thread_list = []
    for info in subject_list:
        th = threading.Thread(target=get_subject_info, args=[info['subject_id'], info])
        th.start()
        thread_list.append(th)
    for th in thread_list:
        th.join()
    # 开始处理Telegram消息
    # 拼接字符串
    markup = telebot.types.InlineKeyboardMarkup()
    anime_text_data = ""
    nums = range(1, len(subject_list) + 1)
    nums_unicode = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
    button_list = []
    for info, num, nums_unicode in zip(subject_list, nums, nums_unicode):
        anime_text_data += f'*{nums_unicode}* {info["subject_info"]["name_cn"] if info["subject_info"]["name_cn"] else info["subject_info"]["name"]}' \
                           f' `[{info["ep_status"]}/{info["subject_info"]["total_episodes"]}]`\n\n'
        button_list.append(telebot.types.InlineKeyboardButton(
            text=num, callback_data=f"anime_do|{tg_id}|{info['subject_id']}|0|{offset}"))
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
    """获取用户指吧定条目收藏信息 token 和tg_id须传一个"""
    if token == "":
        if tg_id == "":
            raise ValueError("参数错误,token 和tg_id须传一个")
        from bot import user_data_get
        token = user_data_get(tg_id).get('access_token')
    if subject_id is None or subject_id == "":
        raise ValueError("subject_id不能为空")
    headers = {'Authorization': f'Bearer {token}'}
    url = f"https://api.bgm.tv/collection/{subject_id}"
    try:
        r = requests.get(url=url, headers=headers)
    except requests.ConnectionError:
        r = requests.get(url=url, headers=headers)
    return json.loads(r.text)


def get_subject_info(subject_id, t_dict=None):
    """获取指定条目信息 并使用Redis缓存"""
    subject = redis_cli.get(f"subject:{subject_id}")
    if subject:
        loads = json.loads(subject)
    elif subject == "None__":
        raise FileNotFoundError(f"subject_id:{subject_id}获取失败_缓存")
    else:
        url = f'https://api.bgm.tv/v0/subjects/{subject_id}'
        try:
            r = requests.get(url=url)
        except requests.ConnectionError:
            r = requests.get(url=url)
        if r.status_code != 200:
            redis_cli.set(f"subject:{subject_id}", "None__", ex=60 * 10)  # 不存在时 防止缓存穿透
            raise FileNotFoundError(f"subject_id:{subject_id}获取失败")
        loads = json.loads(r.text)
        loads['_air_weekday'] = None
        for info in loads['infobox']:
            if info['key'] == '放送星期':
                loads['_air_weekday'] = info['value']  # 加一个下划线 用于区别
                break
        redis_cli.set(f"subject:{subject_id}", json.dumps(loads), ex=60 * 60 * 24 + random.randint(-3600, 3600))
    if t_dict:
        t_dict["subject_info"] = loads
    return loads


def anime_img(subject_id):
    """动画简介图片获取 不需Access Token 并使用Redis缓存"""
    img_url = redis_cli.get(f"anime_img:{subject_id}")
    if img_url:
        return img_url.decode()
    if img_url == "None__":
        return None
    anime_name = get_subject_info(subject_id)['name']
    query = '''
    query ($id: Int, $page: Int, $perPage: Int, $search: String) {
        Page (page: $page, perPage: $perPage) {
            pageInfo {
                total
                currentPage
                lastPage
                hasNextPage
                perPage
            }
            media (id: $id, search: $search) {
                id
                title {
                    romaji
                }
            }
        }
    }
    '''
    variables = {
        'search': anime_name,
        'page': 1,
        'perPage': 1
    }
    url = 'https://graphql.anilist.co'
    try:
        r = requests.post(url, json={'query': query, 'variables': variables})
    except requests.ConnectionError:
        r = requests.post(url, json={'query': query, 'variables': variables})
    anilist_data = json.loads(r.text).get('data').get('Page').get('media')
    if len(anilist_data) > 0:
        img_url = f'https://img.anili.st/media/{anilist_data[0]["id"]}'
        redis_cli.set(f"anime_img:{subject_id}", img_url, ex=60 * 60 * 24 + random.randint(-3600, 3600))
        return img_url
    else:
        redis_cli.set(f"anime_img:{subject_id}", "None__", ex=60 * 10)  # 不存在时 防止缓存穿透
        return None
