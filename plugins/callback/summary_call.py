"""简介页"""
from plugins.summary import grnder_summary_message

def callback(call, bot):
    call_data = call.data.split('|')
    subject_id = call_data[1]  # subject_id
    if len(call_data) > 2:
        week_day = call_data[2]
    else:
        week_day = 0
    summary_data = grnder_summary_message(subject_id, week_day)
    if call.message.content_type == 'photo':
        bot.edit_message_caption(caption=summary_data['text'], chat_id=call.message.chat.id,
                                    message_id=call.message.message_id,
                                    parse_mode='Markdown',
                                    reply_markup=summary_data['markup'])
    else:
        bot.edit_message_text(text=summary_data['text'],
                                parse_mode='Markdown',
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=summary_data['markup'])
    bot.answer_callback_query(call.id)