import random

from telebot.types import (InlineQuery, InlineQueryResultArticle,
                           InputTextMessageContent)

from utils.config_vars import BOT_USERNAME, bgm
from utils.converts import subject_type_to_emoji


async def query_search_sender(inline_query: InlineQuery, query_type: str = None):
    """私聊或@ 关键词 搜索发送命令"""
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