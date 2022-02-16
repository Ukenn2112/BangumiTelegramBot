import math
import telebot

from model.page_model import SubjectEpsPageRequest, BackRequest
from utils.api import get_subject_episode


def generate_page(request: SubjectEpsPageRequest, stack_uuid: str) -> SubjectEpsPageRequest:
    subject_id = request.subject_id
    eps = get_subject_episode(int(subject_id), limit=request.limit, offset=request.offset)
    button_list = []
    text = "该条目章节列表:\n"
    for i in eps['data']:
        if i['ep'].is_integer():
            text += f"*{int(i['ep'])}*"
        else:
            text += f"*{i['ep']}*"
        if i['name_cn']:
            text += f" {i['name_cn']}"
        elif i['name']:
            text += f" {i['name']}"
        else:
            text += " 未公布"
        text += "\n"
        # button_list.append() TODO

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
                SubjectEpsPageRequest(request.subject_id, limit=limit,
                                      offset=offset - limit,
                                      user_data=request.user_data)
        else:
            button_list2.append(telebot.types.InlineKeyboardButton(
                text='这是首页', callback_data="None"))
        button_list2.append(telebot.types.InlineKeyboardButton(
            text=f'{int(offset / limit) + 1}/{math.ceil(total / limit)}', callback_data="None"))
        if offset + limit < total:
            button_list2.append(
                telebot.types.InlineKeyboardButton(text='下一页', callback_data=f'{stack_uuid}|next'))
            request.possible_request['next'] = \
                SubjectEpsPageRequest(request.subject_id, limit=limit,
                                      offset=offset + limit, user_data=request.user_data)
        else:
            button_list2.append(telebot.types.InlineKeyboardButton(text='这是末页', callback_data="None"))
    markup.add(*button_list2)
    markup.add(telebot.types.InlineKeyboardButton(text='返回', callback_data=f"{stack_uuid}|back"))
    request.possible_request['back'] = BackRequest(needs_refresh=True)
    request.page_text = text
    request.page_markup = markup
    return request
