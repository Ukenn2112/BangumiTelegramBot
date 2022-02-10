import telebot

from model.page_model import SubjectRequest, BackRequest, SummaryRequest, EditCollectionTypePageRequest
from utils.api import get_subject_info, anime_img, user_collection_get
from utils.converts import subject_type_to_emoji


def generate_page(subject_request: SubjectRequest, stack_uuid: str) -> SubjectRequest:
    user_collection = None
    if subject_request.user_data:
        user_collection = user_collection_get(None, subject_request.subject_id,
                                              subject_request.user_data['_user']['access_token'])

    if (not subject_request.page_text) or subject_request.user_data:
        subject_request.page_text = gander_page_text(subject_request.subject_id, user_collection)

    if not subject_request.page_image:
        subject_request.page_image = anime_img(subject_request.subject_id)
    if subject_request.user_data:
        subject_request.page_markup = gender_page_manager_button(subject_request, stack_uuid)
    else:
        subject_request.page_markup = gender_page_show_buttons(subject_request, stack_uuid)
    return subject_request


def gender_page_manager_button(subject_request: SubjectRequest, stack_uuid: str):
    markup = telebot.types.InlineKeyboardMarkup()
    button_list = []
    if not subject_request.is_root:
        button_list.append(telebot.types.InlineKeyboardButton(text='返回', callback_data=f"{stack_uuid}|back"))
        subject_request.possible_request['back'] = BackRequest()
    button_list.append(
        telebot.types.InlineKeyboardButton(text='简介', callback_data=f"{stack_uuid}|summary"))
    button_list.append(
        telebot.types.InlineKeyboardButton(text='评分', callback_data=f"{stack_uuid}|rating"))  # TODO
    button_list.append(
        telebot.types.InlineKeyboardButton(text='收藏管理', callback_data=f"{stack_uuid}|collection"))
    subject_request.possible_request['summary'] = SummaryRequest(subject_request.subject_id)
    subject_request.possible_request['summary'].page_image = subject_request.page_image
    subject_request.possible_request['collection'] = EditCollectionTypePageRequest(subject_request.subject_id)
    subject_request.possible_request['collection'].page_image = subject_request.page_image
    markup.add(*button_list)
    return markup


def gender_page_show_buttons(subject_request: SubjectRequest, stack_uuid: str):
    markup = telebot.types.InlineKeyboardMarkup()
    button_list = []
    if not subject_request.is_root:
        button_list.append(telebot.types.InlineKeyboardButton(text='返回', callback_data=f"{stack_uuid}|back"))
        subject_request.possible_request['back'] = BackRequest()
    button_list.append(telebot.types.InlineKeyboardButton(text='简介', callback_data=f"{stack_uuid}|summary"))
    subject_request.possible_request['summary'] = SummaryRequest(subject_request.subject_id)
    subject_request.possible_request['summary'].page_image = subject_request.page_image
    button_list.append(telebot.types.InlineKeyboardButton(text='收藏', callback_data=f"{stack_uuid}|collection"))  # TODO
    subject_request.possible_request['collection'] = EditCollectionTypePageRequest(subject_request.subject_id)
    subject_request.possible_request['collection'].page_image = subject_request.page_image
    markup.add(*button_list)
    return markup


def gander_page_text(subject_id, user_collection=None) -> str:
    """详情页"""
    subject_info = get_subject_info(subject_id)
    subject_type = subject_info['type']
    text = f"{subject_type_to_emoji(subject_type)} *{subject_info['name_cn']}*\n" \
           f"{subject_info['name']}\n\n" \
           f"BGM ID：`{subject_id}`\n"
    if subject_info and 'rating' in subject_info and 'score' in subject_info['rating']:
        text += f"➤ BGM 平均评分：`{subject_info['rating']['score']}`🌟\n"
    else:
        text += f"➤ BGM 平均评分：暂无评分\n"
    if user_collection:  # TODO
        if 'rating' in user_collection:
            if user_collection['rating'] == 0:
                text += f"➤ 您的评分：暂未评分\n"
            else:
                text += f"➤ 您的评分：`{user_collection['rating']}`🌟\n"
    else:
        if subject_type == 2 or subject_type == 6:  # 当类型为anime或real时
            text += f"➤ 集数：共`{subject_info['eps']}`集\n"
    if subject_type == 2 or subject_type == 6:  # 当类型为anime或real时
        if subject_type == 6:
            text += f"➤ 剧集类型：`{subject_info['platform']}`\n"
        else:
            text += f"➤ 放送类型：`{subject_info['platform']}`\n"
        text += f"➤ 放送开始：`{subject_info['date']}`\n"
        if subject_info["_air_weekday"]:
            text += f"➤ 放送星期：`{subject_info['_air_weekday']}`\n"
        # if eps_data is not None:
        #     text += f"➤ 观看进度：`{eps_data['progress']}`\n"
    if subject_type == 1:  # 当类型为book时
        text += f"➤ 书籍类型：`{subject_info['platform']}`\n"
        for box in subject_info['infobox']:
            if box.get('key') == '页数':
                text += f"➤ 页数：共`{box['value']}`页\n"
            if box.get('key') == '作者':
                text += f"➤ 作者：`{box['value']}`\n"
            if box.get('key') == '出版社':
                text += f"➤ 出版社：`{box['value']}`\n"
        text += f"➤ 发售日期：`{subject_info['date']}`\n"
    if subject_type == 3:  # 当类型为Music时
        for box in subject_info['infobox']:
            if box.get('key') == '艺术家':
                text += f"➤ 艺术家：`{box['value']}`\n"
            if box.get('key') == '作曲':
                text += f"➤ 作曲：`{box['value']}`\n"
            if box.get('key') == '作词':
                text += f"➤ 作词：`{box['value']}`\n"
            if box.get('key') == '编曲':
                text += f"➤ 编曲：`{box['value']}`\n"
            if box.get('key') == '厂牌':
                text += f"➤ 厂牌：`{box['value']}`\n"
            if box.get('key') == '碟片数量':
                text += f"➤ 碟片数量：`{box['value']}`\n"
            if box.get('key') == '播放时长':
                text += f"➤ 播放时长：`{box['value']}`\n"
            if box.get('key') == '价格':
                text += f"➤ 价格：`{box['value']}`\n"
        text += f"➤ 发售日期：`{subject_info['date']}`\n"
    if subject_type == 4:  # 当类型为Game时
        for box in subject_info['infobox']:
            if box.get('key') == '游戏类型':
                text += f"➤ 游戏类型：`{box['value']}`\n"
            if box.get('key') == '游玩人数':
                text += f"➤ 游玩人数：`{box['value']}`\n"
            if box.get('key') == '平台':
                if isinstance(box['value'], list):
                    text += f"➤ 平台："
                    for price in box['value']:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"➤ 平台：`{box['value']}`\n"
            if box.get('key') == '发行':
                text += f"➤ 发行：`{box['value']}`\n"
            if box.get('key') == '售价':
                if isinstance(box['value'], list):
                    text += f"➤ 售价："
                    for price in box['value']:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"➤ 售价：`{box['value']}`\n"
        text += f"➤ 发行日期：`{subject_info['date']}`\n"
    if user_collection and user_collection['tag'] and len(user_collection['tag']) == 1 and user_collection['tag'][
        0] == "":
        user_collection['tag'] = []  # 鬼知道为什么没标签会返回个空字符串
    if subject_info['tags'] and len(subject_info['tags']) == 1 and subject_info['tags'][0] == "":
        subject_info['tags'] = []
    if (user_collection and user_collection['tag']) or (subject_info['tags']):
        text += f"➤ 标签："
    if user_collection and user_collection['tag']:
        for tag in user_collection['tag'][:10]:
            text += f"#{'x' if tag.isdecimal() else ''}{tag} "
        if subject_info['tags']:
            tag_not_click = [i for i in subject_info['tags']
                             if i['name'] not in user_collection['tag']]
        else:
            tag_not_click = []
    else:
        tag_not_click = subject_info['tags']
    if tag_not_click and tag_not_click[0]:
        # 如果有列表
        if not (user_collection and user_collection['tag']):
            # 如果没有用户标签
            if tag_not_click and tag_not_click[0]:
                for tag in tag_not_click[:10]:
                    text += f"`{tag['name']}` "
        if user_collection and user_collection['tag'] and len(user_collection['tag']) < 10:
            # 有用户标签 但 用户标签数小于10
            for tag in tag_not_click[:10 - len(user_collection['tag'])]:
                text += f"`{tag['name']}` "
        if (user_collection and user_collection['tag']) or (subject_info['tags']):
            text += "\n"
    text += f"\n📖 [详情](https://bgm.tv/subject/{subject_id})" \
            f"\n💬 [吐槽箱](https://bgm.tv/subject/{subject_id}/comments)"
    return text
