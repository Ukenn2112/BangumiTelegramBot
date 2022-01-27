"""在看详情"""
from utils.api import anime_img, user_collection_get, eps_get, user_data_get
from plugins.info import gander_info_message
from plugins.doing_page import gender_page_message

def callback(call, bot):
    call_tg_id = call.from_user.id
    call_data = call.data.split('|')
    tg_id = int(call_data[1])  # 被请求用户 Telegram ID
    subject_id = call_data[2]  # 剧集ID
    back = int(call_data[3])  # 是否是从其它功能页返回 是则为1 否则为2
    back_page = call_data[4]  # 返回在看列表页数
    if call_tg_id == tg_id:
        img_url = anime_img(subject_id)
        user_collection_data = user_collection_get(tg_id, subject_id)
        eps_data = eps_get(tg_id, subject_id)
        now_do_message = gander_info_message(
            call_tg_id, subject_id, tg_id=tg_id, back_page=back_page,
            user_rating=user_collection_data, eps_data=eps_data)
        if back == 1:
            if call.message.content_type == 'photo':
                bot.edit_message_caption(
                    caption=now_do_message['text'],
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    parse_mode='Markdown',
                    reply_markup=now_do_message['markup'])
            else:
                bot.edit_message_text(
                    text=now_do_message['text'],
                    parse_mode='Markdown',
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=now_do_message['markup'])
        else:
            bot.delete_message(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                timeout=20)  # 删除用户在看动画列表消息
            if img_url == 'None__' or not img_url:  # 是否有动画简介图片
                bot.send_message(
                    chat_id=call.message.chat.id,
                    text=now_do_message['text'],
                    parse_mode='Markdown',
                    reply_markup=now_do_message['markup'],
                    timeout=20)
            else:
                bot.send_photo(
                    chat_id=call.message.chat.id,
                    photo=img_url,
                    caption=now_do_message['text'],
                    parse_mode='Markdown',
                    reply_markup=now_do_message['markup'])
        bot.answer_callback_query(call.id)
    else:
        bot.answer_callback_query(call.id, text='和你没关系，别点了~', show_alert=True)

def callback_page(call, bot):
    """在看详情 翻页"""
    # call_tg_id = call.from_user.id
    msg = call.message
    call_data = call.data.split('|')
    tg_id = int(call_data[1])  # 被查询用户 Telegram ID
    # if str(call_tg_id) != tg_id:
    #     bot.answer_callback_query(call.id, text='和你没关系，别点了~', show_alert=True)
    #     return
    offset = int(call_data[2])  # 当前用户所请求的页数
    subject_type = int(call_data[3]) # 返回再看列表类型
    user_data = user_data_get(tg_id)
    page = gender_page_message(user_data, offset, tg_id, subject_type)
    if call.message.content_type == 'text':
        bot.edit_message_text(text=page['text'],
                              chat_id=msg.chat.id,
                              message_id=msg.message_id,
                              parse_mode='Markdown',
                              reply_markup=page['markup'])
    else:
        bot.delete_message(chat_id=msg.chat.id, message_id=msg.message_id)
        bot.send_message(text=page['text'], chat_id=msg.chat.id, parse_mode='Markdown', reply_markup=page['markup'])
    bot.answer_callback_query(call.id)