"""week 页返回"""
from plugins.week import gender_week_message


def callback(call, bot):
    day = int(call.data.split('|')[1])  # week day
    week_data = gender_week_message(day)
    if call.message.content_type != 'text':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id, timeout=20)
        bot.send_message(chat_id=call.message.chat.id,
                         text=week_data['text'],
                         parse_mode='Markdown',
                         reply_markup=week_data['markup'],
                         timeout=20)
    else:
        bot.edit_message_text(text=week_data['text'], parse_mode='Markdown', reply_markup=week_data['markup'],
                              chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)
