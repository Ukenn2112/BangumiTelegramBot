"""已看最新"""
import telebot

from model.page_model import EditEpsPageRequest, BackRequest, DoEditEpisodeRequest
from utils.api import post_eps_status
from utils.converts import number_to_episode_type


def generate_page(request: EditEpsPageRequest, stack_uuid: str) -> EditEpsPageRequest:
    episode_id = request.episode_id
    episode_info = request.episode_info
    if not episode_info:
        raise RuntimeWarning("TODO")  # TODO 调用接口查询
    if episode_info['ep'].is_integer():
        ep = str(int(episode_info['ep']))
    else:
        ep = str(episode_info['ep'])
    text = f"{number_to_episode_type(episode_info['type'])}.{ep}\n"
    if episode_info['name_cn']:
        text += f"`{episode_info['name_cn']}\n`"
    if episode_info['name']:
        text += f"`{episode_info['name']}\n`"
    if episode_info['duration']:
        text += f"时长：{episode_info['duration']}\n"
    if episode_info['airdate']:
        text += f"首播日期：{episode_info['airdate']}\n"
    if episode_info['desc']:
        text += f"章节简介：\n{episode_info['desc']}\n"
    text += f"[讨论：{episode_info['comment']}](https://bgm.tv/ep/{episode_id})"
    markup = telebot.types.InlineKeyboardMarkup()
    request.possible_request['back'] = BackRequest()
    if request.access_token:
        button_list = []
        button_list.append(telebot.types.InlineKeyboardButton(text="看过", callback_data=f'{stack_uuid}|watched'))
        request.possible_request['watched'] = DoEditEpisodeRequest(request.episode_id, 'watched', request.access_token)
        button_list.append(telebot.types.InlineKeyboardButton(text="看到", callback_data=f'{stack_uuid}|watched_batch'))
        request.possible_request['watched_batch'] = DoEditEpisodeRequest(request.episode_id, 'watched_batch',
                                                                         request.access_token)
        button_list.append(telebot.types.InlineKeyboardButton(text="想看", callback_data=f'{stack_uuid}|queue'))
        request.possible_request['queue'] = DoEditEpisodeRequest(request.episode_id, 'queue', request.access_token)
        button_list.append(telebot.types.InlineKeyboardButton(text="抛弃", callback_data=f'{stack_uuid}|drop'))
        request.possible_request['drop'] = DoEditEpisodeRequest(request.episode_id, 'drop', request.access_token)
        button_list.append(telebot.types.InlineKeyboardButton(text="撤销", callback_data=f'{stack_uuid}|remove'))
        request.possible_request['remove'] = DoEditEpisodeRequest(request.episode_id, 'remove', request.access_token)
        markup.add(*button_list, row_width=5)

    markup.add(telebot.types.InlineKeyboardButton(text="返回", callback_data=f'{stack_uuid}|back'))
    request.page_markup = markup
    request.page_text = text
    return request


def do(request: DoEditEpisodeRequest, tg_id: int) -> DoEditEpisodeRequest:
    if request.status != 'watched_batch':
        post_eps_status(tg_id, request.episode_id, request.status)
        request.callback_text = '已修改'
    return request
