"""每日放送查询"""
import telebot
import datetime
from utils.api import get_calendar
from utils.converts import number_to_week


def send(message, bot):
    data = message.text.split(' ')
    if len(data) == 1:
        # 如果未传参数
        now_week = int(datetime.datetime.now().strftime("%w"))
        day = 7 if now_week == 0 else now_week
    else:
        if data[1].isdecimal() and 1 <= int(data[1]) <= 7:
            day = data[1]
        else:
            bot.send_message(message.chat.id, "输入错误 请输入：`/week 1~7`",
                             parse_mode='Markdown', timeout=20)
            return
    msg = bot.send_message(message.chat.id, "正在搜索请稍候...", reply_to_message_id=message.message_id, parse_mode='Markdown',
                           timeout=20)
    week_data = gender_week_message(day)
    bot.edit_message_text(chat_id=message.chat.id, message_id=msg.id, text=week_data['text'], parse_mode='Markdown',
                          reply_markup=week_data['markup'])


def gender_week_message(day):
    """每日放送查询页"""
    week_data = get_calendar()
    if week_data is None:
        return {'text': "出错了!", 'markup': None}
    for i in week_data:
        if i.get('weekday', {}).get('id') == int(day):
            items = i.get('items')
            air_weekday = i.get('weekday', {}).get('cn')
            count = len(items)
            markup = telebot.types.InlineKeyboardMarkup()
            week_text_data = ""
            nums = range(1, count + 1)
            button_list = []
            for item, num in zip(items, nums):
                week_text_data += f'*[{num}]* {item["name_cn"] if item["name_cn"] else item["name"]}\n\n'
                button_list.append(telebot.types.InlineKeyboardButton(
                    text=str(num), callback_data=f"search_details|week|{item['id']}|{day}|0"))
            text = f'*在{air_weekday}放送的节目*\n\n{week_text_data}' \
                   f'共{count}部'
            markup.add(*button_list, row_width=5)
            week_button_list = []
            for week_day in range(1, 8):
                week_button_list.append(telebot.types.InlineKeyboardButton(
                    text=number_to_week(week_day)[-1:],
                    callback_data=f"back_week|{week_day}" if str(week_day) != str(day) else "None"))
            markup.add(*week_button_list, row_width=7)
            return {'text': text, 'markup': markup}
