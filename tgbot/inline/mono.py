import random

from telebot.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           InlineQuery, InlineQueryResultArticle,
                           InputTextMessageContent)

from utils.config_vars import BOT_USERNAME, bgm


async def query_mono(inline_query: InlineQuery, cat: str, query_type: str = None, is_sender: bool = False):
    """人物搜索
    :param inline_query: 查询人物关键词
    :param cat = prsn/crt -> 查询人物/角色"""
    offset = int(inline_query.offset or 0)
    query_result_list: list[InlineQueryResultArticle] = []
    query_param = inline_query.query.split(" ")
    keywords = inline_query.query[len(query_param[0]) + 1 :]
    if query_type:
        keywords = keywords[:-len(query_param[-1]) - 1]

    data = await bgm.search_mono(keywords, page=offset + 1, cat=cat)
    if data["error"]:
        switch_pm_text = data["error"]
    else:
        if cat == "prsn":
            switch_pm_text = f"现实人物[{keywords}]的{query_type if query_type else ''}搜索结果"
        elif cat == "crt":
            switch_pm_text = f"虚拟角色[{keywords}]的{query_type if query_type else ''}搜索结果"
        else:
            switch_pm_text = f"人物[{keywords}]的{query_type if query_type else ''}搜索结果"
    next_offset = str(offset + 1) if len(data["list"]) >= 9 else None

    for cop in data["list"]:
        text = (
            f"*{cop['name_cn'] or cop['name']}*\n"+
            (f"{cop['name']}\n" if cop["name_cn"] else "")+
            f"\n{cop['info']}\n"
            f"\n📚 [简介](https://t.me/iv?url=https://bangumi.tv/{cop['type']}/{cop['id']}&rhash=48797fd986e111)"
            f"\n📖 [详情](https://bgm.tv/{cop['type']}/{cop['id']})"
        )
        query_result_list.append(InlineQueryResultArticle(
            id=f"p/c:{cop['id']}",
            title=cop["name_cn"] or cop["name"],
            description=cop["info"],
            input_message_content=InputTextMessageContent(
                text, parse_mode = "markdown", disable_web_page_preview = False
            ),
            thumb_url=cop["img_url"],
            reply_markup=(
                InlineKeyboardMarkup().add(
                    InlineKeyboardButton(
                        text = "人物关联", switch_inline_query_current_chat = f"PS {cop['id']}"
                    )
                )
            ) if cat == "prsn" else None,
        ))
        if query_type == "条目":
            def subject_text(subject, is_sender):
                if is_sender:
                    return InlineQueryResultArticle(
                        id=f"PS:{subject['staff']}{subject['id']}",
                        title=(subject["name_cn"] if subject["name_cn"] else subject["name"]),
                        input_message_content=InputTextMessageContent(
                            message_text=f"/info@{BOT_USERNAME} {subject['id']}", disable_web_page_preview=True
                        ),
                        description=f"[关联{query_type}] " + (f"{subject['name']} | " if subject["name_cn"] else "") + (subject["staff"] if subject["staff"] else ""),
                        thumb_url=subject["image"] if subject["image"] else None,
                    )
                else:
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
                    return InlineQueryResultArticle(
                        id=f"PS:{subject['staff']}{subject['id']}",
                        title=(subject["name_cn"] if subject["name_cn"] else subject["name"]),
                        input_message_content=InputTextMessageContent(
                            text, parse_mode="markdown", disable_web_page_preview=False
                        ),
                        description=f"[关联{query_type}] " + (f"{subject['name']} | " if subject["name_cn"] else "") + (subject["staff"] if subject["staff"] else ""),
                        thumb_url=subject["image"] if subject["image"] else None,
                        reply_markup=InlineKeyboardMarkup().add(*button_list),
                    )
            if cat == "prsn":
                person_related_subjects = await bgm.get_person_subjects(cop["id"])
                if person_related_subjects:
                    query_result_list += [subject_text(p, is_sender) for p in person_related_subjects if "演出" in p.get("staff") and subject_text(p, is_sender) is not None][:5]
            elif cat == "crt":
                character_related_subjects = await bgm.get_character_subjects(cop["id"])
                if character_related_subjects:
                    query_result_list += [subject_text(c, is_sender) for c in character_related_subjects if subject_text(c, is_sender) is not None][:5]
        elif query_type in ["角色", "人物"]:
            def character_text(character):
                text = (
                    f"*{character['name']}*"
                    f"\n{character['staff']}\n"
                    f"\n📚 [简介](https://t.me/iv?url=https://bangumi.tv/character/{character['id']}&rhash=48797fd986e111)"
                    f"\n📖 [详情](https://bgm.tv/character/{character['id']})"
                )
                return InlineQueryResultArticle(
                    id = f"PC:{character['id']}{str(random.randint(0, 1000000000))}",
                    title = character["name"],
                    description = f"[关联{query_type}] " + character['staff'],
                    input_message_content = InputTextMessageContent(
                        text, parse_mode = "markdown", disable_web_page_preview = False
                    ),
                    thumb_url = character["images"]["grid"] if character["images"] else None,
                )
            if cat == "prsn":
                person_related_characters = await bgm.get_person_characters(cop["id"])
                if person_related_characters:
                    query_result_list += [character_text(p) for p in person_related_characters if p.get("staff") == "主角" and character_text(p) is not None][:5]
            elif cat == "crt":
                character_related_persons = await bgm.get_character_persons(cop["id"])
                if character_related_persons:
                    query_result_list += [character_text(c) for c in character_related_persons if character_text(c) is not None][:5]
    return {
        "results": query_result_list[:50],
        "next_offset": next_offset,
        "switch_pm_text": switch_pm_text,
        "switch_pm_parameter": "search",
        "cache_time": 0,
    }