"""简介页"""
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.config_vars import bgm, redis
from utils.converts import subject_type_to_emoji

from ..model.page_model import BackRequest, SummaryRequest


async def generate_page(request: SummaryRequest) -> SummaryRequest:
    session_uuid = request.session.uuid
    """简介页"""
    subject_info = request.subject_info
    subject_id = subject_info["id"]
    text = (
        f"{subject_type_to_emoji(subject_info['type'])} *{subject_info['name_cn']}*\n"
        f"{subject_info['name']}\n\n"
        f"*➤ 简介：*\n"+
        subject_info['summary'].strip("\n").strip("\r\n\r\n")+
        f"\n\n📖 [详情](https://bgm.tv/subject/{subject_id})"
        f"\n💬 [吐槽箱](https://bgm.tv/subject/{subject_id}/comments)"
    )
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text='返回', callback_data=f"{session_uuid}|back"),
        InlineKeyboardButton(text="巡礼", switch_inline_query_current_chat=f"anitabi {subject_id}"),
        InlineKeyboardButton(text="角色", switch_inline_query_current_chat=f"SC {subject_id}"),
    )
    request.page_text = text
    request.page_markup = markup
    request.possible_request['back'] = BackRequest(request.session)
    return request
