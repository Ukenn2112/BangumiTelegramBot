"""已看最新"""
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.config_vars import bgm
from utils.converts import number_to_episode_type

from ..model.page_model import (BackRequest, DoEditEpisodeRequest,
                                EditEpsPageRequest)

EPISODE_DESC_LIMIT = 512


async def generate_page(request: EditEpsPageRequest) -> EditEpsPageRequest:
    session_uuid = request.session.uuid
    episode_info = request.episode_info
    text = f"*{number_to_episode_type(episode_info['type'])}.{episode_info['sort']}*"
    if episode_info["name_cn"]:
        text += f"* | {episode_info['name_cn']}*"
    if episode_info["name"]:
        text += f"* / {episode_info['name']}*"
    text += f"\n\n*EP ID：* `{episode_info['id']}`"
    if episode_info["duration"]:
        text += f"\n*➤ 时长：*`{episode_info['duration']}`"
    if episode_info["airdate"]:
        text += f"\n*➤ 首播日期：*`{episode_info['airdate']}`"
    if desc := episode_info["desc"]:
        if len(desc) > EPISODE_DESC_LIMIT:
            desc = desc[:EPISODE_DESC_LIMIT] + " ..."
        text += f"\n*➤ 章节简介：*\n{desc}"
    text += f"\n\n💬 [讨论：{episode_info['comment']}](https://bgm.tv/ep/{episode_info['id']})"
    markup = InlineKeyboardMarkup()
    request.possible_request["back"] = BackRequest(request.session)
    if request.session.bot_message.chat.type == "private" and request.before_status is not None and request.session.user_bgm_data:
        text += "\n*回复此消息即可对此章节进行评论*"
        button_list = []
        if request.before_status != 2:
            button_list.append(InlineKeyboardButton(text="看过", callback_data=f"{session_uuid}|watched"))
            request.possible_request["watched"] = DoEditEpisodeRequest(
                request.session, episode_info, 2
            )

        button_list.append(InlineKeyboardButton(text="看到", callback_data=f"{session_uuid}|watched_batch"))
        request.possible_request["watched_batch"] = DoEditEpisodeRequest(
            request.session, episode_info, 4
        )
        if request.before_status != 1:
            button_list.append(InlineKeyboardButton(text="想看", callback_data=f"{session_uuid}|queue"))
            request.possible_request["queue"] = DoEditEpisodeRequest(
                request.session, episode_info, 1
            )
        if request.before_status != 3:
            button_list.append(InlineKeyboardButton(text="抛弃", callback_data=f"{session_uuid}|drop"))
            request.possible_request["drop"] = DoEditEpisodeRequest(
                request.session, episode_info, 3
            )
        if request.before_status != 0:
            button_list.append(InlineKeyboardButton(text="撤销", callback_data=f"{session_uuid}|remove"))
            request.possible_request["remove"] = DoEditEpisodeRequest(
                request.session, episode_info, 0
            )
        markup.add(*button_list, row_width=5)

    markup.add(InlineKeyboardButton(text="返回", callback_data=f"{session_uuid}|back"))
    request.page_markup = markup
    request.page_text = text
    return request


async def do(request: DoEditEpisodeRequest) -> DoEditEpisodeRequest:
    episode_info = request.episode_info
    if request.status != 4:
        await bgm.put_user_episode_collection(
            request.session.user_bgm_data["accessToken"],
            request.episode_info["id"],
            request.status
        )
        request.callback_text = "已修改"
    else:  # 批量更新
        page = 0
        limit = 200
        update_eps = []
        while True:
            data = await bgm.get_episodes(
                episode_info["subject_id"],
                episode_info["type"],
                limit=limit,
                offset=limit * page,
                access_token=request.session.user_bgm_data["accessToken"]
            )
            page += 1
            ok = False
            for ep in data["data"]:
                update_eps.append(ep["id"])
                if ep["id"] == episode_info["id"]:
                    ok = True
                    break
            if ok or data["total"] < limit or len(data["data"]) < limit:
                break
        await bgm.patch_uesr_episode_collection(
            request.session.user_bgm_data["accessToken"],
            episode_info["subject_id"],
            update_eps,
            2
        )
        request.callback_text = f"已修改{len(update_eps)}个章节为看过"
    return request
