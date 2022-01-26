import json
import logging
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


def requests_get(url, params: Optional[dict] = None, access_token: Optional[str] = None, max_retry_times: int = 3):
    """requests_get 请求"""
    r = None
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
    if access_token is not None:
        headers.update({'Authorization': 'Bearer ' + access_token})
    for num in range(max_retry_times):  # 如api请求错误 重试3次
        try:
            r = requests.get(url=url, params=params, headers=headers)
        except requests.ConnectionError as err:
            if num + 1 >= max_retry_times:
                raise
            else:
                logging.warning(f'api请求错误，重试中...{str(err)}')
    if r.status_code != 200:
        return None
    else:
        try:
            return json.loads(r.text)
        except json.JSONDecodeError:
            return None


def gender_week_message(day):
    """每日放送查询页"""
    week_data = get_calendar()
    if week_data is None:
        return {'text': "出错了!", 'markup': None}
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
            week_button_list = []
            for week_day in range(1, 8):
                week_button_list.append(telebot.types.InlineKeyboardButton(
                    text=number_to_week(week_day)[-1:],
                    callback_data=f"back_week|{week_day}" if str(week_day) != str(day) else "None"))
            markup.add(*week_button_list, row_width=7)
            return {'text': text, 'markup': markup}


def gander_anime_message(call_tg_id, subject_id, tg_id: Optional[int] = None, user_rating: Optional[dict] = None,
                         eps_data: Optional[dict] = None, back_page: Optional[str] = None,
                         eps_id: Optional[int] = None, back_week_day: Optional[int] = None,
                         back_type: Optional[str] = None):
    """动画详情页"""
    subject_info = get_subject_info(subject_id)
    subject_type = subject_info['type']
    text = f"{subject_type_to_emoji(subject_type)} *{subject_info['name_cn']}*\n" \
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
        if subject_type == 2 or subject_type == 6:  # 当类型为anime或real时
            text += f"➤ 集数：共`{subject_info['eps']}`集\n"
    if subject_type == 2 or subject_type == 6:  # 当类型为anime或real时
        if subject_type == 6:
            text += f"➤ 剧集类型：`{subject_info['platform']}`\n"
        else:
            text += f"➤ 放送类型：`{subject_info['platform']}`\n"
        text += f"➤ 放送开始：`{subject_info['date']}`\n"
        if subject_info["_air_weekday"]:
            text += f"➤ 放送星期：`{subject_info['_air_weekday']}`\n"
        if eps_data is not None:
            text += f"➤ 观看进度：`{eps_data['progress']}`\n"
    if subject_type == 1:  # 当类型为book时
        text += f"➤ 书籍类型：`{subject_info['platform']}`\n"
        for box in subject_info['infobox']:
            if box.get('key') == '页数':
                text += f"➤ 页数：共`{box['value']}`页\n"
            if box.get('key') == '作者':
                text += f"➤ 作者：`{box['value']}`\n"
            if box.get('key') == '出版社':
                text += f"➤ 出版社：`{box['value']}`\n"
        text += f"➤ 发售日期：`{subject_info['date']}`\n"
    if subject_type == 3:  # 当类型为Music时
        for box in subject_info['infobox']:
            if box.get('key') == '艺术家':
                text += f"➤ 艺术家：`{box['value']}`\n"
            if box.get('key') == '作曲':
                text += f"➤ 作曲：`{box['value']}`\n"
            if box.get('key') == '作词':
                text += f"➤ 作词：`{box['value']}`\n"
            if box.get('key') == '编曲':
                text += f"➤ 编曲：`{box['value']}`\n"
            if box.get('key') == '厂牌':
                text += f"➤ 厂牌：`{box['value']}`\n"
            if box.get('key') == '碟片数量':
                text += f"➤ 碟片数量：`{box['value']}`\n"
            if box.get('key') == '播放时长':
                text += f"➤ 播放时长：`{box['value']}`\n"
            if box.get('key') == '价格':
                text += f"➤ 价格：`{box['value']}`\n"
        text += f"➤ 发售日期：`{subject_info['date']}`\n"
    if subject_type == 4:  # 当类型为Game时
        for box in subject_info['infobox']:
            if box.get('key') == '游戏类型':
                text += f"➤ 游戏类型：`{box['value']}`\n"
            if box.get('key') == '游玩人数':
                text += f"➤ 游玩人数：`{box['value']}`\n"
            if box.get('key') == '平台':
                if isinstance(box['value'], list):
                    text += f"➤ 平台："
                    for price in box['value']:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"➤ 平台：`{box['value']}`\n"
            if box.get('key') == '发行':
                text += f"➤ 发行：`{box['value']}`\n"
            if box.get('key') == '售价':
                if isinstance(box['value'], list):
                    text += f"➤ 售价："
                    for price in box['value']:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"➤ 售价：`{box['value']}`\n"
        text += f"➤ 发行日期：`{subject_info['date']}`\n"
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
                text='返回', callback_data=f'anime_do_page|{tg_id}|{back_page}|{subject_type}'),
                telebot.types.InlineKeyboardButton(
                text='评分', callback_data=f'rating|{tg_id}|0|{subject_id}|{back_page}'))
            if eps_id is not None:
                markup.add(telebot.types.InlineKeyboardButton(text='收藏管理',
                                                              callback_data=f'collection|{call_tg_id}|{subject_id}|anime_do|0|null|{back_page}'),
                           telebot.types.InlineKeyboardButton(text='撤销最新观看',
                                                              callback_data=f'anime_eps|{tg_id}|{eps_id}|{subject_id}|{back_page}|remove'))
            else:
                markup.add(telebot.types.InlineKeyboardButton(text='收藏管理',
                                                              callback_data=f'collection|{call_tg_id}|{subject_id}|anime_do|0|null|{back_page}'))
        else:
            markup.add(
                telebot.types.InlineKeyboardButton(text='返回', callback_data=f'anime_do_page|{tg_id}|{back_page}|{subject_type}'),
                telebot.types.InlineKeyboardButton(text='评分',
                                                   callback_data=f'rating|{tg_id}|0|{subject_id}|{back_page}'),
                telebot.types.InlineKeyboardButton(text='已看最新',
                                                   callback_data=f'anime_eps|{tg_id}|{unwatched_id[0]}|{subject_id}|{back_page}'))
            if eps_id is not None and eps_data['watched'] != 1:
                markup.add(telebot.types.InlineKeyboardButton(text='收藏管理',
                                                              callback_data=f'collection|{call_tg_id}|{subject_id}|anime_do|0|null|{back_page}'),
                           telebot.types.InlineKeyboardButton(text='撤销最新观看',
                                                              callback_data=f'anime_eps|{tg_id}|{eps_id}|{subject_id}|{back_page}|remove'))
            else:
                markup.add(telebot.types.InlineKeyboardButton(text='收藏管理',
                                                              callback_data=f'collection|{call_tg_id}|{subject_id}|anime_do|0|null|{back_page}'))
        if eps_id is not None:
            text += f"\n📝 [第{eps_data['watched']}话评论](https://bgm.tv/ep/{eps_id})\n"
    elif back_type is not None:
        if back_type == 'week':
            markup.add(telebot.types.InlineKeyboardButton(text='返回', callback_data=f'back_week|{back_week_day}'),
                       telebot.types.InlineKeyboardButton(text='简介', callback_data=f'summary|{subject_id}|{back_week_day}'),
                       telebot.types.InlineKeyboardButton(text='收藏',
                                                          callback_data=f'collection|{call_tg_id}|{subject_id}|{back_type}|{back_week_day}|null'))
        else:
            markup.add(telebot.types.InlineKeyboardButton(text='收藏',
                                                          callback_data=f'collection|{call_tg_id}|{subject_id}|{back_type}|0|null'),
                       telebot.types.InlineKeyboardButton(text='简介', callback_data=f'summary|{subject_id}'))
    return {'text': text, 'markup': markup, 'subject_info': subject_info}


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


def grnder_summary_message(subject_id, week_day: Optional[str] = None):
    """简介页"""
    subject_info = get_subject_info(subject_id)
    text = {f"{subject_type_to_emoji(subject_info['type'])} *{subject_info['name_cn']}*\n"
            f"{subject_info['name']}\n\n"
            f"*➤ 简介：*\n"
            f"{subject_info['summary']}\n"
            f"\n📖 [详情](https://bgm.tv/subject/{subject_id})"
            f"\n💬 [吐槽箱](https://bgm.tv/subject/{subject_id}/comments)"}
    markup = telebot.types.InlineKeyboardMarkup()
    if week_day != 0:
        markup.add(telebot.types.InlineKeyboardButton(
            text='返回', callback_data=f'animesearch|week|{subject_id}|{week_day}|1'))
    else:
        markup.add(telebot.types.InlineKeyboardButton(
            text='返回', callback_data=f'animesearch|search|{subject_id}|0|1'))
    return {'text': text, 'markup': markup}


def gender_anime_page_message(user_data, offset, tg_id, subject_type: int):
    bgm_id = user_data.get('user_id')
    access_token = user_data.get('access_token')
    # 查询用户名 TODO 将用户数据放入数据库
    user_data = requests_get(url=f'https://api.bgm.tv/user/{bgm_id}')
    if user_data is None:
        return {'text': '出错了', 'markup': None}
    if isinstance(user_data, dict) and user_data.get('code') == 404:
        return {'text': '出错了，没有查询到该用户', 'markup': None}
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
    response = requests_get(url=url, params=params, access_token=access_token)
    if response is None:
        return {'text': '出错啦，您貌似没有此状态类型的收藏', 'markup': None}
    anime_count = response.get('total')  # 总在看数 int
    subject_list = response['data']
    if subject_list is None or len(subject_list) == 0:  # 是否有数据
        return {'text': '出错啦，您貌似没有此状态类型的收藏', 'markup': None}
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
    if subject_type == 1:
        text = f'*{nickname} 在读的书籍*\n\n{anime_text_data}' \
               f'共{anime_count}本'
    if subject_type == 2:
        text = f'*{nickname} 在看的动画*\n\n{anime_text_data}' \
               f'共{anime_count}部'
    if subject_type == 3:
        text = f'*{nickname} 在听的音乐*\n\n{anime_text_data}' \
               f'共{anime_count}张'
    if subject_type == 4:
        text = f'*{nickname} 在玩的游戏*\n\n{anime_text_data}' \
               f'共{anime_count}部'
    if subject_type == 6:
        text = f'*{nickname} 在看的剧集*\n\n{anime_text_data}' \
               f'共{anime_count}部'
    markup.add(*button_list, row_width=5)
    # 只有数量大于分页时 开启分页
    if anime_count > limit:
        button_list2 = []
        if offset - limit >= 0:
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='上一页', callback_data=f'anime_do_page|{tg_id}|{offset - limit}|{subject_type}'))
        else:
            button_list2.append(telebot.types.InlineKeyboardButton(text='这是首页', callback_data="None"))
        button_list2.append(telebot.types.InlineKeyboardButton(
            text=f'{int(offset / limit) + 1}/{math.ceil(anime_count / limit)}', callback_data="None"))
        if offset + limit < anime_count:
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='下一页', callback_data=f'anime_do_page|{tg_id}|{offset + limit}|{subject_type}'))
        else:
            button_list2.append(telebot.types.InlineKeyboardButton(text='这是末页', callback_data="None"))
        markup.add(*button_list2)
    return {'text': text, 'markup': markup}


def get_collection(subject_id: str, token: str = "", tg_id=""):
    """获取用户指吧定条目收藏信息 token 和tg_id须传一个"""
    if token == "":
        if tg_id == "":
            raise ValueError("参数错误,token 和tg_id须传一个")
        from bot import user_data_get
        token = user_data_get(tg_id).get('access_token')
    if subject_id is None or subject_id == "":
        raise ValueError("subject_id不能为空")
    url = f"https://api.bgm.tv/collection/{subject_id}"
    return requests_get(url=url, access_token=token)


def post_collection(tg_id, subject_id, status, comment=None, tags=None, rating=None, private=None):
    r"""管理收藏

    :param tg_id: Telegram 用户id
    :param subject_id: 条目id
    :param status: 状态 wish collect do on_hold dropped
    :param comment: 简评
    :param tags: 标签 以半角空格分割
    :param rating: 评分 1-10 不填默认重置为未评分
    :param private: 收藏隐私 0 = 公开 1 = 私密 不填默认为0
    :return 请求结果
    """
    from bot import user_data_get
    access_token = user_data_get(tg_id).get('access_token')
    params = {"status": status}  #
    if comment is not None:
        params['comment'] = comment
    if tags is not None:
        params['tags'] = tags
    if rating is not None:
        params['rating'] = rating
    if private is not None:
        params['private'] = private
    headers = {'Authorization': f'Bearer {access_token}'}
    url = f'https://api.bgm.tv/collection/{subject_id}/update'
    return requests.post(url=url, data=params, headers=headers)


def get_calendar() -> dict:
    """获取每日放送动漫"""
    data = redis_cli.get("calendar")
    if data:
        return json.loads(data)
    else:
        calendar = requests_get(url='https://api.bgm.tv/calendar')
        redis_cli.set("calendar", json.dumps(calendar), ex=3600)
        return calendar


def get_subject_info(subject_id, t_dict=None):
    """获取指定条目信息 并使用Redis缓存"""
    subject = redis_cli.get(f"subject:{subject_id}")
    if subject:
        loads = json.loads(subject)
    elif subject == "None__":
        raise FileNotFoundError(f"subject_id:{subject_id}获取失败_缓存")
    else:
        url = f'https://api.bgm.tv/v0/subjects/{subject_id}'
        loads = requests_get(url=url)
        if loads is None:
            redis_cli.set(f"subject:{subject_id}", "None__", ex=60 * 10)  # 不存在时 防止缓存穿透
            raise FileNotFoundError(f"subject_id:{subject_id}获取失败")
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
            media (id: $id, search: $search) {
                id
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


def search_subject(keywords: str,
                   type_: int = None,
                   response_group: str = 'small',
                   start: int = 0,
                   max_results: int = 25) -> dict:
    """搜索条目

    :param keywords: 关键词
    :param type_: 条目类型 1=book 2=anime 3=music 4=game 6=real
    :param response_group: 返回数据大小 small medium
    :param start: 开始条数
    :param max_results: 每页条数 最多 25
    """
    params = {"type": type_, "responseGroup": response_group, "start": start, "max_results": max_results}
    url = f'https://api.bgm.tv/search/subject/{keywords}'
    try:
        r = requests.get(url=url, params=params)
    except requests.ConnectionError:
        r = requests.get(url=url, params=params)
    try:
        j = json.loads(r.text)
    except:
        return {"results": 0, 'list': []}
    return j


def subject_type_to_number(subject_type: str) -> int:
    if subject_type == 'book':
        return 1
    elif subject_type == 'anime':
        return 2
    elif subject_type == 'music':
        return 3
    elif subject_type == 'game':
        return 4
    elif subject_type == 'real':
        return 6

def subject_type_to_emoji(type_: int) -> str:
    if type_ == 1:
        return "📚"
    elif type_ == 2:
        return "🌸"
    elif type_ == 3:
        return "🎵"
    elif type_ == 4:
        return "🎮"
    elif type_ == 6:
        return "📺"


def number_to_week(num: int) -> str:
    if num == 1:
        return "星期一"
    if num == 2:
        return "星期二"
    if num == 3:
        return "星期三"
    if num == 4:
        return "星期四"
    if num == 5:
        return "星期五"
    if num == 6:
        return "星期六"
    if num == 7:
        return "星期日"
    else:
        return "未知"


def parse_markdown_v2(text: str) -> str:
    return text.translate(str.maketrans(
        {'_': '\\_',
         '*': '\\*',
         '[': '\\[',
         ']': '\\]',
         '(': '\\(',
         ')': '\\)',
         '~': '\\~',
         '`': '\\`',
         '>': '\\>',
         '#': '\\#',
         '+': '\\+',
         '-': '\\-',
         '=': '\\=',
         '|': '\\|',
         '{': '\\{',
         '}': '\\}',
         '.': '\\.',
         '!': '\\!'}))


def remove_duplicate_newlines(text: str) -> str:
    """删除重行 够用就行 懒的搞正则"""
    return text.translate(str.maketrans({'\n\n': '\n', '\n\n\n': '\n'}))
