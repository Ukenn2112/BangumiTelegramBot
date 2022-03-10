"""inline 方式公共搜索"""
import telebot

from config import BOT_USERNAME
from plugins.info import gander_info_message
from utils.api import anime_img, search_subject, get_subject_characters
from utils.converts import subject_type_to_emoji, parse_markdown_v2, number_to_week


def query_public_text(inline_query, bot):
    message_data = inline_query.query.split(' ')
    query_result_list = []
    characters_list = []
    if not inline_query.offset:
        offset = 0
        if message_data[0].isdecimal():
            if len(message_data) != 2:
                message = gander_info_message("", message_data[0])
                img_url = anime_img(message_data[0])
                subject_info = message['subject_info']
                if subject_info:
                    if not img_url:
                        qr = telebot.types.InlineQueryResultArticle(
                            id=message_data[0],
                            title=subject_type_to_emoji(subject_info['type']) + (
                                subject_info["name_cn"] if subject_info["name_cn"]
                                else subject_info["name"]),
                            input_message_content=telebot.types.InputTextMessageContent(
                                message['text'],
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
                            id=message_data[0],
                            photo_url=img_url,
                            title=subject_type_to_emoji(subject_info['type']) + (
                                subject_info["name_cn"] if subject_info["name_cn"]
                                else subject_info["name"]),
                            caption=message['text'],
                            parse_mode="markdown",
                            description=subject_info["name"] if subject_info["name_cn"] else None,
                            thumb_url=subject_info["images"]["medium"] if subject_info["images"] else None,
                            reply_markup=telebot.types.InlineKeyboardMarkup().add(
                                telebot.types.InlineKeyboardButton(text='去管理',
                                                                   url=f"t.me/{BOT_USERNAME}?start={subject_info['id']}"))
                        )
                    query_result_list.append(qr)
            else:
                subject_characters = get_subject_characters(message_data[0])
                for _character in subject_characters:
                    if '角色' == message_data[1]:
                        characters_list = subject_characters
                    if '主' in message_data[1]:
                        if _character['relation'] == '主角':
                            characters_list.append(_character)
                    if '配' in message_data[1]:
                        if _character['relation'] == '配角':
                            characters_list.append(_character)
                    if '客' in message_data[1]:
                        if _character['relation'] == '客串':
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
    else:
        offset = int(inline_query.offset)
    subject_list = search_subject(
        message_data[0], response_group="large", start=offset)
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
            button_list = []
            button_list.append(telebot.types.InlineKeyboardButton(
                text="展示详情", switch_inline_query_current_chat=subject['id']))
            if subject["type"] == 2 or subject["type"] == 6:  # 当类型为anime或real时
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
    if len(characters_list) != 0:
        pm_text = f"共 {len(characters_list)} 个结果，可替换输入 主角，配角 对搜索结果分类"
    else:
        pm_text = f"共 {subject_list['results']} 个结果"
    bot.answer_inline_query(inline_query.id, query_result_list, next_offset=str(offset + 25),
                            switch_pm_text=pm_text, switch_pm_parameter="help")
