"""评分页"""
import telebot
from utils.api import collection_post, user_collection_get, eps_get, get_subject_info

def callback(call, bot):
    call_tg_id = call.from_user.id
    call_data = call.data.split('|')
    tg_id = int(call_data[1])  # 被请求更新用户 Telegram ID
    if call_tg_id == tg_id:
        rating_data = int(call_data[2])  # 用户请求评分 初始进入评分页为0
        subject_id = call_data[3]  # 剧集ID
        back_page = call_data[4]  # 返回在看列表页数
        eps_data = eps_get(tg_id, subject_id)
        user_collection_data = user_collection_get(tg_id, subject_id)
        user_now_rating = user_collection_data['rating']
        if rating_data != 0:
            user_startus = user_collection_data.get('status', {}).get('type')
            if user_startus is None:
                user_startus = 'collect'
            collection_post(tg_id, subject_id, user_startus, str(rating_data))
            bot.answer_callback_query(call.id, text="已成功更新评分,稍后更新当前页面...")
            user_collection_data = user_collection_get(tg_id, subject_id)
        rating_message = grnder_rating_message(tg_id, subject_id, eps_data, user_collection_data, back_page)
        if rating_data == 0 or user_now_rating != user_collection_data['rating']:  # 当用户当前评分请求与之前评分不一致时
            if call.message.content_type == 'photo':
                bot.edit_message_caption(caption=rating_message['text'],
                                         chat_id=call.message.chat.id,
                                         message_id=call.message.message_id,
                                         parse_mode='Markdown',
                                         reply_markup=rating_message['markup'])
            else:
                bot.edit_message_text(text=rating_message['text'],
                                      parse_mode='Markdown',
                                      chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      reply_markup=rating_message['markup'])
        bot.answer_callback_query(call.id)
    else:
        bot.answer_callback_query(call.id, text='和你没关系，别点了~', show_alert=True)

def grnder_rating_message(tg_id, subject_id, eps_data, user_rating, back_page):
    subject_info = get_subject_info(subject_id)
    text = {f"*{subject_info['name_cn']}*\n"
            f"{subject_info['name']}\n\n"
            f"BGM ID：`{subject_id}`\n\n"
            f"➤ BGM 平均评分：`{subject_info['rating']['score']}`🌟\n"
            f"➤ 您的评分：`{user_rating['rating']}`🌟\n\n"
            f"➤ 观看进度：`{eps_data['progress']}`\n\n"
            f"💬 [吐槽箱](https://bgm.tv/subject/{subject_id}/comments)\n\n"
            f"请点按下列数字进行评分"}
    markup = telebot.types.InlineKeyboardMarkup()
    nums = range(1, 11)
    button_list = []
    for num in nums:
        button_list.append(telebot.types.InlineKeyboardButton(
            text=str(num), callback_data=f'rating|{tg_id}|{num}|{subject_id}|{back_page}'))
    markup.add(*button_list, row_width=5)
    markup.add(telebot.types.InlineKeyboardButton(
        text='返回', callback_data=f'now_do|{tg_id}|{subject_id}|1|{back_page}'))
    return {'text': text, 'markup': markup}