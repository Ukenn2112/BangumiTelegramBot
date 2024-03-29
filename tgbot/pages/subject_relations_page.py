from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from ..model.page_model import BackRequest, SubjectRelationsPageRequest, SubjectRequest
from utils.converts import subject_type_to_emoji, full_group_by
from utils.config_vars import bgm

order = {
    "原作": 1,
    "前作": 2,
    "前传": 3,
    "续作": 4,
    "续集": 5,
    "动画": 6,
    "游戏": 7,
    "番外篇": 8,
    "剧场版": 9,
    "总集篇": 10,
    "书籍": 11,
    "画集": 12,
    "衍生": 13,
    "原声集": 14,
    "角色歌": 15,
    "片头曲": 16,
    "片尾曲": 17,
    "插入歌": 18,
    "音乐": 19,
    "广播剧": 20,
    "其他": 100,
}


async def generate_page(request: SubjectRelationsPageRequest) -> SubjectRelationsPageRequest:
    subject_info = request.subject_info
    relations = await bgm.get_subject_related(
        subject_info["id"],
        request.session.user_bgm_data["accessToken"] if request.session.user_bgm_data else None
    )
    button_list = []
    if not relations:
        text = (
            f"*{subject_type_to_emoji(subject_info['type'])}"
            f"『 {subject_info['name_cn'] or subject_info['name']} 』无关联条目*\n\n"
        )
    else:
        text = (
            f"*{subject_type_to_emoji(subject_info['type'])}"
            f"『 {subject_info['name_cn'] or subject_info['name']} 』关联条目:*\n\n"
        )
        relations = sorted(relations[:12], key=lambda a: order.get(a["relation"], 99))
        relation_group = full_group_by(relations[:12], lambda a: a["relation"])
        num: int = 1
        for key in relation_group:
            text += f"*➤ {key}:*\n"
            for relation in relation_group[key]:
                text += (
                    f"`{num:02d}`. {subject_type_to_emoji(relation['type'])}"
                    f"{relation['name_cn'] or relation['name']}\n"
                )
                button_list.append(InlineKeyboardButton(text=str(num), callback_data=f"{request.session.uuid}|{num}"))
                request.possible_request[str(num)] = SubjectRequest(request.session, relation["id"])
                num += 1

    markup = InlineKeyboardMarkup()
    markup.add(*button_list, row_width=6)
    markup.add(InlineKeyboardButton(text="返回", callback_data=f"{request.session.uuid}|back"))
    request.possible_request["back"] = BackRequest(request.session)

    request.page_text = text
    request.page_markup = markup
    return request
