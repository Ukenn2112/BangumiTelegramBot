from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineQuery

from .mono import query_mono
from .query_character import (query_character_related_persons,
                              query_character_related_subjects)
from .query_person import (query_person_related_characters,
                           query_person_related_subjects)
from .query_subject import query_subject_characters, query_subject_person
from .search_sender import query_search


async def global_inline_handler(inline_query: InlineQuery, bot: AsyncTeleBot):
    is_sender = True if inline_query.chat_type == "sender" else False # 是否为私聊
    if inline_query.query.startswith("@"): is_sender, inline_query.query = True, inline_query.query[1:]
    query: str = inline_query.query
    query_param: list[str] = inline_query.query.split(" ")
    kwargs = {"results": [], "switch_pm_text": "搜索帮助", "switch_pm_parameter": "help", "cache_time": 0}

    # 使用 ID 搜索
    if query.startswith("SC ") or (query.startswith("SC") and len(query) == 2):
        kwargs = {"results": [], "switch_pm_text": "条目关联角色 Subject ID", "switch_pm_parameter": "help", "cache_time": 0}
        if query.startswith("SC ") and len(query_param) > 1 and query_param[1].isdecimal():  # 条目关联的角色
            kwargs = await query_subject_characters(inline_query)
    elif query.startswith("SP ") or (query.startswith("SP") and len(query) == 2):
        kwargs = {"results": [], "switch_pm_text": "条目关联人物 Subject ID", "switch_pm_parameter": "help", "cache_time": 0}
        if query.startswith("SP ") and len(query_param) > 1 and query_param[1].isdecimal():  # 条目关联人物
            kwargs = await query_subject_person(inline_query)
    elif query.startswith("PC ") or (query.startswith("PC") and len(query) == 2):
        kwargs = {"results": [], "switch_pm_text": "人物关联角色 Person ID", "switch_pm_parameter": "help", "cache_time": 0}
        if query.startswith("PC ") and len(query_param) > 1 and query_param[1].isdecimal():  # 人物关联角色
            kwargs = await query_person_related_characters(inline_query)
    elif query.startswith("PS ") or (query.startswith("PS") and len(query) == 2):
        kwargs = {"results": [], "switch_pm_text": "人物关联条目 Person ID", "switch_pm_parameter": "help", "cache_time": 0}
        if query.startswith("PS ") and len(query_param) > 1 and query_param[1].isdecimal():  # 人物关联条目
            kwargs = await query_person_related_subjects(inline_query, is_sender)
    elif query.startswith("CP ") or (query.startswith("CP") and len(query) == 2):
        kwargs = {"results": [], "switch_pm_text": "角色关联人物 Character ID", "switch_pm_parameter": "help", "cache_time": 0}
        if query.startswith("CP ") and len(query_param) > 1 and query_param[1].isdecimal():  # 角色关联人物
            kwargs = await query_character_related_persons(inline_query)
    elif query.startswith("CS ") or (query.startswith("CS") and len(query) == 2):
        kwargs = {"results": [], "switch_pm_text": "角色关联条目 Character ID", "switch_pm_parameter": "help", "cache_time": 0}
        if query.startswith("CS ") and len(query_param) > 1 and query_param[1].isdecimal():  # 角色关联条目
            kwargs = await query_character_related_subjects(inline_query, is_sender)

    # 使用关键词搜索
    elif query.startswith("p ") or (query.startswith("p") and len(query) == 1):  # 现实人物搜索
        kwargs = {"results": [], "switch_pm_text": "关键词人物搜索 + [条目/角色]", "switch_pm_parameter": "help", "cache_time": 0}
        query_type = None
        if query.startswith("p ") and len(query_param) > 1:
            if inline_query.query.endswith((" 条目", " 关联")):
                query_type = "条目"
            elif inline_query.query.endswith(" 角色"):
                query_type = "角色"
            kwargs = await query_mono(inline_query, "prsn", query_type, is_sender)
    elif query.startswith("c ") or (query.startswith("c") and len(query) == 1):  # 虚拟人物搜索
        kwargs = {"results": [], "switch_pm_text": "关键词角色搜索 + [条目/人物(cv)]", "switch_pm_parameter": "help", "cache_time": 0}
        query_type = None
        if query.startswith("c ") and len(query_param) > 1:
            if inline_query.query.endswith((" 条目", " 关联")):
                query_type = "条目"
            elif inline_query.query.endswith((" 人物", " 出演", " cv", " CV")):
                query_type = "人物"
            kwargs = await query_mono(inline_query, "crt", query_type, is_sender)
    else:  # 普通搜索
        query_type = None
        if inline_query.query.endswith(" 角色"):
            query_type = "角色"
        kwargs = await query_search(inline_query, query_type, is_sender)

    return await bot.answer_inline_query(inline_query_id=inline_query.id, **kwargs)