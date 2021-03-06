import telebot

from config import BOT_USERNAME
from model.page_model import (
    SubjectRequest,
    BackRequest,
    SummaryRequest,
    EditCollectionTypePageRequest,
    EditRatingPageRequest,
    SubjectEpsPageRequest,
    SubjectRelationsPageRequest,
)
from utils.api import get_subject_info, anime_img, user_collection_get
from utils.converts import subject_type_to_emoji, score_to_str


def generate_page(subject_request: SubjectRequest) -> SubjectRequest:
    user_collection = None
    if (not subject_request.page_text) and (not subject_request.page_markup):
        if subject_request.session.bot_message.chat.type == "private":
            if (
                subject_request.session.bgm_auth
                and 'access_token' in subject_request.session.bgm_auth
            ):
                user_collection = user_collection_get(
                    None,
                    subject_request.subject_id,
                    subject_request.session.bgm_auth['access_token'],
                )

    if not subject_request.page_text and not subject_request.page_image:
        subject_info = get_subject_info(subject_request.subject_id)
        if not subject_request.page_text:
            subject_request.page_text = gander_page_text(
                subject_request.subject_id, user_collection, subject_info
            )

        if not subject_request.page_image:
            subject_request.page_image = anime_img(subject_request.subject_id)

    if not subject_request.page_markup:
        if subject_request.session.bot_message.chat.type == "private":
            subject_request.page_markup = gender_page_manager_button(
                subject_request, user_collection
            )
        else:
            subject_request.page_markup = gender_page_show_buttons(subject_request)
    return subject_request


def gender_page_manager_button(subject_request: SubjectRequest, user_collection):
    session_uuid = subject_request.session.uuid
    markup = telebot.types.InlineKeyboardMarkup()
    button_list = [[], []]
    if not subject_request.is_root:
        button_list[1].append(
            telebot.types.InlineKeyboardButton(text='??????', callback_data=f"{session_uuid}|back")
        )
        subject_request.possible_request['back'] = BackRequest(subject_request.session)
    button_list[0].append(
        telebot.types.InlineKeyboardButton(text='??????', callback_data=f"{session_uuid}|summary")
    )
    button_list[0].append(
        telebot.types.InlineKeyboardButton(text='??????', callback_data=f"{session_uuid}|relations")
    )
    if user_collection:
        if 'status' in user_collection:
            button_list[1].append(
                telebot.types.InlineKeyboardButton(
                    text='??????', callback_data=f"{session_uuid}|rating"
                )
            )
            edit_rating_page_request = EditRatingPageRequest(
                subject_request.session, subject_request.subject_id
            )
            edit_rating_page_request.page_image = subject_request.page_image
            edit_rating_page_request.user_collection = user_collection
            subject_request.possible_request['rating'] = edit_rating_page_request

            button_list[0].append(
                telebot.types.InlineKeyboardButton(text='?????????', callback_data=f"{session_uuid}|eps")
            )
        else:
            button_list[0].append(
                telebot.types.InlineKeyboardButton(text='??????', callback_data=f"{session_uuid}|eps")
            )
        subject_eps_page_request = SubjectEpsPageRequest(
            subject_request.session, subject_id=subject_request.subject_id, limit=12, type_=0
        )
        subject_eps_page_request.user_collection = user_collection
        subject_request.possible_request['eps'] = subject_eps_page_request
        button_list[1].append(
            telebot.types.InlineKeyboardButton(
                text='????????????', callback_data=f"{session_uuid}|collection"
            )
        )
        edit_collection_type_page_request = EditCollectionTypePageRequest(
            subject_request.session, subject_request.subject_id
        )
        subject_request.possible_request['collection'] = edit_collection_type_page_request
        edit_collection_type_page_request.page_image = subject_request.page_image
    else:
        subject_eps_page_request = SubjectEpsPageRequest(
            subject_request.session, subject_id=subject_request.subject_id, limit=12, type_=0
        )
        subject_eps_page_request.user_collection = user_collection
        subject_request.possible_request['eps'] = subject_eps_page_request
        button_list[0].append(
            telebot.types.InlineKeyboardButton(text='??????', callback_data=f"{session_uuid}|eps")
        )
    subject_request.possible_request['summary'] = SummaryRequest(
        subject_request.session, subject_request.subject_id
    )
    subject_request.possible_request['summary'].page_image = subject_request.page_image
    relations_request = SubjectRelationsPageRequest(
        subject_request.session, subject_id=subject_request.subject_id
    )
    subject_request.possible_request['relations'] = relations_request

    for i in button_list:
        if i:
            markup.add(*i)
    return markup


def gender_page_show_buttons(subject_request: SubjectRequest):
    session_uuid = subject_request.session.uuid
    markup = telebot.types.InlineKeyboardMarkup()
    button_list = [[], []]
    if not subject_request.is_root:
        button_list[1].append(
            telebot.types.InlineKeyboardButton(text='??????', callback_data=f"{session_uuid}|back")
        )
        subject_request.possible_request['back'] = BackRequest(subject_request.session)
    button_list[1].append(
        telebot.types.InlineKeyboardButton(
            text='?????????', url=f"t.me/{BOT_USERNAME}?start={subject_request.subject_id}"
        )
    )  # TODO
    button_list[0].append(
        telebot.types.InlineKeyboardButton(text='??????', callback_data=f"{session_uuid}|summary")
    )
    button_list[0].append(
        telebot.types.InlineKeyboardButton(text='??????', callback_data=f"{session_uuid}|eps")
    )
    button_list[0].append(
        telebot.types.InlineKeyboardButton(text='??????', callback_data=f"{session_uuid}|relations")
    )
    subject_eps_page_request = SubjectEpsPageRequest(
        subject_request.session, subject_id=subject_request.subject_id, limit=12, type_=0
    )
    subject_eps_page_request.user_collection = {'code'}
    subject_request.possible_request['eps'] = subject_eps_page_request
    subject_request.possible_request['summary'] = SummaryRequest(
        subject_request.session, subject_request.subject_id
    )
    subject_request.possible_request['summary'].page_image = subject_request.page_image
    relations_request = SubjectRelationsPageRequest(
        subject_request.session, subject_id=subject_request.subject_id
    )
    subject_request.possible_request['relations'] = relations_request
    subject_request.possible_request['collection'] = EditCollectionTypePageRequest(
        subject_request.session, subject_request.subject_id
    )
    subject_request.possible_request['collection'].page_image = subject_request.page_image

    for i in button_list:
        if i:
            markup.add(*i, row_width=4)
    return markup


def gander_page_text(subject_id, user_collection=None, subject_info=None) -> str:
    """?????????"""
    if not subject_info:
        subject_info = get_subject_info(subject_id)
    subject_type = subject_info['type']
    text = (
        f"{subject_type_to_emoji(subject_type)} *{subject_info['name_cn']}*\n"
        f"{subject_info['name']}\n\n"
    )
    if user_collection and 'status' in user_collection:
        text += f"*BGM ID???*`{subject_id}` | {user_collection['status']['name']}"
    else:
        text += f"*BGM ID???*`{subject_id}`"
    if subject_info['nsfw']:
        text += " ????"
    text += "\n"
    if subject_info and 'rating' in subject_info and 'score' in subject_info['rating']:
        text += (
            f"*??? BGM ???????????????*`{subject_info['rating']['score']}`???? "
            f"{score_to_str(subject_info['rating']['score'])}\n"
        )
    else:
        text += "*??? BGM ???????????????*????????????\n"
    epssssss = subject_info["eps"]
    if not epssssss:
        epssssss = subject_info["total_episodes"]
    if user_collection:
        if 'rating' in user_collection:
            if user_collection['rating'] == 0:
                text += "*??? ???????????????*????????????\n"
            else:
                text += f"*??? ???????????????*`{user_collection['rating']}`????\n"
    else:
        if subject_type == 2 or subject_type == 6:  # ????????????anime???real???
            text += f"*??? ?????????*???`{epssssss}`???\n"
    if subject_type == 2 or subject_type == 6:  # ????????????anime???real???
        if subject_type == 6:
            text += f"*??? ???????????????*`{subject_info['platform']}`\n"
        else:
            text += f"*??? ???????????????*`{subject_info['platform']}`\n"
        text += f"*??? ???????????????*`{subject_info['date']}`\n"
        if subject_info["_air_weekday"]:
            text += f"*??? ???????????????*`{subject_info['_air_weekday']}`\n"
        if user_collection and 'ep_status' in user_collection:
            text += f"*??? ???????????????*`{user_collection['ep_status']}/{epssssss}`\n"
    if subject_type == 1:  # ????????????book???
        text += f"*??? ???????????????*`{subject_info['platform']}`\n"
        for box in subject_info['infobox']:
            if box.get('key') == '??????':
                text += f"*??? ?????????*???`{box['value']}`???\n"
            if box.get('key') == '??????':
                text += f"*??? ?????????*`{box['value']}`\n"
            if box.get('key') == '?????????':
                if isinstance(box['value'], list):
                    text += "*??? ????????????*"
                    for price in box['value']:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"*??? ????????????*`{box['value']}`\n"
        text += f"*??? ???????????????*`{subject_info['date']}`\n"
    if subject_type == 3:  # ????????????Music???
        for box in subject_info['infobox']:
            if box.get('key') == '?????????':
                text += f"*??? ????????????*`{box['value']}`\n"
            if box.get('key') == '??????':
                text += f"*??? ?????????*`{box['value']}`\n"
            if box.get('key') == '??????':
                text += f"*??? ?????????*`{box['value']}`\n"
            if box.get('key') == '??????':
                text += f"*??? ?????????*`{box['value']}`\n"
            if box.get('key') == '??????':
                text += f"*??? ?????????*`{box['value']}`\n"
            if box.get('key') == '????????????':
                text += f"*??? ???????????????*`{box['value']}`\n"
            if box.get('key') == '????????????':
                text += f"*??? ???????????????*`{box['value']}`\n"
            if box.get('key') == '??????':
                if isinstance(box['value'], list):
                    text += "*??? ?????????*"
                    for price in box['value']:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"*??? ?????????*`{box['value']}`\n"
        text += f"*??? ???????????????*`{subject_info['date']}`\n"
    if subject_type == 4:  # ????????????Game???
        for box in subject_info['infobox']:
            if box.get('key') == '????????????':
                text += f"*??? ???????????????*`{box['value']}`\n"
            if box.get('key') == '????????????':
                text += f"*??? ???????????????*`{box['value']}`\n"
            if box.get('key') == '??????':
                if isinstance(box['value'], list):
                    text += "*??? ?????????*"
                    for price in box['value']:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"*??? ?????????*`{box['value']}`\n"
            if box.get('key') == '??????':
                text += "*??? ?????????*`{box['value']}`\n"
            if box.get('key') == '??????':
                if isinstance(box['value'], list):
                    text += "*??? ?????????*"
                    for price in box['value']:
                        text += f" `{price['v']}`"
                    text += "\n"
                else:
                    text += f"*??? ?????????*`{box['value']}`\n"
        text += f"*??? ???????????????*`{subject_info['date']}`\n"
    if (
        user_collection
        and 'tag' in user_collection
        and user_collection['tag']
        and len(user_collection['tag']) == 1
        and user_collection['tag'][0] == ""
    ):
        user_collection['tag'] = []  # ???????????????????????????????????????????????????
    if subject_info['tags'] and len(subject_info['tags']) == 1 and subject_info['tags'][0] == "":
        subject_info['tags'] = []
    if (user_collection and 'tag' in user_collection and user_collection['tag']) or (
        subject_info['tags']
    ):
        text += "*??? ?????????*"
    if user_collection and 'tag' in user_collection and user_collection['tag']:
        for tag in user_collection['tag'][:10]:
            text += f"#{'x' if tag.isdecimal() else ''}{tag} "
        if subject_info['tags']:
            tag_not_click = [
                i for i in subject_info['tags'] if i['name'] not in user_collection['tag']
            ]
        else:
            tag_not_click = []
    else:
        tag_not_click = subject_info['tags']
    if tag_not_click and tag_not_click[0]:
        # ???????????????
        if not (user_collection and 'tag' in user_collection and user_collection['tag']):
            # ????????????????????????
            if tag_not_click and tag_not_click[0]:
                for tag in tag_not_click[:10]:
                    text += f"`{tag['name']}` "
        if (
            user_collection
            and 'tag' in user_collection
            and user_collection['tag']
            and len(user_collection['tag']) < 10
        ):
            # ??????????????? ??? ?????????????????????10
            for tag in tag_not_click[: 10 - len(user_collection['tag'])]:
                text += f"`{tag['name']}` "
        if (user_collection and 'tag' in user_collection and user_collection['tag']) or (
            subject_info['tags']
        ):
            text += "\n"
    text += (
        f"\n???? [??????](https://bgm.tv/subject/{subject_id})"
        f"\n???? [?????????](https://bgm.tv/subject/{subject_id}/comments)\n"
    )
    return text
