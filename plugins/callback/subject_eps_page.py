import math

import telebot

from model.page_model import SubjectEpsPageRequest, BackRequest, EditEpsPageRequest
from utils.api import get_subject_episode, anime_img, get_subject_info, user_collection_get
from utils.converts import subject_type_to_emoji


def generate_page(request: SubjectEpsPageRequest, stack_uuid: str) -> SubjectEpsPageRequest:
    if not request.page_image:
        request.page_image = anime_img(request.subject_id)
    if not request.subject_info:
        request.subject_info = get_subject_info(request.subject_id)
    if not request.user_collection:
        request.user_collection = user_collection_get(None, request.subject_id,
                                                      request.session.bgm_auth['access_token'])

    subject_id = request.subject_id
    eps = get_subject_episode(int(subject_id), limit=request.limit, offset=request.offset, type_=request.type_)
    button_list = []
    subject_info = request.subject_info
    text = f"*《{subject_type_to_emoji(subject_info['type'])}{subject_info['name_cn'] or subject_info['name']}》*章节列表:\n"
    for i in eps['data']:
        if i['ep'].is_integer():
            ep = str(int(i['ep']))
        else:
            ep = str(i['ep'])
        text += f"*{ep}.*"
        text += f" {i['name_cn'] or i['name'] or '未公布'}\n"
        button_list.append(telebot.types.InlineKeyboardButton(text=ep, callback_data=f'{stack_uuid}|{i["id"]}'))
        request.possible_request[str(i['id'])] = EditEpsPageRequest(request.session, request.subject_id, i['id'],
                                                                    episode_info=i)

    total = eps['total']
    limit = eps['limit']
    offset = request.offset
    button_list2 = []
    markup = telebot.types.InlineKeyboardMarkup()
    if total > limit:
        if offset - limit >= 0:
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='上一页', callback_data=f'{stack_uuid}|pre'))
            request.possible_request['pre'] = \
                SubjectEpsPageRequest(request.session, request.subject_id, limit=limit,
                                      offset=offset - limit)
        else:
            button_list2.append(telebot.types.InlineKeyboardButton(
                text='这是首页', callback_data="None"))
        button_list2.append(telebot.types.InlineKeyboardButton(
            text=f'{int(offset / limit) + 1}/{math.ceil(total / limit)}', callback_data="None"))
        if offset + limit < total:
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='下一页', callback_data=f'{stack_uuid}|next'))
            request.possible_request['next'] = \
                SubjectEpsPageRequest(request.session, request.subject_id, limit=limit, type_=request.type_,
                                      offset=offset + limit)
        else:
            button_list2.append(telebot.types.InlineKeyboardButton(text='这是末页', callback_data="None"))
    markup.add(*button_list, row_width=6)
    markup.add(*button_list2)
    markup.add(telebot.types.InlineKeyboardButton(text='返回', callback_data=f"{stack_uuid}|back"))
    request.possible_request['back'] = BackRequest(request.session, needs_refresh=True)

    request.page_text = text
    request.page_markup = markup
    return request
