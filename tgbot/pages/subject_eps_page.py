import math

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from ..model.page_model import DoEditCollectionTypeRequest, SubjectEpsPageRequest, BackRequest, EditEpsPageRequest
from utils.converts import subject_type_to_emoji, number_to_episode_type
from utils.config_vars import bgm


async def generate_page(request: SubjectEpsPageRequest) -> SubjectEpsPageRequest:
    session_uuid = request.session.uuid
    subject_info = request.subject_info
    id_to_emoji = {1: "👀", 2: "🔘", 3: "🗑️"}
    watched_last_episode = False
    if request.session.user_bgm_data:
        eps_list = await bgm.get_user_episode_collections(
            request.session.user_bgm_data["accessToken"],
            subject_info["id"],
            request.offset,
            request.limit,
            request.episode_type,
        )
        if eps_list["data"] and eps_list["data"][-1]["type"] == 2 and eps_list["data"][-1]["episode"]["ep"] == eps_list["total"]:
            watched_last_episode = True
    else:
        eps_list = await bgm.get_episodes(
            subject_info["id"], request.episode_type, request.limit, request.offset
        )
    button_list = []
    text = (
        f"*{subject_type_to_emoji(subject_info['type'])}"
        f"『 {subject_info['name_cn'] or subject_info['name']} 』{number_to_episode_type(request.episode_type)}章节列表:*\n\n"
    )
    if eps_list["data"]:
        for i in eps_list["data"]:
            before_status = None
            if request.session.user_bgm_data:
                text += id_to_emoji.get(i["type"], "⚪")
                before_status = i["type"]
                episode_info = i["episode"]
            else:
                episode_info = i
            button_list.append(InlineKeyboardButton(text=str(episode_info["sort"]), callback_data=f"{session_uuid}|{episode_info['id']}"))
            page_request = EditEpsPageRequest(request.session, episode_info)
            request.possible_request[str(episode_info["id"])] = page_request

            page_request.before_status = before_status
            text += f"`{episode_info['sort']:02d}`*.*"
            text += f" {episode_info['name_cn'] or episode_info['name'] or '未公布'} \n"
    else:
        text += "无章节"

    total = eps_list["total"]
    limit = eps_list["limit"]
    offset = request.offset
    button_list2 = []
    markup = InlineKeyboardMarkup()
    if total > limit:
        if offset - limit >= 0:
            button_list2.append(InlineKeyboardButton(text="上一页", callback_data=f"{session_uuid}|pre"))
            pre_request = SubjectEpsPageRequest(
                request.session,
                subject_info,
                limit=limit,
                episode_type=request.episode_type,
                offset=offset - limit,
            )
            request.possible_request["pre"] = pre_request
        else:
            button_list2.append(InlineKeyboardButton(text="这是首页", callback_data="None"))
        button_list2.append(InlineKeyboardButton(text=f"{int(offset / limit) + 1}/{math.ceil(total / limit)}", callback_data="None"))
        if offset + limit < total:
            button_list2.append(InlineKeyboardButton(text="下一页", callback_data=f"{session_uuid}|next"))
            next_request = SubjectEpsPageRequest(
                request.session,
                subject_info,
                limit=limit,
                episode_type=request.episode_type,
                offset=offset + limit,
            )
            request.possible_request["next"] = next_request
        else:
            button_list2.append(InlineKeyboardButton(text="这是末页", callback_data="None"))
    if subject_info["type"] == 2:
        button_list3 = []
        if request.episode_type != 0:
            button_list3.append(InlineKeyboardButton(text="本篇", callback_data=f"{session_uuid}|eps"))
            subject_eps_page_request = SubjectEpsPageRequest(
                request.session, subject_info, limit=12, episode_type=0
            )
            request.possible_request["eps"] = subject_eps_page_request
        if request.episode_type != 1:
            button_list3.append(InlineKeyboardButton(text="SP", callback_data=f"{session_uuid}|eps1"))
            subject_eps_page_request = SubjectEpsPageRequest(
                request.session, subject_info, limit=12, episode_type=1
            )
            request.possible_request["eps1"] = subject_eps_page_request
        if request.episode_type != 2:
            button_list3.append(InlineKeyboardButton(text="OP", callback_data=f"{session_uuid}|eps2"))
            subject_eps_page_request = SubjectEpsPageRequest(
                request.session, subject_info, limit=12, episode_type=2
            )
            request.possible_request["eps2"] = subject_eps_page_request
        if request.episode_type != 3:
            button_list3.append(InlineKeyboardButton(text="ED", callback_data=f"{session_uuid}|eps3"))
            subject_eps_page_request = SubjectEpsPageRequest(
                request.session, subject_info, limit=12, episode_type=3
            )
            request.possible_request["eps3"] = subject_eps_page_request
        markup.add(*button_list3, row_width=3)
    markup.add(*button_list, row_width=6)
    markup.add(*button_list2)
    if watched_last_episode:
        markup.add(InlineKeyboardButton(text="将此章节收藏改为完成？", callback_data=f"{session_uuid}|collect"))
        request.possible_request["collect"] = DoEditCollectionTypeRequest(
            request.session, subject_info["id"], subject_info["type"], 2, {}
        )
    markup.add(InlineKeyboardButton(text="返回", callback_data=f"{session_uuid}|back"))
    request.possible_request["back"] = BackRequest(request.session, needs_refresh=True)

    request.page_text = text
    request.page_markup = markup
    return request
