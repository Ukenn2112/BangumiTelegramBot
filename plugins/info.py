"""根据subjectId 返回对应条目信息"""
import uuid
from typing import Optional

import telebot

from config import BOT_USERNAME
from model.page_model import SubjectRequest, RequestSession
from utils.api import get_subject_info, get_subject_relations
from utils.converts import subject_type_to_emoji


def send(message, bot, subject_id: Optional[int] = None):
    if subject_id is not None:
        subject_id = subject_id
    else:
        message_data = message.text.split(' ')
        if len(message_data) != 2 or not message_data[1].isdecimal():
            bot.send_message(
                chat_id=message.chat.id,
                text="错误使用 `/info BGM_Subject_ID`",
                parse_mode='Markdown',
                timeout=20,
            )
            return
        subject_id = int(message_data[1])  # 剧集ID
    msg = bot.send_message(
        message.chat.id,
        "正在搜索请稍候...",
        reply_to_message_id=message.message_id,
        parse_mode='Markdown',
        timeout=20,
    )

    session = RequestSession(uuid.uuid4().hex, message)
    subject_request = SubjectRequest(session, subject_id, True)
    session.stack = [subject_request]
    session.bot_message = msg
    from bot import consumption_request

    consumption_request(session)


def gander_info_message(
    call_tg_id,
    subject_id,
    tg_id: Optional[int] = None,
    user_rating: Optional[dict] = None,
    eps_data: Optional[dict] = None,
    back_page: Optional[str] = None,
    eps_id: Optional[int] = None,
    back_week_day: Optional[int] = None,
    back_type: Optional[str] = None,
):
    """详情页"""
    subject_info = get_subject_info(subject_id)
    subject_type = subject_info['type']
    text = (
        f"{subject_type_to_emoji(subject_type)} *{subject_info['name_cn']}*\n"
        f"{subject_info['name']}\n\n"
        f"*BGM ID：*`{subject_id}`\n"
    )
    if subject_info and 'rating' in subject_info and 'score' in subject_info['rating']:
        text += f"*➤ BGM 平均评分：*`{subject_info['rating']['score']}`🌟\n"
    else:
        text += f"*➤ BGM 平均评分：*暂无评分\n"
    if user_rating:
        if 'rating' in user_rating:
            if user_rating['rating'] == 0:
                text += f"*➤ 您的评分：*暂未评分\n"
            else:
                text += f"*➤ 您的评分：*`{user_rating['rating']}`🌟\n"
    else:
        if subject_type == 2 or subject_type == 6:  # 当类型为anime或real时
            text += f"*➤ 集数：*共`{subject_info['eps']}`集\n"
    if subject_type == 2 or subject_type == 6:  # 当类型为anime或real时
        if subject_type == 6:
            text += f"*➤ 剧集类型：*`{subject_info['platform']}`\n"
        else:
            text += f"*➤ 放送类型：*`{subject_info['platform']}`\n"
        text += f"*➤ 放送开始：*`{subject_info['date']}`\n"
        if subject_info["_air_weekday"]:
            text += f"*➤ 放送星期：*`{subject_info['_air_weekday']}`\n"
        if eps_data is not None:
            text += f"*➤ 观看进度：*`{eps_data['progress']}`\n"
    if subject_type == 1:  # 当类型为book时
        text += f"*➤ 书籍类型：*`{subject_info['platform']}`\n"
        for box in subject_info['infobox']:
            if box.get('key') == '页数':
                text += f"*➤ 页数：*共`{box['value']}`页\n"
            if box.get('key') == '作者':
                text += f"*➤ 作者：*`{box['value']}`\n"
            if box.get('key') == '出版社':
                if isinstance(box['value'], list):
                    text += f"*➤ 出版社：*"
                    for price in box['value']:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"*➤ 出版社：*`{box['value']}`\n"
        text += f"➤ 发售日期：`{subject_info['date']}`\n"
    if subject_type == 3:  # 当类型为Music时
        for box in subject_info['infobox']:
            if box.get('key') == '艺术家':
                text += f"*➤ 艺术家：*`{box['value']}`\n"
            if box.get('key') == '作曲':
                text += f"*➤ 作曲：*`{box['value']}`\n"
            if box.get('key') == '作词':
                text += f"*➤ 作词：*`{box['value']}`\n"
            if box.get('key') == '编曲':
                text += f"*➤ 编曲：*`{box['value']}`\n"
            if box.get('key') == '厂牌':
                text += f"*➤ 厂牌：*`{box['value']}`\n"
            if box.get('key') == '碟片数量':
                text += f"*➤ 碟片数量：*`{box['value']}`\n"
            if box.get('key') == '播放时长':
                text += f"*➤ 播放时长：*`{box['value']}`\n"
            if box.get('key') == '价格':
                if isinstance(box['value'], list):
                    text += f"*➤ 价格：*"
                    for price in box['value']:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"*➤ 价格：*`{box['value']}`\n"
        text += f"*➤ 发售日期：*`{subject_info['date']}`\n"
    if subject_type == 4:  # 当类型为Game时
        for box in subject_info['infobox']:
            if box.get('key') == '游戏类型':
                text += f"*➤ 游戏类型：*`{box['value']}`\n"
            if box.get('key') == '游玩人数':
                text += f"*➤ 游玩人数：*`{box['value']}`\n"
            if box.get('key') == '平台':
                if isinstance(box['value'], list):
                    text += f"*➤ 平台：*"
                    for price in box['value']:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"*➤ 平台：*`{box['value']}`\n"
            if box.get('key') == '发行':
                text += f"*➤ 发行：*`{box['value']}`\n"
            if box.get('key') == '售价':
                if isinstance(box['value'], list):
                    text += f"*➤ 售价：*"
                    for price in box['value']:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"*➤ 售价：*`{box['value']}`\n"
        text += f"*➤ 发行日期：*`{subject_info['date']}`\n"
    if (
        user_rating
        and user_rating['tag']
        and len(user_rating['tag']) == 1
        and user_rating['tag'][0] == ""
    ):
        user_rating['tag'] = []  # 鬼知道为什么没标签会返回个空字符串
    if subject_info['tags'] and len(subject_info['tags']) == 1 and subject_info['tags'][0] == "":
        subject_info['tags'] = []
    if (user_rating and user_rating['tag']) or (subject_info['tags']):
        text += f"*➤ 标签：*"
    if user_rating and user_rating['tag']:
        for tag in user_rating['tag'][:10]:
            text += f"#{'x' if tag.isdecimal() else ''}{tag} "
        if subject_info['tags']:
            tag_not_click = [
                i for i in subject_info['tags'] if i['name'] not in user_rating['tag']
            ]
        else:
            tag_not_click = []
    else:
        tag_not_click = subject_info['tags']
    if tag_not_click and tag_not_click[0]:
        # 如果有列表
        if not (user_rating and user_rating['tag']):
            # 如果没有用户标签
            if tag_not_click and tag_not_click[0]:
                for tag in tag_not_click[:10]:
                    text += f"`{tag['name']}` "
        if user_rating and user_rating['tag'] and len(user_rating['tag']) < 10:
            # 有用户标签 但 用户标签数小于10
            for tag in tag_not_click[: 10 - len(user_rating['tag'])]:
                text += f"`{tag['name']}` "
        if (user_rating and user_rating['tag']) or (subject_info['tags']):
            text += "\n"
    text += (
        f"\n📖 [详情](https://bgm.tv/subject/{subject_id})"
        f"\n💬 [吐槽箱](https://bgm.tv/subject/{subject_id}/comments)\n"
    )
    subject_relations = get_subject_relations(subject_id)
    if subject_relations != "None__":
        for relation in subject_relations:
            if relation['relation'] == '前传':
                text += f"\n*前传：*[{relation['name_cn'] or relation['name']}](https://t.me/{BOT_USERNAME}?start={relation['id']})"
            if relation['relation'] == '续集':
                text += f"\n*续集：*[{relation['name_cn'] or relation['name']}](https://t.me/{BOT_USERNAME}?start={relation['id']})"
    markup = telebot.types.InlineKeyboardMarkup()
    if eps_data is not None:
        unwatched_id = eps_data['unwatched_id']
        if not unwatched_id:
            markup.add(
                telebot.types.InlineKeyboardButton(
                    text='返回', callback_data=f'do_page|{tg_id}|{back_page}|{subject_type}'
                ),
                telebot.types.InlineKeyboardButton(
                    text='评分', callback_data=f'rating|{tg_id}|0|{subject_id}|{back_page}'
                ),
            )
            if eps_id is not None:
                markup.add(
                    telebot.types.InlineKeyboardButton(
                        text='收藏管理',
                        callback_data=f'collection|{call_tg_id}|{subject_id}|now_do|0|null|{back_page}',
                    ),
                    telebot.types.InlineKeyboardButton(
                        text='撤销最新观看',
                        callback_data=f'letest_eps|{tg_id}|{eps_id}|{subject_id}|{back_page}|remove',
                    ),
                )
            else:
                # markup.add(telebot.types.InlineKeyboardButton(text='批量更新收视进度',
                #                                               callback_data=f'bulk_eps|{subject_id}|'))
                markup.add(
                    telebot.types.InlineKeyboardButton(
                        text='收藏管理',
                        callback_data=f'collection|{call_tg_id}|{subject_id}|now_do|0|null|{back_page}',
                    )
                )
        else:
            markup.add(
                telebot.types.InlineKeyboardButton(
                    text='返回', callback_data=f'do_page|{tg_id}|{back_page}|{subject_type}'
                ),
                telebot.types.InlineKeyboardButton(
                    text='评分', callback_data=f'rating|{tg_id}|0|{subject_id}|{back_page}'
                ),
                telebot.types.InlineKeyboardButton(
                    text='已看最新',
                    callback_data=f'letest_eps|{tg_id}|{unwatched_id[0]}|{subject_id}|{back_page}',
                ),
            )
            if eps_id is not None and eps_data['watched'] != 1:
                markup.add(
                    telebot.types.InlineKeyboardButton(
                        text='收藏管理',
                        callback_data=f'collection|{call_tg_id}|{subject_id}|now_do|0|null|{back_page}',
                    ),
                    telebot.types.InlineKeyboardButton(
                        text='撤销最新观看',
                        callback_data=f'letest_eps|{tg_id}|{eps_id}|{subject_id}|{back_page}|remove',
                    ),
                )
            else:
                # markup.add(telebot.types.InlineKeyboardButton(text='批量更新收视进度',
                #                                               callback_data=f'bulk_eps|{subject_id}'))
                markup.add(
                    telebot.types.InlineKeyboardButton(
                        text='收藏管理',
                        callback_data=f'collection|{call_tg_id}|{subject_id}|now_do|0|null|{back_page}',
                    )
                )
        if eps_id is not None:
            text += f"\n📝 [第{eps_data['watched']}话评论](https://bgm.tv/ep/{eps_id})\n"
    elif back_type is not None:
        if back_type == 'week':
            markup.add(
                telebot.types.InlineKeyboardButton(
                    text='返回', callback_data=f'back_week|{back_week_day}'
                ),
                telebot.types.InlineKeyboardButton(
                    text='简介', callback_data=f'summary|{subject_id}|{back_week_day}'
                ),
                telebot.types.InlineKeyboardButton(
                    text='收藏',
                    callback_data=f'collection|{call_tg_id}|{subject_id}|{back_type}|{back_week_day}|null',
                ),
            )
        else:
            markup.add(
                telebot.types.InlineKeyboardButton(
                    text='收藏',
                    callback_data=f'collection|{call_tg_id}|{subject_id}|{back_type}|0|null',
                ),
                telebot.types.InlineKeyboardButton(
                    text='简介', callback_data=f'summary|{subject_id}'
                ),
            )
    return {'text': text, 'markup': markup, 'subject_info': subject_info}
