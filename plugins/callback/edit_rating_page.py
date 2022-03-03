"""评分页"""
import telebot

from model.page_model import EditRatingPageRequest, BackRequest, DoEditRatingRequest
from utils.api import collection_post, get_subject_info, anime_img


def do(request: DoEditRatingRequest, tg_id: int) -> DoEditRatingRequest:  # 返回在看列表页数
    user_status = request.user_collection.get('status', {}).get('type')
    if user_status is None:
        user_status = 'collect'
    collection_post(tg_id, request.subject_id, user_status, str(request.rating_num))
    if request.rating_num == 0:
        request.callback_text = f"已成功撤销评分"
    else:
        request.callback_text = f"已成功更新评分为{request.rating_num}分"
    return request


def generate_page(request: EditRatingPageRequest, stack_uuid: str) -> EditRatingPageRequest:
    subject_info = get_subject_info(request.subject_id)
    text = (f"*{subject_info['name_cn']}*\n"
            f"{subject_info['name']}\n\n"
            f"*BGM ID：*`{request.subject_id}`\n"
            f"*➤ BGM 平均评分：*`{subject_info['rating']['score']}`🌟\n"
            )
    if request.user_collection['rating'] == 0:
        text += f"*➤ 您的评分：*暂未评分\n"
    else:
        text += f"*➤ 您的评分：*`{request.user_collection['rating']}`🌟\n"
    if request.user_collection is not None:
        epssssss = subject_info["eps"]
        if not epssssss:
            epssssss = subject_info["total_episodes"]
        text += f"*➤ 观看进度：*`{request.user_collection['ep_status']}/{epssssss}`\n"
    text += f"\n💬 [吐槽箱](https://bgm.tv/subject/{request.subject_id}/comments)\n请点按下列数字进行评分"
    markup = telebot.types.InlineKeyboardMarkup()
    nums = range(1, 11)
    button_list = []
    for num in nums:
        button_list.append(telebot.types.InlineKeyboardButton(text=str(num), callback_data=f'{stack_uuid}|{num}'))
        do_edit_rating_request = DoEditRatingRequest(request.subject_id, num)
        do_edit_rating_request.user_collection = request.user_collection
        request.possible_request[str(num)] = do_edit_rating_request
    markup.add(*button_list, row_width=5)
    markup.add(*[telebot.types.InlineKeyboardButton(text='返回', callback_data=f'{stack_uuid}|back'),
                 telebot.types.InlineKeyboardButton(text='删除评分', callback_data=f"{stack_uuid}|0")])
    request.possible_request['back'] = BackRequest()
    do_edit_rating_request = DoEditRatingRequest(request.subject_id, 0)
    do_edit_rating_request.user_collection = request.user_collection
    request.possible_request['0'] = do_edit_rating_request
    if not request.page_image:
        request.page_image = anime_img(request.subject_id)
    request.page_text = text
    request.page_markup = markup
    return request
