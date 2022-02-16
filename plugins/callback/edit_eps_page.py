"""已看最新"""
from model.page_model import EditEpsPageRequest
from plugins.info import gander_info_message
from utils.api import collection_post, user_collection_get, eps_get, eps_status_get


def callback(call, bot):
    call_tg_id = call.from_user.id
    call_data = call.data.split('|')
    tg_id = int(call_data[1])  # 被请求更新用户 Telegram ID
    if call_tg_id == tg_id:
        eps_id = int(call_data[2])  # 更新的剧集集数 ID
        if len(call_data) > 5:
            remove = call_data[5]  # 撤销
            if remove == 'remove':
                eps_status_get(tg_id, eps_id, 'remove')  # 更新观看进度为撤销
                bot.send_message(chat_id=call.message.chat.id,
                                 text='已撤销最新观看进度', parse_mode='Markdown', timeout=20)
                bot.answer_callback_query(call.id, text='已撤销最新观看进度')
        else:
            eps_status_get(tg_id, eps_id, 'watched')  # 更新观看进度为看过
            bot.answer_callback_query(call.id, text='已更新观看进度为看过')
        subject_id = int(call_data[3])  # 剧集ID
        back_page = call_data[4]  # 返回在看列表页数
        user_collection_data = user_collection_get(tg_id, subject_id)
        eps_data = eps_get(tg_id, subject_id)
        new_do_message = gander_info_message(call_tg_id, subject_id,
                                             tg_id=tg_id,
                                             user_rating=user_collection_data,
                                             eps_data=eps_data,
                                             eps_id=eps_id,
                                             back_page=back_page)
        if not eps_data['unwatched_id']:
            collection_type = 'collect'
            collection_post(tg_id, subject_id, collection_type,
                            str(user_collection_data['rating']))  # 看完最后一集自动更新收藏状态为看过
        if call.message.content_type == 'photo':
            bot.edit_message_caption(caption=new_do_message['text'],
                                     chat_id=call.message.chat.id,
                                     message_id=call.message.message_id,
                                     parse_mode='Markdown',
                                     reply_markup=new_do_message['markup'])
        else:
            bot.edit_message_text(text=new_do_message['text'],
                                  parse_mode='Markdown',
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=new_do_message['markup'])
    else:
        bot.answer_callback_query(call.id, text='和你没关系，别点了~', show_alert=True)


def generate_page(request: EditEpsPageRequest, stack_uuid: str):
    pass
