"""简介页"""
import telebot

from model.page_model import SummaryRequest, BackRequest
from utils.api import get_subject_info, anime_img
from utils.converts import subject_type_to_emoji


def generate_page(request: SummaryRequest, stack_uuid: str) -> SummaryRequest:
    """简介页"""
    subject_info = get_subject_info(request.subject_id)
    if not request.page_image:
        request.page_image = anime_img(request.subject_id)
    text = (f"{subject_type_to_emoji(subject_info['type'])} *{subject_info['name_cn']}*\n"
            f"{subject_info['name']}\n\n"
            f"*➤ 简介：*\n"
            f"{subject_info['summary']}\n"
            f"\n📖 [详情](https://bgm.tv/subject/{request.subject_id})"
            f"\n💬 [吐槽箱](https://bgm.tv/subject/{request.subject_id}/comments)")
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='返回', callback_data=f"{stack_uuid}|back"))
    request.page_text = text
    request.page_markup = markup
    request.possible_request['back'] = BackRequest(request.session)
    return request
