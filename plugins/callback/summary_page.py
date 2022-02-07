"""简介页"""
import telebot

from model.page_model import SummaryRequest, BackRequest
from utils.api import get_subject_info
from utils.converts import subject_type_to_emoji


def generate_page(summary_request: SummaryRequest, stack_uuid: str) -> SummaryRequest:
    """简介页"""
    subject_info = get_subject_info(summary_request.subject_id)
    text = (f"{subject_type_to_emoji(subject_info['type'])} *{subject_info['name_cn']}*\n"
            f"{subject_info['name']}\n\n"
            f"*➤ 简介：*\n"
            f"{subject_info['summary']}\n"
            f"\n📖 [详情](https://bgm.tv/subject/{summary_request.subject_id})"
            f"\n💬 [吐槽箱](https://bgm.tv/subject/{summary_request.subject_id}/comments)")
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(text='返回', callback_data=f"{stack_uuid}|back"))
    summary_request.page_text = text
    summary_request.page_markup = markup
    summary_request.possible_request['back'] = BackRequest()
    return summary_request
