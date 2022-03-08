"""inline 方式查询个人统计"""
import json

import telebot

from config import APP_ID
from utils.api import requests_get, get_user, user_data_get


def query_mybgm_text(inline_query, bot):
    message_data = inline_query.query.split(' ')
    query_result_list = []
    if len(message_data) == 1:
        # 未加参数 查询自己
        tg_id = inline_query.from_user.id
        user_data = user_data_get(tg_id)
        if user_data is None:
            # 如果未绑定 直接报错
            bot.answer_inline_query(inline_query.id, query_result_list,
                                    switch_pm_text="您未绑定Bangumi，请点击此条文字进行绑定", switch_pm_parameter="help", cache_time=0)
            return
        bgm_id = user_data.get('user_id')
        access_token = user_data.get('access_token')
    else:
        # 加了参数 查参数中的人
        bgm_id = message_data[1]
        access_token = None
    params = {'app_id': APP_ID}
    url = f'https://api.bgm.tv/user/{bgm_id}/collections/status'
    try:
        startus_data = requests_get(
            url=url, params=params, access_token=access_token)
        if startus_data is None:
            # Fixme 会有这种情况吗？
            bot.answer_inline_query(inline_query.id, query_result_list,
                                    switch_pm_text="出错了，没有获取到您的统计信息", switch_pm_parameter="help", cache_time=0)
            return
        if isinstance(startus_data, dict) and startus_data.get('code') == 404:
            bot.answer_inline_query(inline_query.id, query_result_list,
                                    switch_pm_text="出错了，没有查询到该用户", switch_pm_parameter="help", cache_time=0)
            return
        # 查询用户名
        try:
            user_data = get_user(bgm_id)
        except FileNotFoundError:
            bot.answer_inline_query(inline_query.id, query_result_list,
                                    switch_pm_text="出错了，没有获取到您的统计信息", switch_pm_parameter="help", cache_time=0)
            return
        except json.JSONDecodeError:
            bot.answer_inline_query(inline_query.id, query_result_list,
                                    switch_pm_text="出错了,无法获取到您的个人信息", switch_pm_parameter="help", cache_time=0)
            return
        nickname = user_data.get('nickname')
        bgm_id = user_data.get('id')
        # 开始处理数据
        book_do, book_collect, anime_do, anime_collect, music_do, music_collect, game_do, game_collect \
            = 0, 0, 0, 0, 0, 0, 0, 0
        for i in startus_data:
            if i.get('name') == 'book':
                for book in i.get('collects'):
                    if book.get('status').get('type') == 'do':
                        book_do = book.get('count')
                    if book.get('status').get('type') == 'collect':
                        book_collect = book.get('count')
            elif i.get('name') == 'anime':
                for anime in i.get('collects'):
                    if anime.get('status').get('type') == 'do':
                        anime_do = anime.get('count')
                    if anime.get('status').get('type') == 'collect':
                        anime_collect = anime.get('count')
            elif i.get('name') == 'music':
                for music in i.get('collects'):
                    if music.get('status').get('type') == 'do':
                        music_do = music.get('count')
                    if music.get('status').get('type') == 'collect':
                        music_collect = music.get('count')
            elif i.get('name') == 'game':
                for game in i.get('collects'):
                    if game.get('status').get('type') == 'do':
                        game_do = game.get('count')
                    if game.get('status').get('type') == 'collect':
                        game_collect = game.get('count')
        text = f'*Bangumi 用户数据统计：\n\n{nickname}*\n' \
               f'*➤ 动画：*`{anime_do}在看，{anime_collect}看过`\n' \
               f'*➤ 图书：*`{book_do}在读，{book_collect}读过`\n' \
               f'*➤ 音乐：*`{music_do}在听，{music_collect}听过`\n' \
               f'*➤ 游戏：*`{game_do}在玩，{game_collect}玩过`\n\n' \
               f'[🏠 个人主页](https://bgm.tv/user/{bgm_id})\n'
        img_url = f'https://bgm.tv/chart/img/{bgm_id}'
        qr = telebot.types.InlineQueryResultPhoto(
            id=inline_query.query,
            photo_url=img_url,
            title=f'*{nickname} 的 Bangumi 数据统计*',
            caption=text,
            parse_mode="markdown",
            thumb_url=img_url
        )
        query_result_list.append(qr)
    except:
        bot.answer_inline_query(inline_query.id, query_result_list,
                                switch_pm_text="系统错误，请查看日志", switch_pm_parameter="help", cache_time=0)
        raise
    bot.answer_inline_query(inline_query.id, query_result_list,
                            switch_pm_text="@BGM条目ID获取信息或关键字搜索", switch_pm_parameter="help", cache_time=0)
