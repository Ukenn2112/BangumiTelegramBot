from telebot.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           InlineQuery, InlineQueryResultArticle,
                           InputTextMessageContent)

from utils.config_vars import BOT_USERNAME, bgm


async def query_person_related_subjects(inline_query: InlineQuery, is_sender: bool):
    """PS + 人物ID 发送命令 获取人物关联条目"""
    offset = int(inline_query.offset or 0)
    query_result_list: list[InlineQueryResultArticle] = []
    person_id = inline_query.query.split(" ")[1]

    person_related_subjects = await bgm.get_person_subjects(person_id)
    if person_related_subjects is None: return {"results": query_result_list}

    person_info = await bgm.get_person(person_id)
    switch_pm_text = person_info["name"] + " 人物关联列表"

    if is_sender:
        for subject in person_related_subjects[offset : offset + 50]:
            query_result_list.append(InlineQueryResultArticle(
                id=f"{subject['staff']}:{subject['id']}",
                title=(subject["name_cn"] if subject["name_cn"] else subject["name"]),
                input_message_content=InputTextMessageContent(
                    message_text=f"/info@{BOT_USERNAME} {subject['id']}", disable_web_page_preview=True
                ),
                description=(f"{subject['name']} | " if subject["name_cn"] else "") + (subject["staff"] if subject["staff"] else ""),
                thumb_url=subject["image"] if subject["image"] else None,
            ))
    else:
        for subject in person_related_subjects[offset : offset + 50]:
            text = f"*{subject['name_cn'] or subject['name']}*\n"
            text += f"{subject['name']}\n" if subject['name_cn'] else ''

            text += f"\n*BGM ID：*`{subject['id']}`"
            text += (
                f"\n📚 [简介](https://t.me/iv?url=https://bgm.tv/subject/{subject['id']}&rhash=ce4f44b013e2e8)"
                f"\n📖 [详情](https://bgm.tv/subject/{subject['id']})"
                f"\n💬 [吐槽箱](https://bgm.tv/subject/{subject['id']}/comments)"
            )

            button_list = [
                InlineKeyboardButton(text="巡礼", switch_inline_query_current_chat=f"anitabi {subject['id']}"),
                InlineKeyboardButton(text="角色", switch_inline_query_current_chat=f"SC {subject['id']}"),
                InlineKeyboardButton(text='去管理', url=f"t.me/{BOT_USERNAME}?start={subject['id']}"),
            ]
            query_result_list.append(InlineQueryResultArticle(
                id=f"{subject['staff']}:{subject['id']}",
                title=(subject["name_cn"] if subject["name_cn"] else subject["name"]),
                input_message_content=InputTextMessageContent(
                    text, parse_mode="markdown", disable_web_page_preview=False
                ),
                description=(f"{subject['name']} | " if subject["name_cn"] else '')
                + (subject['staff'] if subject["staff"] else ''),
                thumb_url=subject["image"] if subject["image"] else None,
                reply_markup=InlineKeyboardMarkup().add(*button_list),
            ))
    return {
        "results": query_result_list,
        "next_offset": str(offset + 50),
        "switch_pm_text": switch_pm_text,
        "switch_pm_parameter": "help",
        "cache_time": 3600,
    }