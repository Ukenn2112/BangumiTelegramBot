import html
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.config_vars import BOT_USERNAME, bgm, redis
from utils.converts import collection_type_subject_type_str, score_to_str, subject_type_to_emoji

from ..model.page_model import (BackRequest, EditCollectionTypePageRequest,
                                EditRatingPageRequest, SubjectEpsPageRequest,
                                SubjectRelationsPageRequest, SubjectRequest,
                                SummaryRequest)


async def generate_page(subject_request: SubjectRequest) -> SubjectRequest:
    user_collection = None
    if not subject_request.page_text and not subject_request.page_markup:
        if subject_request.session.bot_message.chat.type == "private":
            if subject_request.session.user_bgm_data:
                user_collection = await bgm.get_user_subject_collection(
                    subject_request.session.user_bgm_data["userData"]["username"],
                    subject_request.subject_id,
                    subject_request.session.user_bgm_data["accessToken"],
                )
    if not subject_request.subject_info:
        subject_request.subject_info = await bgm.get_subject(subject_request.subject_id)
    if subject_image := redis.get(f"subject_image:{subject_request.subject_id}"):
        subject_request.page_image = subject_image.decode()
    if not subject_request.page_text or not subject_request.page_image:
        if not subject_request.page_text:
            subject_request.page_text = await gander_page_text(subject_request.subject_id, user_collection, subject_request.subject_info)
        if not subject_request.page_image:
            subject_request.page_image = redis.get(f"_subject_image:{subject_request.subject_id}")

    if not subject_request.page_markup:
        if subject_request.session.bot_message.chat.type == "private":
            subject_request.page_markup = gender_page_manager_button(subject_request, user_collection)
        else:
            subject_request.page_markup = gender_page_show_buttons(subject_request)
    return subject_request


def gender_page_manager_button(subject_request: SubjectRequest, user_collection: dict) -> InlineKeyboardMarkup:
    """管理按钮"""
    session_uuid = subject_request.session.uuid
    markup = InlineKeyboardMarkup()
    button_list = [[], []]
    if not subject_request.is_root:
        button_list[1].append(InlineKeyboardButton(text="返回", callback_data=f"{session_uuid}|back"))
        subject_request.possible_request["back"] = BackRequest(subject_request.session)
    button_list[0].append(InlineKeyboardButton(text="简介", callback_data=f"{session_uuid}|summary"))
    subject_request.possible_request["summary"] = SummaryRequest(
        subject_request.session, subject_request.subject_info
    )
    button_list[0].append(InlineKeyboardButton(text="关联", callback_data=f"{session_uuid}|relations"))
    relations_request = SubjectRelationsPageRequest(
        subject_request.session, subject_id=subject_request.subject_id
    )
    subject_request.possible_request["relations"] = relations_request
    if user_collection:
        button_list[1].append(InlineKeyboardButton(text="评分", callback_data=f"{session_uuid}|rating"))
        edit_rating_page_request = EditRatingPageRequest(subject_request.session, subject_request.subject_id)
        edit_rating_page_request.user_collection = user_collection
        subject_request.possible_request["rating"] = edit_rating_page_request
        button_list[0].append(InlineKeyboardButton(text="点格子", callback_data=f"{session_uuid}|eps"))
    else:
        button_list[0].append(InlineKeyboardButton(text="章节", callback_data=f"{session_uuid}|eps"))
        subject_eps_page_request = SubjectEpsPageRequest(
            subject_request.session, subject_id=subject_request.subject_id, limit=12, type_=0
        )
        subject_eps_page_request.user_collection = user_collection
        subject_request.possible_request["eps"] = subject_eps_page_request
    button_list[1].append(InlineKeyboardButton(text="收藏管理", callback_data=f"{session_uuid}|collection"))
    edit_collection_type_page_request = EditCollectionTypePageRequest(
        subject_request.session, subject_request.subject_id
    )
    subject_request.possible_request["collection"] = edit_collection_type_page_request

    for i in button_list:
        if i:
            markup.add(*i)
    return markup


def gender_page_show_buttons(subject_request: SubjectRequest) -> InlineKeyboardMarkup:
    """仅预览按钮 无管理"""
    session_uuid = subject_request.session.uuid
    markup = InlineKeyboardMarkup()
    button_list = [[], []]
    if not subject_request.is_root:
        button_list[1].append(InlineKeyboardButton(text="返回", callback_data=f"{session_uuid}|back"))
        subject_request.possible_request["back"] = BackRequest(subject_request.session)
    button_list[1].append(InlineKeyboardButton(text="去管理", url=f"t.me/{BOT_USERNAME}?start={subject_request.subject_id}"))  # TODO
    button_list[0].append(InlineKeyboardButton(text="简介", callback_data=f"{session_uuid}|summary"))
    button_list[0].append(InlineKeyboardButton(text="章节", callback_data=f"{session_uuid}|eps"))
    button_list[0].append(InlineKeyboardButton(text="关联", callback_data=f"{session_uuid}|relations"))
    subject_eps_page_request = SubjectEpsPageRequest(
        subject_request.session, subject_id=subject_request.subject_id, limit=12, type_=0
    )
    subject_eps_page_request.user_collection = {"code"}
    subject_request.possible_request["eps"] = subject_eps_page_request
    subject_request.possible_request["summary"] = SummaryRequest(
        subject_request.session, subject_request.subject_info
    )
    relations_request = SubjectRelationsPageRequest(
        subject_request.session, subject_id=subject_request.subject_id
    )
    subject_request.possible_request["relations"] = relations_request
    subject_request.possible_request["collection"] = EditCollectionTypePageRequest(
        subject_request.session, subject_request.subject_id
    )

    for i in button_list:
        if i:
            markup.add(*i, row_width=4)
    return markup


async def gander_page_text(subject_id, user_collection: dict = None, subject_info: dict = None) -> str:
    """详情页 字符串拼接"""
    if not subject_info: subject_info = await bgm.get_subject(subject_id)
    subject_type = subject_info["type"]
    if subject_info["name_cn"]:
        text = (
            f"{subject_type_to_emoji(subject_type)} *{subject_info['name_cn']}*\n"
            f"{subject_info['name']}\n\n"
        )
    else:
        text = f"{subject_type_to_emoji(subject_type)} *{subject_info['name']}*\n\n"
    text += f"*BGM ID：*`{subject_id}`"
    if user_collection:
        text += f" | {collection_type_subject_type_str(subject_type, user_collection['type'])}"
    if subject_info["nsfw"]:
        text += " 🔞"
    text += "\n"
    if subject_info["rating"]["score"] != 0:
        text += (
            f"*➤ BGM 平均评分：*`{subject_info['rating']['score']}`🌟 "
            f"{score_to_str(subject_info['rating']['score'])}\n"
        )
    else:
        text += "*➤ BGM 平均评分：*暂无评分\n"
    subject_info["date"] = subject_info["date"] if subject_info["date"] else "未知"
    epssssss = subject_info["eps"] if subject_info["eps"] != 0 else subject_info["total_episodes"]
    if user_collection:
        if user_collection["rate"] == 0:
            text += "*➤ 您的评分：*暂未评分\n"
        else:
            text += f"*➤ 您的评分：*`{user_collection['rate']}`🌟\n"
    else:
        if subject_type in [2, 6]:  # 当类型为anime或real时
            text += f"*➤ 集数：*共`{epssssss}`集\n"
    if subject_type in [2, 6]:  # 当类型为anime或real时
        if subject_type == 6:
            text += f"*➤ 剧集类型：*`{subject_info['platform']}`\n"
        else:
            text += f"*➤ 放送类型：*`{subject_info['platform']}`\n"
        text += f"*➤ 放送开始：*`{subject_info['date']}`\n"
        if subject_info["_air_weekday"]:
            text += f"*➤ 放送星期：*`{subject_info['_air_weekday']}`\n"
        if user_collection:
            text += f"*➤ 观看进度：*`{user_collection['ep_status']}/{epssssss}`\n"
    if subject_type == 1:  # 当类型为book时
        text += f"*➤ 书籍类型：*`{subject_info['platform']}`\n"
        for box in subject_info["infobox"]:
            if box.get("key") == "页数":
                text += f"*➤ 页数：*共`{box['value']}`页\n"
            if box.get("key") == "作者":
                text += f"*➤ 作者：*`{box['value']}`\n"
            if box.get("key") == "出版社":
                if isinstance(box["value"], list):
                    text += "*➤ 出版社：*"
                    for price in box["value"]:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"*➤ 出版社：*`{box['value']}`\n"
        text += f"*➤ 发售日期：*`{subject_info['date']}`\n"
    if subject_type == 3:  # 当类型为Music时
        for box in subject_info["infobox"]:
            if box.get("key") in ["艺术家", "作曲", "作词", "编曲", "厂牌", "碟片数量", "播放时长"]:
                text += f"*➤ {box['key']}：*`{html.unescape(box['value'])}`\n"
            if box.get("key") in ["价格"]:
                if isinstance(box["value"], list):
                    text += "*➤ 价格：*"
                    for price in box["value"]:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"*➤ 价格：*`{box['value']}`\n"
        text += f"*➤ 发售日期：*`{subject_info['date']}`\n"
    if subject_type == 4:  # 当类型为Game时
        for box in subject_info["infobox"]:
            if box.get("key") in ["游戏类型", "游玩人数"]:
                text += f"*➤ {box['key']}：*`{box['value']}`\n"
            if box.get("key") == "平台":
                if isinstance(box["value"], list):
                    text += "*➤ 平台：*"
                    for price in box["value"]:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"*➤ 平台：*`{box['value']}`\n"
            if box.get("key") == "发行":
                text += f"*➤ 发行：*`{box['value']}`\n"
            if box.get("key") == "售价":
                if isinstance(box["value"], list):
                    text += "*➤ 售价：*"
                    for price in box["value"]:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"*➤ 售价：*`{box['value']}`\n"
        text += f"*➤ 发行日期：*`{subject_info['date']}`\n"
    if subject_info["tags"]:
        text += "*➤ 标签：*"
    if user_collection and user_collection["tags"]:
        for tag in user_collection["tags"][:10]:
            text += f"#{'x' if tag.isdecimal() else ''}{tag} "
        if subject_info["tags"]:
            tag_not_click = [i for i in subject_info["tags"] if i["name"] not in user_collection["tags"]]
        else:
            tag_not_click = []
    else:
        tag_not_click = subject_info["tags"]
    if tag_not_click and tag_not_click[0]:
        # 如果有列表
        if not user_collection or not user_collection["tags"]:
            # 如果没有用户标签
            if tag_not_click and tag_not_click[0]:
                for tag in tag_not_click[:10]:
                    text += f"`{tag['name']}` "
        if user_collection and user_collection["tags"] and len(user_collection["tags"]) < 10:
            # 有用户标签 但 用户标签数小于10
            for tag in tag_not_click[:10 - len(user_collection["tags"])]:
                text += f"`{tag['name']}` "
        if subject_info["tags"]:
            text += "\n"
    text += (
        f"\n📖 [详情](https://bgm.tv/subject/{subject_id})"
        f"\n💬 [吐槽箱](https://bgm.tv/subject/{subject_id}/comments)\n"
    )
    if subject_type == 3:  # 当类型为Music时
        text += f"🍎 [AppleMusic](https://am.ukenn.workers.dev/search?term={subject_info['name']})\n"
    return text
