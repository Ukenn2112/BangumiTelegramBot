"""收藏页"""
import telebot

from model.page_model import EditCollectionTypePageRequest, BackRequest, DoEditCollectionTypeRequest, \
    COLLECTION_TYPE_STR
from utils.api import get_subject_info, user_data_get, user_collection_get, collection_post, anime_img
from utils.converts import collection_type_markup_text_list


def generate_page(request: EditCollectionTypePageRequest, session_uuid: str) -> EditCollectionTypePageRequest:
    subject_data = get_subject_info(request.subject_id)
    text = f"*您想将 “*`{subject_data['name']}`*” 收藏为*\n\n"
    markup_text = collection_type_markup_text_list(subject_data['type'])
    markup = telebot.types.InlineKeyboardMarkup()
    button_list = [
        telebot.types.InlineKeyboardButton(text=markup_text[0], callback_data=f'{session_uuid}|wish'),
        telebot.types.InlineKeyboardButton(text=markup_text[1], callback_data=f'{session_uuid}|collect'),
        telebot.types.InlineKeyboardButton(text=markup_text[2], callback_data=f'{session_uuid}|do'),
        telebot.types.InlineKeyboardButton(text='返回', callback_data=f'{session_uuid}|back'),
        telebot.types.InlineKeyboardButton(text='搁置', callback_data=f'{session_uuid}|on_hold'),
        telebot.types.InlineKeyboardButton(text='抛弃', callback_data=f'{session_uuid}|dropped')]
    request.possible_request['back'] = BackRequest(request.session)
    for i in COLLECTION_TYPE_STR.__args__:
        request.possible_request[i] = DoEditCollectionTypeRequest(request.session, request.subject_id, i)
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
        # request.callback_text = "已将收藏更改为想看"
    if collection_type == 'collect':  # 看过
        collection_post(None, subject_id, collection_type, rating, access_token)
        # request.callback_text = "已将收藏更改为看过"
    if collection_type == 'do':  # 在看
        collection_post(None, subject_id, collection_type, rating, access_token)
        # request.callback_text = "已将收藏更改为在看"
    if collection_type == 'on_hold':  # 搁置
        collection_post(None, subject_id, collection_type, rating, access_token)
        # request.callback_text = "已将收藏更改为搁置"
    if collection_type == 'dropped':  # 抛弃
        collection_post(None, subject_id, collection_type, rating, access_token)
        # request.callback_text = "已将收藏更改为抛弃"
    request.callback_text = "已更改收藏状态"
    if not request.page_image:
        request.page_image = anime_img(request.subject_id)
    return request
