import random

from telebot.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           InlineQuery, InlineQueryResultArticle,
                           InputTextMessageContent)

from utils.config_vars import BOT_USERNAME, bgm
from utils.converts import number_to_week, parse_markdown_v2, subject_type_to_emoji


async def query_search(inline_query: InlineQuery, query_type: str = None, is_sender: bool = False):
    """关键词 搜索"""
    offset = int(inline_query.offset or 0)
    query_result_list: list[InlineQueryResultArticle] = []
    query_param = inline_query.query.split(" ")
    query = inline_query.query
    if query_type:
        query = query[:-len(query_param[-1]) - 1]

    if query.startswith("📚") or query.startswith("B ") or query.startswith("b "):
        subject_list = await bgm.search_subjects(query[1:], subject_type=1, response_group="large", start=offset)
        pm_text = "书籍搜索模式,请直接输入关键词"
    elif query.startswith("🌸") or query.startswith("A ") or query.startswith("a "):
        subject_list = await bgm.search_subjects(query[1:], subject_type=2, response_group="large", start=offset)
        pm_text = "动画搜索模式,请直接输入关键词"
    elif query.startswith("🎵") or query.startswith("M ") or query.startswith("m "):
        subject_list = await bgm.search_subjects(query[1:], subject_type=3, response_group="large", start=offset)
        pm_text = "音乐搜索模式,请直接输入关键词"
    elif query.startswith("🎮") or query.startswith("G ") or query.startswith("g "):
        subject_list = await bgm.search_subjects(query[1:], subject_type=4, response_group="large", start=offset)
        pm_text = "游戏搜索模式,请直接输入关键词"
    elif query.startswith("📺") or query.startswith("R ") or query.startswith("r "):
        subject_list = await bgm.search_subjects(query[1:], subject_type=6, response_group="large", start=offset)
        pm_text = "剧集搜索模式,请直接输入关键词"
    else:
        subject_list = await bgm.search_subjects(query, response_group="large", start=offset)
        pm_text = "条目搜索"
    if subject_list.get("list"):
        for subject in subject_list["list"]:
            emoji = subject_type_to_emoji(subject["type"])
            if is_sender:
                qr = InlineQueryResultArticle(
                    id=subject["id"],
                    title=emoji + (subject["name_cn"] or subject["name"]),
                    input_message_content=InputTextMessageContent(
                        message_text=f"/info@{BOT_USERNAME} {subject['id']}",
                        disable_web_page_preview=True,
                    ),
                    description=subject["name"] if subject["name_cn"] else None,
                    thumb_url=subject["images"]["medium"] if subject["images"] else None,
                )
                query_result_list.append(qr)
            else:
                text = f"搜索结果{emoji}:\n*{parse_markdown_v2(subject['name'])}*\n"
                if subject['name_cn']:
                    text += f"{parse_markdown_v2(subject['name_cn'])}\n"
                text += "\n"
                text += f"*BGM ID：*`{subject['id']}`\n"
                if 'rating' in subject and subject['rating']['score']:
                    text += f"*➤ BGM 平均评分：*`{subject['rating']['score']}`🌟\n"
                if subject["type"] == 2 or subject["type"] == 6:  # 当类型为anime或real时
                    if 'eps' in subject and subject['eps']:
                        text += f"*➤ 集数：*共`{subject['eps']}`集\n"
                    if subject['air_date']:
                        text += f"*➤ 放送日期：*`{parse_markdown_v2(subject['air_date'])}`\n"
                    if subject['air_weekday']:
                        text += f"*➤ 放送星期：*`{number_to_week(subject['air_weekday'])}`\n"
                if subject["type"] == 1:  # 当类型为book时
                    if 'eps' in subject and subject['eps']:
                        text += f"*➤ 话数：*共`{subject['eps']}`话\n"
                    if subject['air_date']:
                        text += f"*➤ 发售日期：*`{parse_markdown_v2(subject['air_date'])}`\n"
                if subject["type"] == 3:  # 当类型为music时
                    if subject['air_date']:
                        text += f"*➤ 发售日期：*`{parse_markdown_v2(subject['air_date'])}`\n"
                if subject["type"] == 4:  # 当类型为game时
                    if subject['air_date']:
                        text += f"*➤ 发行日期：*`{parse_markdown_v2(subject['air_date'])}`\n"
                text += (
                    f"\n📚 [简介](https://t.me/iv?url=https://bgm.tv/subject/{subject['id']}&rhash=ce4f44b013e2e8)"
                    f"\n📖 [详情](https://bgm.tv/subject/{subject['id']})"
                    f"\n💬 [吐槽箱](https://bgm.tv/subject/{subject['id']}/comments)"
                )
                button_list = []
                if subject["type"] != 3:  # 当类型为anime或real时
                    button_list.append(
                        InlineKeyboardButton(
                            text="巡礼", switch_inline_query_current_chat=f"anitabi {subject['id']}"
                        ),
                    )
                    button_list.append(
                        InlineKeyboardButton(
                            text="角色", switch_inline_query_current_chat=f"SC {subject['id']}"
                        )
                    )
                button_list.append(
                    InlineKeyboardButton(
                        text='去管理', url=f"t.me/{BOT_USERNAME}?start={subject['id']}"
                    )
                )
                qr = InlineQueryResultArticle(
                    id=subject['id'],
                    title=emoji + (subject["name_cn"] if subject["name_cn"] else subject["name"]),
                    input_message_content=InputTextMessageContent(
                        text, parse_mode="markdownV2", disable_web_page_preview=False
                    ),
                    description=subject["name"] if subject["name_cn"] else None,
                    thumb_url=subject["images"]["medium"] if subject["images"] else None,
                    reply_markup=InlineKeyboardMarkup().add(*button_list),
                )
                query_result_list.append(qr)
            if query_type == "角色":
                def character_text(character):
                    text = (
                        f"*{character['name']}*"
                        f"\n{character['relation']}\n"
                        f"\n📚 [简介](https://t.me/iv?url=https://bangumi.tv/character/{character['id']}&rhash=48797fd986e111)"
                        f"\n📖 [详情](https://bgm.tv/character/{character['id']})"
                    )
                    return InlineQueryResultArticle(
                        id = f"PC:{character['id']}{str(random.randint(0, 1000000000))}",
                        title = character["name"],
                        description = f"[关联{query_type}] " + character['relation'],
                        input_message_content = InputTextMessageContent(
                            text, parse_mode = "markdown", disable_web_page_preview = False
                        ),
                        thumb_url = character["images"]["grid"] if character["images"] else None,
                    )
                subject_related_characters = await bgm.get_subject_characters(subject["id"])
                if subject_related_characters:
                    query_result_list += [character_text(p) for p in subject_related_characters if p.get("relation") == "主角" and character_text(p) is not None][:5]
        pm_text = f"共 {subject_list['results']} 个结果"
    return {
        "results": query_result_list,
        "next_offset": str(offset + 10),
        "switch_pm_text": pm_text,
        "switch_pm_parameter": "help",
        "cache_time": 0,
    }