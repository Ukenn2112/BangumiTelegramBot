"""inline 方式公共搜索"""
import telebot
from utils.api import anime_img, search_subject
from utils.converts import subject_type_to_emoji, parse_markdown_v2, number_to_week
from plugins.info import gander_info_message


def query_public_text(inline_query, bot):
    query_result_list = []
    if not inline_query.offset:
        offset = 0
        if inline_query.query.isdecimal():
            message = gander_info_message("", inline_query.query)
            img_url = anime_img(inline_query.query)
            subject_info = message['subject_info']
            if subject_info:
                if img_url == 'None__' or not img_url:
                    qr = telebot.types.InlineQueryResultArticle(
                        id=inline_query.query,
                        title=subject_type_to_emoji(subject_info['type']) + (
                            subject_info["name_cn"] if subject_info["name_cn"]
                            else subject_info["name"]),
                        input_message_content=telebot.types.InputTextMessageContent(
                            message['text'],
                            parse_mode="markdown",
                            disable_web_page_preview=True
                        ),
                        description=subject_info["name"] if subject_info["name_cn"] else None,
                        thumb_url=subject_info["images"]["medium"] if subject_info["images"] else None
                    )
                else:
                    qr = telebot.types.InlineQueryResultPhoto(
                        id=inline_query.query,
                        photo_url=img_url,
                        title=subject_type_to_emoji(subject_info['type']) + (
                            subject_info["name_cn"] if subject_info["name_cn"]
                            else subject_info["name"]),
                        caption=message['text'],
                        parse_mode="markdown",
                        description=subject_info["name"] if subject_info["name_cn"] else None,
                        thumb_url=subject_info["images"]["medium"] if subject_info["images"] else None
                    )
                query_result_list.append(qr)
    else:
        offset = int(inline_query.offset)
    subject_list = search_subject(
        inline_query.query, response_group="large", start=offset)
    if 'list' in subject_list and subject_list["list"] is not None:
        for subject in subject_list["list"]:
            emoji = subject_type_to_emoji(subject["type"])
            text = f"搜索结果{emoji}:\n*{parse_markdown_v2(subject['name'])}*\n"
            if subject['name_cn']:
                text += f"{parse_markdown_v2(subject['name_cn'])}\n"
            text += "\n"
            text += f"BGM ID：`{subject['id']}`\n"
            if 'rating' in subject and subject['rating']['score']:
                text += f"➤ BGM 平均评分：`{subject['rating']['score']}`🌟\n"
            if subject["type"] == 2 or subject["type"] == 6:  # 当类型为anime或real时
                if 'eps' in subject and subject['eps']:
                    text += f"➤ 集数：共`{subject['eps']}`集\n"
                if subject['air_date']:
                    text += f"➤ 放送日期：`{parse_markdown_v2(subject['air_date'])}`\n"
                if subject['air_weekday']:
                    text += f"➤ 放送星期：`{number_to_week(subject['air_weekday'])}`\n"
            if subject["type"] == 1:  # 当类型为book时
                if 'eps' in subject and subject['eps']:
                    text += f"➤ 话数：共`{subject['eps']}`话\n"
                if subject['air_date']:
                    text += f"➤ 发售日期：`{parse_markdown_v2(subject['air_date'])}`\n"
            if subject["type"] == 3:  # 当类型为music时
                if subject['air_date']:
                    text += f"➤ 发售日期：`{parse_markdown_v2(subject['air_date'])}`\n"
            if subject["type"] == 4:  # 当类型为game时
                if subject['air_date']:
                    text += f"➤ 发行日期：`{parse_markdown_v2(subject['air_date'])}`\n"
            text += f"\n📖 [详情](https://bgm.tv/subject/{subject['id']})" \
                    f"\n💬 [吐槽箱](https://bgm.tv/subject/{subject['id']}/comments)"
            # if 'collection' in subject and subject['collection']:
            #     text += f"➤ BGM 统计:\n"
            #     if 'wish' in subject['collection']:
            #         text += f"想:{subject['collection']['wish']} "
            #     if 'collect' in subject['collection']:
            #         text += f"完:{subject['collection']['collect']} "
            #     if 'doing' in subject['collection']:
            #         text += f"在:{subject['collection']['doing']} "
            #     if 'on_hold' in subject['collection']:
            #         text += f"搁:{subject['collection']['on_hold']} "
            #     if 'dropped' in subject['collection']:
            #         text += f"抛:{subject['collection']['dropped']} "
            #   text += "\n"
            # if subject['summary']:
            #     text += f"||_{utils.parse_markdown_v2(subject['summary'])}_||\n"
            qr = telebot.types.InlineQueryResultArticle(
                id=subject['url'],
                title=emoji +
                (subject["name_cn"] if subject["name_cn"]
                 else subject["name"]),
                input_message_content=telebot.types.InputTextMessageContent(
                    text,
                    parse_mode="markdownV2",
                    disable_web_page_preview=True
                ),
                description=subject["name"] if subject["name_cn"] else None,
                thumb_url=subject["images"]["medium"] if subject["images"] else None,
                reply_markup=telebot.types.InlineKeyboardMarkup().add(telebot.types.InlineKeyboardButton(
                    text="展示详情",
                    switch_inline_query_current_chat=subject['id']
                ))
            )
            query_result_list.append(qr)
    bot.answer_inline_query(inline_query.id, query_result_list, next_offset=str(offset + 25),
                            switch_pm_text="@BGM条目ID获取信息或关键字搜索", switch_pm_parameter="None")
