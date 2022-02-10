"""收藏页"""
import telebot

from model.page_model import EditCollectionTypePageRequest, BackRequest, DoEditCollectionTypeRequest
from utils.api import get_subject_info


def generate_page(request: EditCollectionTypePageRequest, stack_uuid: str) -> EditCollectionTypePageRequest:
    name = get_subject_info(request.subject_id)['name']
    text = f'*您想将 “*`{name}`*” 收藏为*\n\n'
    markup = telebot.types.InlineKeyboardMarkup()
    button_list = [telebot.types.InlineKeyboardButton(text='返回', callback_data=f'{stack_uuid}|back'),
                   telebot.types.InlineKeyboardButton(text='想看', callback_data=f'{stack_uuid}|wish'),
                   telebot.types.InlineKeyboardButton(text='看过', callback_data=f'{stack_uuid}|collect'),
                   telebot.types.InlineKeyboardButton(text='在看', callback_data=f'{stack_uuid}|do'),
                   telebot.types.InlineKeyboardButton(text='搁置', callback_data=f'{stack_uuid}|on_hold'),
                   telebot.types.InlineKeyboardButton(text='抛弃', callback_data=f'{stack_uuid}|dropped')]
    request.possible_request['back'] = BackRequest()
    request.possible_request['wish'] = DoEditCollectionTypeRequest(request.subject_id, 'wish')
    request.possible_request['collect'] = DoEditCollectionTypeRequest(request.subject_id, 'collect')
    request.possible_request['do'] = DoEditCollectionTypeRequest(request.subject_id, 'do')
    request.possible_request['on_hold'] = DoEditCollectionTypeRequest(request.subject_id, 'on_hold')
    request.possible_request['dropped'] = DoEditCollectionTypeRequest(request.subject_id, 'dropped')
    markup.add(*button_list, row_width=3)
    request.page_text = text
    request.page_markup = markup
    return request
