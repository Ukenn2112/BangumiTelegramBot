import random

from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineQuery, InlineQueryResultVenue

from utils.api import AnitabiAPI

api = AnitabiAPI()


async def bgmid_anitabi(inline_query: InlineQuery, bgm_id: int):
    offset = int(inline_query.offset or 0)
    query_result_list: list[InlineQueryResultVenue] = []

    anitabi_datas = await api.get_anitabi_data()
    anitabi_data, switch_pm_text = None, "没有找到相关数据"
    for data in anitabi_datas:
        if data["id"] == bgm_id:
            anitabi_data = data
            break
    if anitabi_data:
        switch_pm_text = (anitabi_data["cn"] or anitabi_data["title"]) + " 巡礼地址"
        for point in data["points"][offset : offset + 50]:
            min, sec = 0, 0
            if point.get("s"):
                min, sec = divmod(point["s"], 60)
            if not point.get("ep"):
                point["ep"] = 0
            if min == 0 and sec == 0 and point["ep"] == 0:
                address = f"{anitabi_data['cn'] or anitabi_data['title']} 巡礼地址 @anitabi.cn"
            else:
                address = f"[EP{point['ep']:02d} {min:02d}:{sec:02d}] {anitabi_data['cn'] or anitabi_data['title']} 巡礼地址 @anitabi.cn"
            query_result_list.append(
                InlineQueryResultVenue(
                    id=point.get("id") or str(random.randint(0, 1000000000)),
                    latitude=point["geo"][0],
                    longitude=point["geo"][1],
                    title=point["cn"] if point.get("cn") else point["name"],
                    address=address,
                    thumb_url=("https://anitabi.cn/" + point["image"]) if point.get("image") else None,
                )
            )
    return {
        "results": query_result_list,
        "next_offset": str(offset + 50),
        "switch_pm_text": switch_pm_text,
        "switch_pm_parameter": "help",
        "cache_time": 3600,
    }


async def query_anitabi_text(inline_query: InlineQuery, bot: AsyncTeleBot):
    message_data = inline_query.query.split(" ")
    if len(message_data) < 2:
        return await bot.answer_inline_query(inline_query.id, results=[], switch_pm_text="请输入 BGM ID", switch_pm_parameter="help")
    
    msg_data: str = message_data[1]
    if not msg_data.isdigit():
        return await bot.answer_inline_query(inline_query.id, results=[], switch_pm_text="请输入 BGM ID", switch_pm_parameter="help")

    kwargs = await bgmid_anitabi(inline_query, int(msg_data))
    return await bot.answer_inline_query(inline_query_id=inline_query.id, **kwargs)
