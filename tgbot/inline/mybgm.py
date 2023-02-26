from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineQuery, InlineQueryResultPhoto

from utils.config_vars import bgm
from utils.user_token import bgm_user_data


async def send_mybgm(bgm_id: str, nickname: str):
    query_result_list: list[InlineQueryResultPhoto] = []

    status_data = await bgm.get_user_collections_status(bgm_id)
    if not status_data:
        return {
            "results": query_result_list,
            "switch_pm_text": "未找到您的收藏数据",
            "switch_pm_parameter": "start",
            "cache_time": 0,
        }

    book_do, book_collect, anime_do, anime_collect, music_do, music_collect, game_do, game_collect, real_do, real_collect = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    for i in status_data:
        if i.get("name") == "book":
            for book in i.get("collects"):
                if book.get("status").get("type") == "do":
                    book_do = book.get("count")
                if book.get("status").get("type") == "collect":
                    book_collect = book.get("count")
        elif i.get("name") == "anime":
            for anime in i.get("collects"):
                if anime.get("status").get("type") == "do":
                    anime_do = anime.get("count")
                if anime.get("status").get("type") == "collect":
                    anime_collect = anime.get("count")
        elif i.get("name") == "music":
            for music in i.get("collects"):
                if music.get("status").get("type") == "do":
                    music_do = music.get("count")
                if music.get("status").get("type") == "collect":
                    music_collect = music.get("count")
        elif i.get("name") == "game":
            for game in i.get("collects"):
                if game.get("status").get("type") == "do":
                    game_do = game.get("count")
                if game.get("status").get("type") == "collect":
                    game_collect = game.get("count")
        elif i.get("name") == "real":
            for real in i.get("collects"):
                if real.get("status").get("type") == "do":
                    real_do = real.get("count")
                if real.get("status").get("type") == "collect":
                    real_collect = real.get("count")
    text = (
        f"*Bangumi 用户数据统计：\n\n{nickname}*\n"
        f"*➤ 动画：*`{anime_do}在看，{anime_collect}看过`\n"
        f"*➤ 图书：*`{book_do}在读，{book_collect}读过`\n"
        f"*➤ 音乐：*`{music_do}在听，{music_collect}听过`\n"
        f"*➤ 游戏：*`{game_do}在玩，{game_collect}玩过`\n"
        f"*➤ 三次元：*`{real_do}在看，{real_collect}看过`\n"
        f"[🏠 个人主页](https://bgm.tv/user/{bgm_id})\n"
    ) 
    qr = InlineQueryResultPhoto(
        id=bgm_id,
        photo_url=f"https://bgm.tv/chart/img/{bgm_id}",
        title=f"*{nickname} 的 Bangumi 数据统计*",
        caption=text,
        parse_mode="markdown",
        thumb_url=f"https://bgm.tv/chart/img/{bgm_id}",
    )
    query_result_list.append(qr)
    return {
        "results": query_result_list,
        "switch_pm_text": f"{nickname} 的 Bangumi 数据统计",
        "switch_pm_parameter": "start",
        "cache_time": 0,
    }


async def query_mybgm_text(inline_query: InlineQuery, bot: AsyncTeleBot):
    message_data = inline_query.query.split(" ")
    if len(message_data) == 1:
        user_bgm_data = await bgm_user_data(inline_query.from_user.id)
        if user_bgm_data is None:
            return await bot.answer_inline_query(
                inline_query.id,
                [], switch_pm_text="您未绑定Bangumi，请点击此条文字进行绑定",
                switch_pm_parameter="start",
                cache_time=0,
            )
        kwargs = await send_mybgm(user_bgm_data["bgmId"], user_bgm_data["userData"]["nickname"])
    else:
        message_data = inline_query.query[6:]
        user_bgm_data = await bgm.get_user_info(message_data)
        if user_bgm_data.get("error"):
            return await bot.answer_inline_query(
                inline_query.id,
                [], switch_pm_text="未找到该用户",
                switch_pm_parameter="start",
                cache_time=0,
            )
        kwargs = await send_mybgm(user_bgm_data["id"], user_bgm_data["nickname"])

    return await bot.answer_inline_query(inline_query_id=inline_query.id, **kwargs)