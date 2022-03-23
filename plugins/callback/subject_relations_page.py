import telebot

from model.page_model import BackRequest, SubjectRelationsPageRequest, SubjectRequest
from utils.api import get_subject_info, get_subject_relations
from utils.converts import subject_type_to_emoji, full_group_by


def generate_page(request: SubjectRelationsPageRequest) -> SubjectRelationsPageRequest:
    if not request.subject_info:
        request.subject_info = get_subject_info(request.subject_id)
    subject_id = request.subject_id
    relations: list = get_subject_relations(subject_id)
    subject_info = request.subject_info
    button_list = []
    if not relations:
        text = f"*{subject_type_to_emoji(subject_info['type'])}" \
               f"『 {subject_info['name_cn'] or subject_info['name']} 』无关联条目*\n\n"
    else:
        text = f"*{subject_type_to_emoji(subject_info['type'])}" \
               f"『 {subject_info['name_cn'] or subject_info['name']} 』关联条目:*\n\n"

        relation_group = full_group_by(relations, lambda a: a['relation'])
        num: int = 1
        for key in relation_group:
            text += f"*➤ {key}:*\n"
            for relation in relation_group[key]:
                text += f"`{str(num).zfill(2)}`. {subject_type_to_emoji(relation['type'])}" \
                        f"{relation['name_cn'] or relation['name']}\n"
                button_list.append(
                    telebot.types.InlineKeyboardButton(text=str(num), callback_data=f'{request.session.uuid}|{num}'))
                request.possible_request[str(num)] = SubjectRequest(request.session, relation['id'])

                num += 1

    markup = telebot.types.InlineKeyboardMarkup()

    markup.add(*button_list, row_width=6)
    markup.add(telebot.types.InlineKeyboardButton(text='返回', callback_data=f"{request.session.uuid}|back"))
    request.possible_request['back'] = BackRequest(request.session)

    request.page_text = text
    request.page_markup = markup
    return request
