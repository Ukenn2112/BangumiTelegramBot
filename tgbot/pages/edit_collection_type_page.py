"""收藏页"""
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..model.page_model import (
    EditCollectionTagsPageRequest,
    EditCollectionTypePageRequest,
    BackRequest,
    DoEditCollectionTypeRequest,
    COLLECTION_TYPE_STR,
)
from utils.converts import collection_type_markup_text_list, subject_type_to_emoji


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
    for i in COLLECTION_TYPE_STR.__args__:
        request.possible_request[i] = DoEditCollectionTypeRequest(
            request.session, subject_info["id"], i
        )
    markup.add(InlineKeyboardButton(text="标签管理", callback_data=f"{session_uuid}|tags"))
    collection_tag_page_request = EditCollectionTagsPageRequest(
        request.session, subject_info
    )
    request.possible_request["tags"] = collection_tag_page_request
    markup.add(*button_list, row_width=3)

    request.page_text = text
    request.page_markup = markup
    return request


# def do(request: DoEditCollectionTypeRequest, tg_id: int) -> DoEditCollectionTypeRequest:
#     subject_id = subject_info["id"]
#     collection_type = request.collection_type
#     access_token = user_data_get(tg_id).get("access_token")
#     if not access_token:
#         request.callback_text = "您尚未绑定Bangumi账户，请私聊bot绑定"
#         return request
#     rating = str(user_collection_get(None, subject_id, access_token).get("rating"))
#     if collection_type == "wish":  # 想看
#         post_collection(
#             None, subject_id, status=collection_type, rating=rating, access_token=access_token
#         )
#         # request.callback_text = "已将收藏更改为想看"
#     if collection_type == "collect":  # 看过
#         post_collection(
#             None, subject_id, status=collection_type, rating=rating, access_token=access_token
#         )
#         # request.callback_text = "已将收藏更改为看过"
#     if collection_type == "do":  # 在看
#         post_collection(
#             None, subject_id, status=collection_type, rating=rating, access_token=access_token
#         )
#         # request.callback_text = "已将收藏更改为在看"
#     if collection_type == "on_hold":  # 搁置
#         post_collection(
#             None, subject_id, status=collection_type, rating=rating, access_token=access_token
#         )
#         # request.callback_text = "已将收藏更改为搁置"
#     if collection_type == "dropped":  # 抛弃
#         post_collection(
#             None, subject_id, status=collection_type, rating=rating, access_token=access_token
#         )
#         # request.callback_text = "已将收藏更改为抛弃"
#     request.callback_text = "已更改收藏状态"
#     if not request.page_image:
#         request.page_image = anime_img(subject_info["id"])
#     return request


# def collection_tags_page(request: EditCollectionTagsPageRequest, tg_id: int):
#     subject_id = subject_info["id"]
#     access_token = user_data_get(tg_id).get("access_token")
#     if not access_token:
#         request.callback_text = "您尚未绑定Bangumi账户，请私聊bot绑定"
#         return request
#     subject_info = get_subject_info(subject_id)
#     user_collection = user_collection_get(None, subject_id, access_token)
#     if (
#         user_collection
#         and "tag" in user_collection
#         and user_collection["tag"]
#         and len(user_collection["tag"]) == 1
#         and user_collection["tag"][0] == ""
#     ):
#         user_collection["tag"] = []  # 鬼知道为什么没标签会返回个空字符串
#     text = (
#         f"*{subject_type_to_emoji(subject_info['type'])}"
#         f"『 {subject_info['name_cn'] or subject_info['name']} 』标签管理*\n\n"
#     )
#     text += "➤ *常用标签：*"
#     if subject_info["tags"]:
#         for tag in subject_info["tags"]:
#             text += f"`{tag['name']}` "
#     else:
#         text += "此条目暂无标签"
#     text += "\n\n➤ *我的标签：*"
#     if user_collection["tag"]:
#         for tag in user_collection["tag"]:
#             text += f"`{tag}` "
#     else:
#         text += "未设置条目标签"
#     text += (
#         f"\n\n📖 [详情](https://bgm.tv/subject/{subject_id})\n"
#         "*回复此消息即可修改标签 (此操作直接对现有设置标签进行覆盖，多标签请用空格隔开)*"
#     )
#     markup = InlineKeyboardMarkup()
#     markup.add(
#         InlineKeyboardButton(text="返回", callback_data=f"{request.session.uuid}|back")
#     )
#     request.possible_request["back"] = BackRequest(request.session)
#     request.page_text = text
#     request.page_markup = markup
#     if not request.page_image:
#         request.page_image = anime_img(subject_info["id"])
#     return request TODO
