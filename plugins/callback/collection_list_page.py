"""查询 Bangumi 用户在看"""

import threading

import math
import requests
import telebot

from model.page_model import CollectionsRequest, SubjectRequest, BackRequest
from utils.api import requests_get, get_subject_info


def generate_page(request: CollectionsRequest, stack_uuid: str) -> CollectionsRequest:
    access_token = request.user_data['_user']['access_token']
    nickname = request.user_data.get('nickname')
    username = request.user_data.get('username')
    subject_type = request.subject_type
    limit = request.limit
    offset = request.offset
    params = {
        'subject_type': subject_type,
        'type': request.collection_type,
        'limit': limit,  # 每页条数
        'offset': offset  # 开始页
    }
    url = f'https://api.bgm.tv/v0/users/{username}/collections'
    try:
        response = requests_get(url=url, params=params,
                                access_token=access_token)
    except requests.exceptions.BaseHTTPError:
        request.page_text = '出错啦，您貌似没有此状态类型的收藏'
        return request
    if response is None:
        request.page_text = '出错啦，您貌似没有此状态类型的收藏'
        return request
    count = response.get('total')  # 总在看数 int
    subject_list = response['data']
    if subject_list is None or len(subject_list) == 0:  # 是否有数据
        request.page_text = '出错啦，您貌似没有此状态类型的收藏'
        return request
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
    text_data = ""
    nums = range(1, len(subject_list) + 1)
    nums_unicode = ['①', '②', '③', '④', '⑤', '⑥', '⑦', '⑧', '⑨', '⑩']
    button_list = []
    for info, num, nums_unicode in zip(subject_list, nums, nums_unicode):
        epssssss = info["subject_info"]["eps"]
        if not epssssss:
            epssssss = info["subject_info"]["total_episodes"]
        text_data += f'*{nums_unicode}* {info["subject_info"]["name_cn"] if info["subject_info"]["name_cn"] else info["subject_info"]["name"]}' \
                     f' `[{info["ep_status"]}/{epssssss}]`\n\n'
        button_list.append(telebot.types.InlineKeyboardButton(
            text=num, callback_data=f"{stack_uuid}|{nums_unicode}"))
        request.possible_request[nums_unicode] = SubjectRequest(str(info['subject_id']), user_data=request.user_data)
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
            # button_list2.append(
            #     telebot.types.InlineKeyboardButton(text='上一页', callback_data=f'{stack_uuid}|{offset - limit}'))
            # request.possible_request[str(offset - limit)] = \
            #     CollectionsRequest(request.user_data, subject_type,
            #                        offset=offset - limit,
            #                        collection_type=request.collection_type,
            #                        limit=limit)
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='上一页', callback_data=f'{stack_uuid}|back'))
            request.possible_request["back"] = BackRequest()
        else:
            button_list2.append(telebot.types.InlineKeyboardButton(
                text='这是首页', callback_data="None"))
        button_list2.append(telebot.types.InlineKeyboardButton(
            text=f'{int(offset / limit) + 1}/{math.ceil(count / limit)}', callback_data="None"))
        if offset + limit < count:
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='下一页', callback_data=f'{stack_uuid}|{offset + limit}'))
            request.possible_request[str(offset + limit)] = \
                CollectionsRequest(request.user_data, subject_type,
                                   offset=+limit,
                                   collection_type=request.collection_type,
                                   limit=limit)
        else:
            button_list2.append(telebot.types.InlineKeyboardButton(text='这是末页', callback_data="None"))
        markup.add(*button_list2)
    request.page_text = text
    request.page_markup = markup
    return request
