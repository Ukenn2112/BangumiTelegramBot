"""inline 方式公共搜索"""
from smtpd import PureProxy
from turtle import pu
from typing import List

import telebot
from telebot.types import InlineQueryResultArticle

from config import BOT_USERNAME
from plugins.callback.subject_page import gander_page_text
from plugins.inline.sender import query_subject_characters, query_search_sender, query_mono
from utils.api import anime_img, get_mono_search, get_person_info, get_person_related_subjects, search_subject, get_subject_info
from utils.converts import subject_type_to_emoji, parse_markdown_v2, number_to_week


def query_subject_info(inline_query, bot):
    subject_id = inline_query.query.split(" ")[1]
    subject_info = get_subject_info(subject_id)
    text = gander_page_text(subject_id, subject_info=subject_info)
    img_url = anime_img(subject_id)
    if subject_info:
        if not img_url:
            qr = telebot.types.InlineQueryResultArticle(
                id=f"S:{subject_id}",
                title=subject_type_to_emoji(subject_info['type']) + (
                    subject_info["name_cn"] if subject_info["name_cn"]
                    else subject_info["name"]),
                input_message_content=telebot.types.InputTextMessageContent(
                    text,
                    parse_mode="markdown",
                    disable_web_page_preview=True
                ),
                description=subject_info["name"] if subject_info["name_cn"] else None,
                thumb_url=subject_info["images"]["medium"] if subject_info["images"] else None,
                reply_markup=telebot.types.InlineKeyboardMarkup().add(
                    telebot.types.InlineKeyboardButton(text='去管理',
                                                       url=f"t.me/{BOT_USERNAME}?start={subject_info['id']}"))
            )
        else:
            qr = telebot.types.InlineQueryResultPhoto(
                id=f"S:{subject_id}",
                photo_url=img_url,
                title=subject_type_to_emoji(subject_info['type']) + (
                    subject_info["name_cn"] if subject_info["name_cn"]
                    else subject_info["name"]),
                caption=text,
                parse_mode="markdown",
                description=subject_info["name"] if subject_info["name_cn"] else None,
                thumb_url=subject_info["images"]["medium"] if subject_info["images"] else None,
                reply_markup=telebot.types.InlineKeyboardMarkup().add(
                    telebot.types.InlineKeyboardButton(text='去管理',
                                                       url=f"t.me/{BOT_USERNAME}?start={subject_info['id']}"))
            )
        bot.answer_inline_query(inline_query.id, [qr],
                                switch_pm_text=subject_info['name_cn'] or subject_info['name'],
                                switch_pm_parameter=f"{subject_info['id']}", cache_time=0)


def query_person_related_subjects(inline_query, bot):
    offset = int(inline_query.offset or 0)
    query_result_list: List[InlineQueryResultArticle] = []
    query_param = inline_query.query.split(' ')
    if query_param[1].isdecimal():
        person_id = query_param[1]
        person_name = get_person_info(person_id)['name']
    else:
        mono_search_data = get_mono_search(query_param[1], page=1, cat='prsn')
        if len(mono_search_data) != 0 and mono_search_data['list'] is not None:
            person_id = mono_search_data['list'][0]['id']
            person_name = mono_search_data['list'][0]['name']
        else:
            return bot.answer_inline_query(inline_query.id, [], switch_pm_text="无结果, 请输入完整关键字", switch_pm_parameter="search", cache_time=0)
    person_related_subjects = get_person_related_subjects(person_id)
    switch_pm_text = person_name + " 人物关联列表"
    for subject in person_related_subjects[offset: offset + 25]:
        text = f"*{subject['name_cn'] or subject['name']}*\n"
        text += f"{subject['name']}\n" if subject['name_cn'] else ''

        text += f"\n*BGM ID：*`{subject['id']}`"
        text += f"\n📚 [简介](https://t.me/iv?url=https://bgm.tv/subject/{subject['id']}&rhash=ce4f44b013e2e8)" \
                f"\n📖 [详情](https://bgm.tv/subject/{subject['id']})" \
                f"\n💬 [吐槽箱](https://bgm.tv/subject/{subject['id']}/comments)"

        button_list = [telebot.types.InlineKeyboardButton(
                text="更多信息", switch_inline_query_current_chat=f"S {subject['id']}")]
        button_list.append(telebot.types.InlineKeyboardButton(
            text="角色", switch_inline_query_current_chat=f"{subject['id']} 角色"))
        button_list.append(telebot.types.InlineKeyboardButton(
            text='去管理', url=f"t.me/{BOT_USERNAME}?start={subject['id']}"))
        qr = telebot.types.InlineQueryResultArticle(
            id=subject['id'],
            title=(subject["name_cn"] if subject["name_cn"] else subject["name"]),
            input_message_content=telebot.types.InputTextMessageContent(
                text,
                parse_mode="markdown",
                disable_web_page_preview=False
            ),
            description=subject["name"] if subject["name_cn"] else None,
            thumb_url=subject["image"] if subject["image"] else None,
            reply_markup=telebot.types.InlineKeyboardMarkup().add(*button_list)
        )
        query_result_list.append(qr)
    bot.answer_inline_query(inline_query.id, query_result_list, next_offset=str(offset + 25),
                            switch_pm_text=switch_pm_text, switch_pm_parameter="help", cache_time=3600)


def query_search(inline_query, bot):
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
        subject_list = search_subject(query, response_group="large", start=offset)
        pm_text = "条目搜索"
    if 'list' in subject_list and subject_list["list"] is not None:
        for subject in subject_list["list"]:
            emoji = subject_type_to_emoji(subject["type"])
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
            text += f"\n📚 [简介](https://t.me/iv?url=https://bgm.tv/subject/{subject['id']}&rhash=ce4f44b013e2e8)" \
                    f"\n📖 [详情](https://bgm.tv/subject/{subject['id']})" \
                    f"\n💬 [吐槽箱](https://bgm.tv/subject/{subject['id']}/comments)"
            button_list = [telebot.types.InlineKeyboardButton(
                text="更多信息", switch_inline_query_current_chat=f"S {subject['id']}")]
            if subject["type"] != 3:  # 当类型为anime或real时
                button_list.append(telebot.types.InlineKeyboardButton(
                    text="角色", switch_inline_query_current_chat=f"{subject['id']} 角色"))
            button_list.append(telebot.types.InlineKeyboardButton(
                text='去管理', url=f"t.me/{BOT_USERNAME}?start={subject['id']}"))
            qr = telebot.types.InlineQueryResultArticle(
                id=subject['url'],
                title=emoji + (subject["name_cn"] if subject["name_cn"]
                               else subject["name"]),
                input_message_content=telebot.types.InputTextMessageContent(
                    text,
                    parse_mode="markdownV2",
                    disable_web_page_preview=False
                ),
                description=subject["name"] if subject["name_cn"] else None,
                thumb_url=subject["images"]["medium"] if subject["images"] else None,
                reply_markup=telebot.types.InlineKeyboardMarkup().add(*button_list)
            )
            query_result_list.append(qr)
        pm_text = f"共 {subject_list['results']} 个结果"
    bot.answer_inline_query(inline_query.id, query_result_list, next_offset=str(offset + 25),
                            switch_pm_text=pm_text, switch_pm_parameter="help", cache_time=0)


def query_public_text(inline_query, bot):
    query: str = inline_query.query
    query_param = inline_query.query.split(' ')
    if query.endswith(" 角色"):
        # subject_characters 条目角色
        query_subject_characters(inline_query, bot)
    elif query.startswith("P "):
        if query.endswith(" 关联"):
            # person_related_subjects 人物关联条目
            query_person_related_subjects(inline_query, bot)
        else:
            # mono 人物搜索
            query_mono(inline_query, bot, 'prsn')
    elif query.startswith("C "):
        query_mono(inline_query, bot, 'crt')
    elif query.startswith("S ") and query_param[1].isdecimal():
        # subject_info 条目
        query_subject_info(inline_query, bot)
    elif query.startswith("@"):
        # @ 搜索
        inline_query.query = inline_query.query[1:]
        query_search_sender(inline_query, bot)
    else:
        # search_subject 普通搜索
        query_search(inline_query, bot)
