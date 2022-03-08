"""inline 方式私聊搜索或者在任何位置搜索前使用@"""
import telebot

from config import BOT_USERNAME
from plugins.info import gander_info_message
from utils.api import search_subject
from utils.converts import subject_type_to_emoji


def query_sender_text(inline_query, bot):
    query_result_list = []
    if not inline_query.offset:
        offset = 0
        if inline_query.query.isdecimal():
            message = gander_info_message("", inline_query.query)
            subject_info = message['subject_info']
            qr = telebot.types.InlineQueryResultArticle(
                id=inline_query.query, title=subject_type_to_emoji(subject_info['type']) + (
                    subject_info["name_cn"] if subject_info["name_cn"]
                    else subject_info["name"]
                ), input_message_content=telebot.types.InputTextMessageContent(
                    message_text=f"/info@{BOT_USERNAME} {inline_query.query}",
                    parse_mode="markdown",
                    disable_web_page_preview=True
                ), description=subject_info["name"] if subject_info["name_cn"] else None,
                thumb_url=subject_info["images"]["medium"] if subject_info["images"] else None
            )
            query_result_list.append(qr)
    else:
        offset = int(inline_query.offset)
    query_keyword = inline_query.query
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
    bot.answer_inline_query(inline_query.id, query_result_list, next_offset=str(offset + 25),
                            switch_pm_text="@BGM条目ID获取信息或关键字搜索", switch_pm_parameter="help")
