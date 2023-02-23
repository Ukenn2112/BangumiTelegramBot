"""week 页返回"""
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.config_vars import bgm
from utils.converts import number_to_week

from ..model.page_model import SubjectRequest, WeekRequest


async def generate_page(request: WeekRequest) -> WeekRequest:
    session_uuid = request.session.uuid
    week_data = await bgm.get_calendar()
    if week_data is None: raise RuntimeError("出错了")
    for i in week_data:
        if i.get("weekday", {}).get("id") == int(request.week_day):
            items = i.get("items")
            air_weekday = i.get("weekday", {}).get("cn")
            count = len(items)
            markup = InlineKeyboardMarkup()
            week_text_data = ""
            nums = range(1, count + 1)
            button_list = []
            for item, num in zip(items, nums):
                week_text_data += (
                    f"*[{num}]* {item['name_cn'] or item['name']}\n\n"
                )
                request.possible_request[str(item["id"])] = SubjectRequest(
                    request.session, item["id"]
                )
                button_list.append(
                    InlineKeyboardButton(
                        text=str(num), callback_data=f"{session_uuid}|{item['id']}"
                    )
                )
            text = f"*在{air_weekday}放送的节目*\n\n{week_text_data}" f"共{count}部"
            markup.add(*button_list, row_width=5)
            week_button_list = []
            for week_day in range(1, 8):
                if week_day != int(request.week_day):
                    day_str = number_to_week(week_day)[-1]
                    request.possible_request[day_str] = WeekRequest(
                        request.session, week_day=week_day
                    )
                    week_button_list.append(
                        InlineKeyboardButton(text=day_str, callback_data=f"{session_uuid}|{day_str}")
                    )
            markup.add(*week_button_list, row_width=6)
            request.page_text = text
            request.page_markup = markup
    return request
