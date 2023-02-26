from telebot.types import (InlineQuery, InlineQueryResultArticle,
                           InputTextMessageContent)

from utils.config_vars import bgm
from utils.converts import full_group_by


async def query_subject_characters(inline_query: InlineQuery):
    """SC + 条目ID 获取条目关联角色"""
    offset = int(inline_query.offset or 0)
    query_result_list: list[InlineQueryResultArticle] = []
    subject_id = inline_query.query.split(" ")[1]

    subject_characters = await bgm.get_subject_characters(subject_id)
    if subject_characters is None: return {"results": query_result_list}        

    subject_info = await bgm.get_subject(subject_id)
    switch_pm_text = (subject_info["name_cn"] or subject_info["name"]) + " 角色列表"

    new_subject_characters = []
    group = full_group_by(subject_characters, lambda c: c["relation"])
    new_subject_characters.extend(group.pop("主角", []))
    new_subject_characters.extend(group.pop("配角", []))
    new_subject_characters.extend(group.pop("客串", []))
    for k in group:
        new_subject_characters.extend(group[k])
    for character in new_subject_characters[offset : offset + 49]:
        text = f"*{character['name']}*"
        description = character["relation"]
        if character["actors"]:
            description += f" | CV: {[cv['name'] for cv in character['actors']][0]}"
        text += (
            f"\n{description}\n"
            f"\n📚 [简介](https://t.me/iv?url=https://bangumi.tv/character/{character['id']}&rhash=48797fd986e111)"
            f"\n📖 [详情](https://bgm.tv/character/{character['id']})"
        )
        query_result_list.append(InlineQueryResultArticle(
            id = f"sc:{character['id']}",
            title = character["name"],
            description = description,
            input_message_content = InputTextMessageContent(
                text, parse_mode = "markdown", disable_web_page_preview = False
            ),
            thumb_url = character["images"]["grid"] if character["images"] else None,
        ))
    if len(new_subject_characters) == 0:
        query_result_list.append(InlineQueryResultArticle(
            id="-1",
            title="这个条目没有角色QAQ",
            input_message_content=InputTextMessageContent(
                "点我干嘛!😡", parse_mode="markdown", disable_web_page_preview=False
            ),
            thumb_url=None,
        ))
    if len(new_subject_characters) <= offset + 49:
        next_offset = None
    else:
        next_offset = offset + 49
    return {
        "results": query_result_list,
        "next_offset": next_offset,
        "switch_pm_text": switch_pm_text,
        "switch_pm_parameter": subject_id,
        "cache_time": 3600,
    }