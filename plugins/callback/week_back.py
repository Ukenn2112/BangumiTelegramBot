"""week 页返回"""
import telebot

from model.page_model import WeekPage
from utils.api import get_calendar
from utils.converts import number_to_week


def generate_page(week_page: WeekPage, stack_uuid: str) -> WeekPage:
    week_data = get_calendar()
    if week_data is None:
        raise RuntimeError("出错了")
    for i in week_data:
        if i.get('weekday', {}).get('id') == int(week_page.week_day):
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
                    text=str(num), callback_data=f"search_details|week|{item['id']}|{week_page.week_day}|0"))  # TODO
            text = f'*在{air_weekday}放送的节目*\n\n{week_text_data}' \
                   f'共{count}部'
            markup.add(*button_list, row_width=5)
            week_button_list = []
            for week_day in range(1, 8):
                day_str = number_to_week(week_day)[-1]
                week_page.possible_request[day_str] = WeekPage(week_day)
                week_button_list.append(telebot.types.InlineKeyboardButton(
                    text=day_str,
                    callback_data=f"{stack_uuid}|{day_str}"))
            markup.add(*week_button_list, row_width=7)
            week_page.page_text = text
            week_page.page_markup = markup
    return week_page
    # bot.answer_callback_query(call.id)
