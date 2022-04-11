"""inline 方式私聊搜索或者在任何位置搜索前使用@"""
from typing import List

import telebot
from telebot.types import InlineQueryResultArticle

from config import BOT_USERNAME
from utils.api import get_person_info, get_person_related_subjects, search_subject, get_subject_characters, \
    get_subject_info, get_mono_search, get_subject_persons
from utils.converts import subject_type_to_emoji, full_group_by


def query_subject_characters(inline_query):
    """SC + 条目ID 获取条目关联角色"""
    offset = int(inline_query.offset or 0)
    query_result_list: List[InlineQueryResultArticle] = []
    query_param = inline_query.query.split(' ')
    subject_id = query_param[1]
    subject_info = get_subject_info(subject_id)
    subject_name = subject_info['name_cn'] or subject_info['name']
    subject_characters = get_subject_characters(subject_id)
    new_subject_characters = []
    group = full_group_by(subject_characters, lambda c: c['relation'])
    new_subject_characters.extend(group.pop('主角', []))
    new_subject_characters.extend(group.pop('配角', []))
    new_subject_characters.extend(group.pop('客串', []))
    for k in group:
        new_subject_characters.extend(group[k])
    switch_pm_text = subject_name + " 角色列表"
    for character in new_subject_characters[offset: offset + 49]:
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
    if len(new_subject_characters) == 0:
        qr = telebot.types.InlineQueryResultArticle(
            id=f"-1",
            title="这个条目没有角色QAQ",
            input_message_content=telebot.types.InputTextMessageContent(
                "点我干嘛!😡",
                parse_mode="markdown",
                disable_web_page_preview=False
            ),
            thumb_url=None
        )
        query_result_list.append(qr)
    if len(new_subject_characters) <= offset + 49:
        next_offset = None
    else:
        next_offset = offset + 49
    return {'results': query_result_list, 'next_offset': next_offset,
            'switch_pm_text': switch_pm_text, 'switch_pm_parameter': subject_id, 'cache_time': 3600}


def query_subject_person(inline_query):
    """SP + 条目ID 获取条目关联STAFF"""
    offset = int(inline_query.offset or 0)
    query_result_list: List[InlineQueryResultArticle] = []
    query_param = inline_query.query.split(' ')
    subject_id = query_param[1]
    subject_info = get_subject_info(subject_id)
    subject_name = subject_info['name_cn'] or subject_info['name']
    try:
        subject_persons = get_subject_persons(subject_id)
    except FileNotFoundError:
        subject_persons = []
    new_subject_persons = []
    group = full_group_by(subject_persons, lambda c: c['relation'])
    new_subject_persons.extend(group.pop('原作', []))  # TODO 补充排序顺序
    new_subject_persons.extend(group.pop('导演', []))
    new_subject_persons.extend(group.pop('监督', []))
    new_subject_persons.extend(group.pop('原画', []))
    for k in group:
        new_subject_persons.extend(group[k])
    switch_pm_text = subject_name + " STAFF列表"
    for num, person in enumerate(new_subject_persons[offset: offset + 49]):
        text = f"*{person['name']}*"
        description = person['relation']
        text += (f"\n{description}\n"
                 f"\n📚 [简介](https://t.me/iv?url=https://bangumi.tv/person/{person['id']}"
                 f"&rhash=48797fd986e111)"
                 f"\n📖 [详情](https://bgm.tv/character/{person['id']})")
        qr = telebot.types.InlineQueryResultArticle(
            id=f"sp:{person['id']}:{num}",
            title=person['name'],
            description=description,
            input_message_content=telebot.types.InputTextMessageContent(
                text,
                parse_mode="markdown",
                disable_web_page_preview=False
            ),
            thumb_url=person['images']['grid'] if person['images'] else None
        )
        query_result_list.append(qr)
    if len(new_subject_persons) == 0:
        qr = telebot.types.InlineQueryResultArticle(
            id=f"-1",
            title="这个条目没有staff QAQ",
            input_message_content=telebot.types.InputTextMessageContent(
                "点我干嘛!😡",
                parse_mode="markdown",
                disable_web_page_preview=False
            ),
            thumb_url=None
        )
        query_result_list.append(qr)
    if len(new_subject_persons) <= offset + 49:
        next_offset = None
    else:
        next_offset = offset + 49
    return {'results': query_result_list, 'next_offset': next_offset,
            'switch_pm_text': switch_pm_text, 'switch_pm_parameter': subject_id, 'cache_time': 3600}


def query_subject_info(inline_query):
    """S + 条目ID 发送命令 获取条目详情"""
    query_param = inline_query.query.split(' ')
    subject_id = query_param[1]

    subject_info = get_subject_info(subject_id)
    switch_pm_text = (subject_info['name_cn'] or subject_info['name'])
    qr = telebot.types.InlineQueryResultArticle(
        id=f"S:{subject_id}", title=subject_type_to_emoji(subject_info['type']) +
                                    (subject_info["name_cn"] or subject_info["name"]),
        input_message_content=telebot.types.InputTextMessageContent(
            message_text=f"/info@{BOT_USERNAME} {subject_id}",
            disable_web_page_preview=True
        ), description=subject_info["name"] if subject_info["name_cn"] else None,
        thumb_url=subject_info["images"]["medium"] if subject_info["images"] else None
    )
    return {'query_result_list': [qr], 'switch_pm_text': switch_pm_text,
            'switch_pm_parameter': f"{subject_info['id']}", 'cache_time': 0}


def query_person_related_subjects(inline_query):
    """PS + 人物ID 发送命令 获取人物关联条目"""
    offset = int(inline_query.offset or 0)
    query_result_list: List[InlineQueryResultArticle] = []
    query_param = inline_query.query.split(' ')
    if query_param[1].isdecimal():
        person_id = query_param[1]
        person_name = get_person_info(person_id)['name']
    else:
        mono_search_data = get_mono_search(query_param[1], page=1, cat='prsn')
        person_id = mono_search_data['list'][0]['id']
        person_name = mono_search_data['list'][0]['name']

    person_related_subjects = get_person_related_subjects(person_id)
    switch_pm_text = person_name + " 人物关联列表"
    for subject in person_related_subjects[offset: offset + 50]:
        qr = telebot.types.InlineQueryResultArticle(
            id=f"{subject['staff']}:{subject['id']}",
            title=(subject["name_cn"] if subject["name_cn"]
                   else subject["name"]),
            input_message_content=telebot.types.InputTextMessageContent(
                message_text=f"/info@{BOT_USERNAME} {subject['id']}",
                disable_web_page_preview=True
            ),
            description=(f"{subject['name']} | " if subject["name_cn"] else '') + (
                subject['staff'] if subject["staff"] else ''),
            thumb_url=subject["image"] if subject["image"] else None,
        )
        query_result_list.append(qr)
    return {'results': query_result_list, 'next_offset': str(offset + 50),
            'switch_pm_text': switch_pm_text, 'switch_pm_parameter': "help", 'cache_time': 3600}


def query_search_sender(inline_query):
    """私聊或@ 关键词 搜索发送命令"""
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
    return {'results': query_result_list, 'next_offset': str(offset + 25),
            'switch_pm_text': pm_text, 'switch_pm_parameter': "help", 'cache_time': 0}


def query_search_subject_characters(inline_query):
    """关键词 + 角色 搜索条目关联角色"""
    split = inline_query.offset.split('|')
    if inline_query.offset:
        subject_num = int(split[0])
    else:
        subject_num = 0
    inline_query.offset = subject_num // 25  # 搜索的第几页
    query_param = inline_query.query.split(' ')
    inline_query.query = inline_query.query[:-len(query_param[-1]) - 1]
    search = query_search_sender(inline_query)
    if len(search['results']) <= subject_num % 25:
        return {'results': [], 'next_offset': None,
                'switch_pm_parameter': "help", 'cache_time': 0}
    query_result_list: List[InlineQueryResultArticle] = [search['results'][subject_num % 25]]
    subject = search['results'][subject_num % 25].id
    inline_query.query = f"C {subject}"
    if len(split) < 2:
        inline_query.offset = 0
    else:
        inline_query.offset = int(split[1])
    subject_characters = query_subject_characters(inline_query)
    if subject_characters['next_offset']:
        next_offset = f"{subject_num}|{subject_characters['next_offset']}"
    else:
        next_offset = f"{subject_num + 1}|0"
    query_result_list.extend(subject_characters['results'])

    return {'results': query_result_list, 'next_offset': next_offset,
            'switch_pm_text': "条目角色模式", 'switch_pm_parameter': "help", 'cache_time': 0}


def query_mono(inline_query, cat):
    """人物搜索
    :param inline_query: 查询人物关键词
    :param cat = prsn -> 查询人物
    :param cat = crt -> 查询角色"""
    offset = int(inline_query.offset or 0)
    query_result_list: List[InlineQueryResultArticle] = []
    query_param = inline_query.query.split(' ')
    keywords = inline_query.query[len(query_param[0]) + 1:]

    data = get_mono_search(keywords, page=offset + 1, cat=cat)
    if data['error']:
        switch_pm_text = data['error']
    else:
        if cat == 'prsn':
            switch_pm_text = f"现实人物[{keywords}]的搜索结果"
        elif cat == 'crt':
            switch_pm_text = f"虚拟角色[{keywords}]的搜索结果"
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
            thumb_url=cop['img_url'],
            reply_markup=(telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton(
                text="人物关联", switch_inline_query_current_chat=f"PS {cop['id']}"))) if cat == 'prsn' else None
        )
        query_result_list.append(qr)
    return {'results': query_result_list, 'next_offset': next_offset,
            'switch_pm_text': switch_pm_text, 'switch_pm_parameter': "search", 'cache_time': 0}


# def query_mono_subject(inline_query, cat):
#     offset = int(inline_query.offset or 1)
#     query_result_list: List[InlineQueryResultArticle] = []
#     query_param = inline_query.query.split(' ')
#     keywords = inline_query.querya[len(query_param[0]) + 1:-len(query_param[-1]) - 1]
#     page = offset // 9 + 1
#     data = get_mono_search(keywords, page=page, cat=cat)
#     if data['error']:
#         switch_pm_text = data['error']
#     else:
#         if cat == 'prsn':
#             switch_pm_text = f"角色参与条目:"
#         elif cat == 'crt':
#             switch_pm_text = f"人物参与条目:"
#         else:
#             switch_pm_text = f"参与条目:"
#
#
#     for cop in data['list']:
#         text = f"*{cop['name_cn'] or cop['name']}*\n"
#         text += f"{cop['name']}\n" if cop['name_cn'] else ''
#         description = cop['info']
#         text += (f"\n{description}\n"
#                  f"\n📚 [简介](https://t.me/iv?url=https://bangumi.tv/{cop['type']}/{cop['id']}"
#                  f"&rhash=48797fd986e111)"
#                  f"\n📖 [详情](https://bgm.tv/{cop['type']}/{cop['id']})")
#         qr = telebot.types.InlineQueryResultArticle(
#             id=f"sc:{cop['id']}",
#             title=cop['name_cn'] or cop['name'],
#             description=description,
#             input_message_content=telebot.types.InputTextMessageContent(
#                 text,
#                 parse_mode="markdown",
#                 disable_web_page_preview=False
#             ),
#             thumb_url=cop['img_url'],
#             reply_markup=(telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton(
#                 text="人物关联", switch_inline_query_current_chat=f"PS {cop['id']}"))) if cat == 'prsn' else None
#         )
#         query_result_list.append(qr)
#     return {'results': query_result_list, 'next_offset': next_offset,
#             'switch_pm_text': switch_pm_text, 'switch_pm_parameter': "search", 'cache_time': 3600}


def query_sender_text(inline_query, bot):
    """私聊搜索"""
    query: str = inline_query.query
    query_param = inline_query.query.split(' ')

    # 使用 ID 搜索
    if query.startswith("S ") and query_param[1].isdecimal():  # 条目id 详情
        kwargs = query_subject_info(inline_query)
    elif query.startswith("PS ") and query_param[1].isdecimal():  # 人物出演的条目
        kwargs = query_person_related_subjects(inline_query)
    elif query.startswith("SC ") and query_param[1].isdecimal():  # 条目关联的角色
        kwargs = query_subject_characters(inline_query)
    elif query.startswith("SP ") and query_param[1].isdecimal():  # 条目关联的STAF
        kwargs = query_subject_person(inline_query)
    # 使用关键词搜索
    elif query.startswith("p "):  # 现实人物搜索
        if inline_query.query.endswith((" 条目", " 关联")):
            return
        elif inline_query.query.endswith(" 角色"):
            return
        else:
            kwargs = query_mono(inline_query, 'prsn')

    elif query.startswith("c "):  # 虚拟人物搜索
        if inline_query.query.endswith((" 条目", " 关联")):
            return
        elif inline_query.query.endswith((" 人物", " 出演", " cv", " CV")):
            return
        else:
            kwargs = query_mono(inline_query, 'crt')

    elif query.startswith("@"):  # @ 搜索 转换至公共搜索
        inline_query.query = inline_query.query.lstrip('@')
        from plugins.inline.public import query_public_text
        return query_public_text(inline_query, bot)  # 公共搜索

    else:  # search_subject 普通搜索
        if inline_query.query.endswith(" 角色"):
            kwargs = query_search_subject_characters(inline_query)
        else:
            kwargs = query_search_sender(inline_query)  # TODO 后缀为 ' 人物' ' 角色' 查询第一个结果的 ~

    return bot.answer_inline_query(inline_query_id=inline_query.id, **kwargs)
