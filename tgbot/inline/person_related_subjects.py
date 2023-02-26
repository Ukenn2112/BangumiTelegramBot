from telebot.types import (InlineQuery, InlineQueryResultArticle,
                           InputTextMessageContent)

from utils.config_vars import BOT_USERNAME, bgm


async def query_person_related_subjects(inline_query: InlineQuery):
    """PS + 人物ID 发送命令 获取人物关联条目"""
    offset = int(inline_query.offset or 0)
    query_result_list: list[InlineQueryResultArticle] = []
    person_id = inline_query.query.split(" ")[1]

    person_related_subjects = await bgm.get_person_subjects(person_id)
    if person_related_subjects is None: return {"results": query_result_list}

    person_info = await bgm.get_person(person_id)
    switch_pm_text = person_info["name"] + " 人物关联列表"

    for subject in person_related_subjects[offset : offset + 50]:
        qr = InlineQueryResultArticle(
            id=f"{subject['staff']}:{subject['id']}",
            title=(subject["name_cn"] if subject["name_cn"] else subject["name"]),
            input_message_content=InputTextMessageContent(
                message_text=f"/info@{BOT_USERNAME} {subject['id']}", disable_web_page_preview=True
            ),
            description=(f"{subject['name']} | " if subject["name_cn"] else "") + (subject["staff"] if subject["staff"] else ""),
            thumb_url=subject["image"] if subject["image"] else None,
        )
        query_result_list.append(qr)
    return {
        "results": query_result_list,
        "next_offset": str(offset + 50),
        "switch_pm_text": switch_pm_text,
        "switch_pm_parameter": "help",
        "cache_time": 3600,
    }