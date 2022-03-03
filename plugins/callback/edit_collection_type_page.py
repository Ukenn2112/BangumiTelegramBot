"""收藏页"""
import telebot

from model.page_model import EditCollectionTypePageRequest, BackRequest, DoEditCollectionTypeRequest, \
    COLLECTION_TYPE_STR
from utils.api import get_subject_info, user_data_get, user_collection_get, collection_post, anime_img


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
    for i in COLLECTION_TYPE_STR.__args__:
        request.possible_request[i] = DoEditCollectionTypeRequest(request.subject_id, i)
    markup.add(*button_list, row_width=3)
    request.page_text = text
    request.page_markup = markup
    return request


def do(request: DoEditCollectionTypeRequest, tg_id: int) -> DoEditCollectionTypeRequest:
    subject_id = request.subject_id
    collection_type = request.collection_type
    access_token = user_data_get(tg_id).get('access_token')
    if not access_token:
        request.callback_text = "您尚未绑定Bangumi账户，请私聊bot绑定"
        return request
    rating = str(user_collection_get(None, subject_id, access_token).get('rating'))
    if collection_type == 'wish':  # 想看
        collection_post(None, subject_id, collection_type, rating, access_token)
        request.callback_text = "已将收藏更改为想看"
    if collection_type == 'collect':  # 看过
        collection_post(None, subject_id, collection_type, rating, access_token)
        request.callback_text = "已将收藏更改为看过"
    if collection_type == 'do':  # 在看
        collection_post(None, subject_id, collection_type, rating, access_token)
        request.callback_text = "已将收藏更改为在看"
    if collection_type == 'on_hold':  # 搁置
        collection_post(None, subject_id, collection_type, rating, access_token)
        request.callback_text = "已将收藏更改为搁置"
    if collection_type == 'dropped':  # 抛弃
        collection_post(None, subject_id, collection_type, rating, access_token)
        request.callback_text = "已将收藏更改为抛弃"
    if not request.page_image:
        request.page_image = anime_img(request.subject_id)
    return request
