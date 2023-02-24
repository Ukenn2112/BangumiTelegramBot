"""收藏页"""
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.config_vars import bgm
from utils.converts import (collection_type_markup_text_list, collection_type_subject_type_str,
                            subject_type_to_emoji)

from ..model.exception import UserNotBound
from ..model.page_model import (BackRequest, DoEditCollectionTypeRequest,
                                EditCollectionTagsPageRequest,
                                EditCollectionTypePageRequest, EditRatingPageRequest)

collection_types = [("wish", 1), ("collect", 2), ("do", 3), ("on_hold", 4), ("dropped", 5)]

async def generate_page(request: EditCollectionTypePageRequest) -> EditCollectionTypePageRequest:
    session_uuid = request.session.uuid
    subject_info = request.subject_info
    text = (
        f"*您想将 “*`{subject_info['name']}`*” 收藏为*\n\n"
        f"💬 [吐槽箱](https://bgm.tv/subject/{subject_info['id']}/comments)\n"
        "*回复此消息即可对此条目进行吐槽 (简评，最多200字)*"
    )
    markup_text = collection_type_markup_text_list(subject_info["type"])
    markup = InlineKeyboardMarkup()
    button_list = [
        InlineKeyboardButton(text=markup_text[0], callback_data=f"{session_uuid}|wish"),
        InlineKeyboardButton(text=markup_text[1], callback_data=f"{session_uuid}|collect"),
        InlineKeyboardButton(text=markup_text[2], callback_data=f"{session_uuid}|do"),
        InlineKeyboardButton(text="返回", callback_data=f"{session_uuid}|back"),
        InlineKeyboardButton(text="搁置", callback_data=f"{session_uuid}|on_hold"),
        InlineKeyboardButton(text="抛弃", callback_data=f"{session_uuid}|dropped"),
    ]
    request.possible_request["back"] = BackRequest(request.session)
    for s, n in collection_types:
        request.possible_request[s] = DoEditCollectionTypeRequest(
            request.session, subject_info["id"], subject_info["type"], n
        )
    if request.user_collection:
        markup.add(
            InlineKeyboardButton(text="标签", callback_data=f"{session_uuid}|tags"),
            InlineKeyboardButton(text="评分", callback_data=f"{session_uuid}|rating")
        )
        collection_tag_page_request = EditCollectionTagsPageRequest(
            request.session, request.user_collection
        )
        request.possible_request["tags"] = collection_tag_page_request
        edit_rating_page_request = EditRatingPageRequest(
            request.session, request.user_collection
        )
        request.possible_request["rating"] = edit_rating_page_request
    markup.add(*button_list, row_width=3)

    request.page_text = text
    request.page_markup = markup
    return request


async def do(request: DoEditCollectionTypeRequest) -> DoEditCollectionTypeRequest:
    await bgm.patch_user_subject_collection(
            request.session.user_bgm_data["accessToken"],
            request.subject_id,
            request.collection_type
        )
    request.callback_text = f"已更改收藏状态为 {collection_type_subject_type_str(request.subject_type, request.collection_type)}"
    return request


async def collection_tags_page(request: EditCollectionTagsPageRequest) -> EditCollectionTagsPageRequest:
    subject_info = request.user_collection["subject"]
    user_collection = request.user_collection
    text = (
        f"*{subject_type_to_emoji(subject_info['type'])}"
        f"『 {subject_info['name_cn'] or subject_info['name']} 』标签管理*\n\n"
    )
    text += "➤ *常用标签：*"
    if subject_info["tags"]:
        for tag in subject_info["tags"]:
            text += f"`{tag['name']}` "
    else:
        text += "此条目暂无标签"
    text += "\n\n➤ *我的标签：*"
    if user_collection and user_collection["tags"]:
        for tag in user_collection["tags"]:
            text += f"`{tag}` "
    else:
        text += "未设置条目标签"
    text += (
        f"\n\n📖 [详情](https://bgm.tv/subject/{subject_info['id']})\n"
        "*回复此消息即可修改标签 (此操作直接对现有设置标签进行覆盖，多标签请用空格隔开)*"
    )
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(text="返回", callback_data=f"{request.session.uuid}|back")
    )
    request.possible_request["back"] = BackRequest(request.session)
    request.page_text = text
    request.page_markup = markup
    return request
