"""inline 方式私聊搜索或者在任何位置搜索前使用@"""
import telebot

from config import BOT_USERNAME
from plugins.info import gander_info_message
from utils.api import search_subject, get_subject_characters
from utils.converts import subject_type_to_emoji


def query_sender_text(inline_query, bot):
    message_data = inline_query.query.split(' ')
    query_result_list = []
    if len(message_data) != 2:
        if not inline_query.offset:
            offset = 0
            if message_data[0].isdecimal():
                message = gander_info_message("", message_data[0])
                subject_info = message['subject_info']
                qr = telebot.types.InlineQueryResultArticle(
                    id=message_data[0], title=subject_type_to_emoji(subject_info['type']) + (
                        subject_info["name_cn"] if subject_info["name_cn"]
                        else subject_info["name"]
                    ), input_message_content=telebot.types.InputTextMessageContent(
                        message_text=f"/info@{BOT_USERNAME} {message_data[0]}",
                        parse_mode="markdown",
                        disable_web_page_preview=True
                    ), description=subject_info["name"] if subject_info["name_cn"] else None,
                    thumb_url=subject_info["images"]["medium"] if subject_info["images"] else None
                )
                query_result_list.append(qr)
        else:
            offset = int(inline_query.offset)
        query_keyword = message_data[0]
        if str.startswith(query_keyword, '@') and len(query_keyword) > 1:
            query_keyword = query_keyword[1:]
        subject_list = search_subject(
            query_keyword, response_group="large", start=offset)
        if 'list' in subject_list and subject_list["list"] is not None:
            for subject in subject_list["list"]:
                emoji = subject_type_to_emoji(subject["type"])
                qr = telebot.types.InlineQueryResultArticle(
                    id=subject['url'], title=emoji +
                                            (subject["name_cn"] if subject["name_cn"]
                                            else subject["name"]),
                    input_message_content=telebot.types.InputTextMessageContent(
                        message_text=f"/info@{BOT_USERNAME} {subject['id']}",
                        disable_web_page_preview=True
                    ),
                    description=subject["name"] if subject["name_cn"] else None,
                    thumb_url=subject["images"]["medium"] if subject["images"] else None
                )
                query_result_list.append(qr)
        pm_text = f"共 {subject_list['results']} 个结果"
    else:
        offset = 0
        if message_data[0].isdecimal():
            subject_characters = get_subject_characters(message_data[0])
            characters_list = []
            for _character in subject_characters:
                if '角色' == message_data[1]:
                    characters_list = subject_characters
                if '主' in message_data[1]:
                    if _character['relation'] == '主角':
                        characters_list.append(_character)
                if '配' in message_data[1]:
                    if _character['relation'] == '配角':
                        characters_list.append(_character)
            for character in characters_list:
                text = f"*{character['name']}*"
                description = character['relation']
                if len(character['actors']) != 0:
                    description += f" | CV: {[cv['name'] for cv in character['actors']][0]}"
                else:
                    pass
                text += f"\n{description}\n" \
                        f"\n📚 [简介](https://t.me/iv?url=https://bangumi.tv/character/{character['id']}&rhash=48797fd986e111)" \
                        f"\n📖 [详情](https://bgm.tv/character/{character['id']})"
                qr = telebot.types.InlineQueryResultArticle(
                    id=character['id'],
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
            pm_text = f"共 {len(characters_list)} 个结果，可替换输入 主角，配角 对搜索结果分类"
        else:
            pm_text = "请正确输入你需要查询的信息 如：角色，主角，配角"
    bot.answer_inline_query(inline_query.id, query_result_list, next_offset=str(offset + 25),
                            switch_pm_text=pm_text, switch_pm_parameter="help")