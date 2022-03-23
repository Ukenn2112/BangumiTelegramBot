"""inline 方式私聊搜索或者在任何位置搜索前使用@"""
from typing import List

import telebot
from telebot.types import InlineQueryResultArticle

from config import BOT_USERNAME
from utils.api import search_subject, get_subject_characters, get_subject_info, get_mono_search
from utils.converts import subject_type_to_emoji, full_group_by


def query_subject_characters(inline_query, bot):
    offset = int(inline_query.offset or 0)
    query_result_list: List[InlineQueryResultArticle] = []
    query_param = inline_query.query.split(' ')
    subject_id = query_param[0]

    subject_characters = get_subject_characters(subject_id)
    new_subject_characters = []
    group = full_group_by(subject_characters, lambda c: c['relation'])
    if '主角' in group:
        new_subject_characters.extend(group['主角'])
    if '配角' in group:
        new_subject_characters.extend(group['配角'])
    if '客串' in group:
        new_subject_characters.extend(group['客串'])
    for k in group:
        if k != '主角' and k != '配角' and k != '客串':
            new_subject_characters.extend(group[k])

    subject_info = get_subject_info(subject_id)
    switch_pm_text = (subject_info['name_cn'] or subject_info['name']) + " 角色列表"
    for character in new_subject_characters[offset: offset + 50]:
        text = f"*{character['name']}*"
        description = character['relation']
        if character['actors']:
            description += f" | CV: {[cv['name'] for cv in character['actors']][0]}"
        text += (f"\n{description}\n"
                 f"\n📚 [简介](https://t.me/iv?url=https://bangumi.tv/character/{character['id']}"
                 f"&rhash=48797fd986e111)"
                 f"\n📖 [详情](https://bgm.tv/character/{character['id']})")
        qr = telebot.types.InlineQueryResultArticle(
            id=f"sc:{character['id']}",
            title=character['name'],
            description=description,
            input_message_content=telebot.types.InputTextMessageContent(
                text,
                parse_mode="markdown",
                disable_web_page_preview=False
            ),
            thumb_url=character['images']['grid'] if character['images'] else None
        )
        query_result_list.append(qr)
    bot.answer_inline_query(inline_query.id, query_result_list, next_offset=str(offset + 50),
                            switch_pm_text=switch_pm_text, switch_pm_parameter=subject_id, cache_time=3600)


def query_subject_info(inline_query, bot):
    query_param = inline_query.query.split(' ')
    subject_id = query_param[1]

    subject_info = get_subject_info(subject_id)
    switch_pm_text = (subject_info['name_cn'] or subject_info['name'])
    qr = telebot.types.InlineQueryResultArticle(
        id=f"S:{subject_id}", title=subject_type_to_emoji(subject_info['type']) +
                                    (subject_info["name_cn"] or subject_info["name"])
        , input_message_content=telebot.types.InputTextMessageContent(
            message_text=f"/info@{BOT_USERNAME} {subject_id}",
            disable_web_page_preview=True
        ), description=subject_info["name"] if subject_info["name_cn"] else None,
        thumb_url=subject_info["images"]["medium"] if subject_info["images"] else None
    )
    bot.answer_inline_query(inline_query.id, [qr],
                            switch_pm_text=switch_pm_text, switch_pm_parameter=f"{subject_info['id']}",
                            cache_time=0)


def query_search_sender(inline_query, bot):
    offset = int(inline_query.offset or 0)
    query_result_list: List[InlineQueryResultArticle] = []
    query = inline_query.query
    if query.startswith("📚") or query.startswith("B ") or query.startswith("b "):
        subject_list = search_subject(query[1:], response_group="large", start=offset, type_=1)
        pm_text = "书籍搜索模式,请直接输入关键词"
    elif query.startswith("🌸") or query.startswith("A ") or query.startswith("a "):
        subject_list = search_subject(query[1:], response_group="large", start=offset, type_=2)
        pm_text = "动画搜索模式,请直接输入关键词"
    elif query.startswith("🎵") or query.startswith("M ") or query.startswith("m "):
        subject_list = search_subject(query[1:], response_group="large", start=offset, type_=3)
        pm_text = "音乐搜索模式,请直接输入关键词"
    elif query.startswith("🎮") or query.startswith("G ") or query.startswith("g "):
        subject_list = search_subject(query[1:], response_group="large", start=offset, type_=4)
        pm_text = "游戏搜索模式,请直接输入关键词"
    elif query.startswith("📺") or query.startswith("R ") or query.startswith("r "):
        subject_list = search_subject(query[1:], response_group="large", start=offset, type_=6)
        pm_text = "剧集搜索模式,请直接输入关键词"
    else:
        subject_list = search_subject(inline_query.query, response_group="large", start=offset)
        pm_text = "条目搜索"
    if 'list' in subject_list and subject_list["list"] is not None:
        for subject in subject_list["list"]:
            emoji = subject_type_to_emoji(subject["type"])
            qr = telebot.types.InlineQueryResultArticle(
                id=subject['id'], title=emoji + (subject["name_cn"] or subject["name"]),
                input_message_content=telebot.types.InputTextMessageContent(
                    message_text=f"/info@{BOT_USERNAME} {subject['id']}",
                    disable_web_page_preview=True
                ),
                description=subject["name"] if subject["name_cn"] else None,
                thumb_url=subject["images"]["medium"] if subject["images"] else None
            )
            query_result_list.append(qr)
        pm_text = f"共 {subject_list['results']} 个结果"
    bot.answer_inline_query(inline_query.id, query_result_list, next_offset=str(offset + 25),
                            switch_pm_text=pm_text, switch_pm_parameter="help", cache_time=0)


def query_mono(inline_query, bot, cat):
    offset = int(inline_query.offset or 1)
    query_result_list: List[InlineQueryResultArticle] = []
    query_param = inline_query.query.split(' ')
    keywords = inline_query.query[len(query_param[0]) + 1:]

    data = get_mono_search(keywords, page=offset, cat=cat)
    if data['error']:
        switch_pm_text = data['error']
    else:
        if cat == 'prsn':
            switch_pm_text = f"现实人物[{keywords}]的搜索结果"
        elif cat == 'crt':
            switch_pm_text = f"虚拟人物[{keywords}]的搜索结果"
        else:
            switch_pm_text = f"人物[{keywords}]的搜索结果"
    next_offset = str(offset + 1) if len(data['list']) >= 9 else None

    for cop in data['list']:
        text = f"*{cop['name_cn'] or cop['name']}*\n"
        text += f"{cop['name']}\n" if cop['name_cn'] else ''
        description = cop['info']
        text += (f"\n{description}\n"
                 f"\n📚 [简介](https://t.me/iv?url=https://bangumi.tv/{cop['type']}/{cop['id']}"
                 f"&rhash=48797fd986e111)"
                 f"\n📖 [详情](https://bgm.tv/{cop['type']}/{cop['id']})")
        qr = telebot.types.InlineQueryResultArticle(
            id=f"sc:{cop['id']}",
            title=cop['name_cn'] or cop['name'],
            description=description,
            input_message_content=telebot.types.InputTextMessageContent(
                text,
                parse_mode="markdown",
                disable_web_page_preview=False
            ),
            thumb_url=cop['img_url']
        )
        query_result_list.append(qr)
    bot.answer_inline_query(inline_query.id, query_result_list, next_offset=next_offset,
                            switch_pm_text=switch_pm_text, switch_pm_parameter="search", cache_time=3600)


def query_sender_text(inline_query, bot):
    query: str = inline_query.query
    query_param = inline_query.query.split(' ')
    if query.endswith(" 角色") and query_param[0].isdecimal():
        # subject_characters 条目角色
        query_subject_characters(inline_query, bot)
    elif query.startswith("P "):
        query_mono(inline_query, bot, 'prsn')
    elif query.startswith("C "):
        query_mono(inline_query, bot, 'crt')
    elif query.startswith("S ") and query_param[1].isdecimal():
        # subject_info 条目
        query_subject_info(inline_query, bot)
    else:
        # search_subject 普通搜索
        query_search_sender(inline_query, bot)
