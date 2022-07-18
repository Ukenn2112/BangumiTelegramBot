import math

import telebot

from model.page_model import (
    DoEditCollectionTypeRequest,
    SubjectEpsPageRequest,
    BackRequest,
    EditEpsPageRequest,
)
from utils.api import (
    get_subject_episode,
    anime_img,
    get_subject_info,
    user_collection_get,
    get_user_progress,
)
from utils.converts import subject_type_to_emoji, number_to_episode_type


def generate_page(request: SubjectEpsPageRequest) -> SubjectEpsPageRequest:
    session_uuid = request.session.uuid
    if not request.page_image:
        request.page_image = anime_img(request.subject_id)
    if not request.subject_info:
        request.subject_info = get_subject_info(request.subject_id)
    if not request.user_collection and request.session.bgm_auth:
        request.user_collection = user_collection_get(
            None, request.subject_id, request.session.bgm_auth['access_token']
        )
    id_to_emoji = {1: '👀', 2: '🔘', 3: '🗑️'}
    user_eps = {}
    if request.user_collection and 'code' not in request.user_collection:
        data = get_user_progress(request.session.request_message.from_user.id, request.subject_id)
        if data and data['eps']:
            for eps in data['eps']:
                user_eps[eps['id']] = eps['status']['id']

    subject_id = request.subject_id
    eps = get_subject_episode(
        subject_id, limit=request.limit, offset=request.offset, type_=request.type_
    )
    button_list = []
    subject_info = request.subject_info
    text = (
        f"*{subject_type_to_emoji(subject_info['type'])}"
        f"『 {subject_info['name_cn'] or subject_info['name']} 』{number_to_episode_type(request.type_)}章节列表:*\n\n"
    )
    for i in eps['data']:
        ep = str(i['Ep'])

        button_list.append(
            telebot.types.InlineKeyboardButton(text=ep, callback_data=f'{session_uuid}|{i["ID"]}')
        )
        page_request = EditEpsPageRequest(request.session, i['ID'], episode_info=i)
        request.possible_request[str(i['ID'])] = page_request

        if request.user_collection and 'code' not in request.user_collection:
            text += id_to_emoji.get(user_eps.get(i['ID'], ''), '⚪')
            page_request.before_status = user_eps.get(i['ID'], 0)
        text += f"`{ep.zfill(2)}`*.*"
        text += f" {i['NameCN'] or i['Name'] or '未公布'} \n"

    total = eps['total']
    limit = eps['limit']
    offset = request.offset
    button_list2 = []
    markup = telebot.types.InlineKeyboardMarkup()
    if total > limit:
        if offset - limit >= 0:
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='上一页', callback_data=f'{session_uuid}|pre')
            )
            pre_request = SubjectEpsPageRequest(
                request.session,
                request.subject_id,
                limit=limit,
                type_=request.type_,
                offset=offset - limit,
            )
            pre_request.user_collection = request.user_collection
            request.possible_request['pre'] = pre_request
        else:
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='这是首页', callback_data="None")
            )
        button_list2.append(
            telebot.types.InlineKeyboardButton(
                text=f'{int(offset / limit) + 1}/{math.ceil(total / limit)}', callback_data="None"
            )
        )
        if offset + limit < total:
            button_list2.append(
                telebot.types.InlineKeyboardButton(
                    text='下一页', callback_data=f'{session_uuid}|next'
                )
            )
            next_request = SubjectEpsPageRequest(
                request.session,
                request.subject_id,
                limit=limit,
                type_=request.type_,
                offset=offset + limit,
            )
            next_request.user_collection = request.user_collection
            request.possible_request['next'] = next_request
        else:
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='这是末页', callback_data="None")
            )
    if request.subject_info['type'] == 2:
        button_list3 = []
        if request.type_ != 0:
            button_list3.append(
                telebot.types.InlineKeyboardButton(text='本篇', callback_data=f"{session_uuid}|eps")
            )
            subject_eps_page_request = SubjectEpsPageRequest(
                request.session, subject_id=request.subject_id, limit=12, type_=0
            )
            subject_eps_page_request.user_collection = request.user_collection
            request.possible_request['eps'] = subject_eps_page_request
        if request.type_ != 1:
            button_list3.append(
                telebot.types.InlineKeyboardButton(text='SP', callback_data=f"{session_uuid}|eps1")
            )
            subject_eps_page_request = SubjectEpsPageRequest(
                request.session, subject_id=request.subject_id, limit=12, type_=1
            )
            subject_eps_page_request.user_collection = request.user_collection
            request.possible_request['eps1'] = subject_eps_page_request
        if request.type_ != 2:
            button_list3.append(
                telebot.types.InlineKeyboardButton(text='OP', callback_data=f"{session_uuid}|eps2")
            )
            subject_eps_page_request = SubjectEpsPageRequest(
                request.session, subject_id=request.subject_id, limit=12, type_=2
            )
            subject_eps_page_request.user_collection = request.user_collection
            request.possible_request['eps2'] = subject_eps_page_request
        if request.type_ != 3:
            button_list3.append(
                telebot.types.InlineKeyboardButton(text='ED', callback_data=f"{session_uuid}|eps3")
            )
            subject_eps_page_request = SubjectEpsPageRequest(
                request.session, subject_id=request.subject_id, limit=12, type_=3
            )
            subject_eps_page_request.user_collection = request.user_collection
            request.possible_request['eps3'] = subject_eps_page_request
        markup.add(*button_list3, row_width=3)
    markup.add(*button_list, row_width=6)
    markup.add(*button_list2)
    if (
        len(user_eps) == total
        and len(user_eps) != 0
        and request.user_collection['status']['name'] != '看过'
    ):
        markup.add(
            telebot.types.InlineKeyboardButton(
                text='将此章节收藏改为看过？', callback_data=f"{session_uuid}|collect"
            )
        )
        request.possible_request['collect'] = DoEditCollectionTypeRequest(
            request.session, request.subject_id, 'collect'
        )
    markup.add(telebot.types.InlineKeyboardButton(text='返回', callback_data=f"{session_uuid}|back"))
    request.possible_request['back'] = BackRequest(request.session, needs_refresh=True)

    request.page_text = text
    request.page_markup = markup
    return request
