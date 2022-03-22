"""查询 Bangumi 用户在看"""
import json
import math
import threading

import requests
import telebot

from model.page_model import CollectionsRequest, SubjectRequest, BackRequest
from utils.api import requests_get, get_subject_info, get_user
from utils.converts import subject_type_to_str, collection_type_subject_type_str


def generate_page(request: CollectionsRequest) -> CollectionsRequest:
    session_uuid = request.session.uuid
    if request.user_data is None:
        try:
            request.user_data = get_user(request.session.bgm_auth['user_id'])
        except FileNotFoundError:
            request.page_text = "出错了，无法获取到您的个人信息"
            return request
        except json.JSONDecodeError:
            request.page_text = "出错了，无法获取到您的个人信息"
            return request

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
                                access_token=request.session.bgm_auth['access_token'])
    except requests.exceptions.BaseHTTPError:
        request.page_text = f'出错啦，您貌似没有{collection_type_subject_type_str(subject_type, request.collection_type)}' \
                            f'的{subject_type_to_str(subject_type)}'
        return request
    if response is None:
        request.page_text = f'出错啦，您貌似没有{collection_type_subject_type_str(subject_type, request.collection_type)}' \
                            f'的{subject_type_to_str(subject_type)}'
        return request
    count = response.get('total')  # 总在看数 int
    subject_list = response['data']
    if subject_list is None or len(subject_list) == 0:  # 是否有数据
        request.page_text = f'出错啦，您貌似没有{collection_type_subject_type_str(subject_type, request.collection_type)}' \
                            f'的{subject_type_to_str(subject_type)}'
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
        text_data += f'*{nums_unicode}* {info["subject_info"]["name_cn"] or info["subject_info"]["name"]}' \
                     f' `[{info["ep_status"]}/{epssssss}]`\n\n'
        button_list.append(telebot.types.InlineKeyboardButton(
            text=num, callback_data=f"{session_uuid}|{nums_unicode}"))
        request.possible_request[nums_unicode] = SubjectRequest(request.session, info['subject_id'])
    text = f'*{nickname} {collection_type_subject_type_str(subject_type, request.collection_type)}' \
           f'的{subject_type_to_str(subject_type)}*\n\n{text_data}' \
           f'共{count}部'
    markup.add(*button_list, row_width=5)
    # 只有数量大于分页时 开启分页
    if count > limit:
        button_list2 = []
        if offset - limit >= 0:
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='上一页', callback_data=f'{session_uuid}|back'))
            request.possible_request["back"] = BackRequest(request.session)
        else:
            button_list2.append(telebot.types.InlineKeyboardButton(
                text='这是首页', callback_data="None"))
        button_list2.append(telebot.types.InlineKeyboardButton(
            text=f'{int(offset / limit) + 1}/{math.ceil(count / limit)}', callback_data="None"))
        if offset + limit < count:
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='下一页', callback_data=f'{session_uuid}|{offset + limit}'))
            next_request = CollectionsRequest(request.session, subject_type, offset=offset + limit,
                                              collection_type=request.collection_type, limit=limit)
            request.possible_request[str(offset + limit)] = next_request
            next_request.user_data = request.user_data
        else:
            button_list2.append(telebot.types.InlineKeyboardButton(text='这是末页', callback_data="None"))
        markup.add(*button_list2)
    request.page_text = text
    request.page_markup = markup
    return request
