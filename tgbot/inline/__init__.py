from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineQuery

from .mono import query_mono
from .person_related_subjects import query_person_related_subjects
from .search_sender import query_search_sender
from .subject_characters import query_subject_characters


async def global_inline_handler(inline_query: InlineQuery, bot: AsyncTeleBot):
    query: str = inline_query.query
    query_param: list[str] = inline_query.query.split(" ")
    kwargs = {"results": [], "switch_pm_text": "搜索帮助", "switch_pm_parameter": "help", "cache_time": 0}

    # 使用 ID 搜索
    if query.startswith("SC ") or (query.startswith("SC") and len(query) == 2):
        kwargs = {"results": [], "switch_pm_text": "条目关联角色 Subject ID", "switch_pm_parameter": "help", "cache_time": 0}
        if query.startswith("SC ") and len(query_param) > 1 and query_param[1].isdecimal():  # 条目关联的角色
            kwargs = await query_subject_characters(inline_query)
    elif query.startswith("PS ") or (query.startswith("PS") and len(query) == 2):
        kwargs = {"results": [], "switch_pm_text": "人物关联条目 Person ID", "switch_pm_parameter": "help", "cache_time": 0}
        if query.startswith("PS ") and len(query_param) > 1 and query_param[1].isdecimal():  # 人物出演的条目
            kwargs = await query_person_related_subjects(inline_query)
    # 使用关键词搜索
    elif query.startswith("p ") or (query.startswith("p") and len(query) == 1):  # 现实人物搜索
        kwargs = {"results": [], "switch_pm_text": "关键词人物搜索 + [条目/角色]", "switch_pm_parameter": "help", "cache_time": 0}
        query_type = None
        if query.startswith("p ") and len(query_param) > 1:
            if inline_query.query.endswith((" 条目", " 关联")):
                query_type = "条目"
            elif inline_query.query.endswith(" 角色"):
                query_type = "角色"
            kwargs = await query_mono(inline_query, "prsn", query_type)
    elif query.startswith("c ") or (query.startswith("c") and len(query) == 1):  # 虚拟人物搜索
        kwargs = {"results": [], "switch_pm_text": "关键词角色搜索 + [条目/人物(cv)]", "switch_pm_parameter": "help", "cache_time": 0}
        query_type = None
        if query.startswith("c ") and len(query_param) > 1:
            if inline_query.query.endswith((" 条目", " 关联")):
                query_type = "条目"
            elif inline_query.query.endswith((" 人物", " 出演", " cv", " CV")):
                query_type = "人物"
            kwargs = await query_mono(inline_query, "crt", query_type)
    else:  # 普通搜索
        query_type = None
        if inline_query.query.endswith(" 角色"):
            query_type = "角色"
        kwargs = await query_search_sender(inline_query, query_type)

    return await bot.answer_inline_query(inline_query_id=inline_query.id, **kwargs)