#!/usr/bin/python
'''
https://bangumi.github.io/api/
'''

import json
import telebot
import requests
import datetime

from config import BOT_TOKEN, APP_ID, APP_SECRET, WEBSITE_BASE, BOT_USERNAME

# 请求TG Bot api
bot = telebot.TeleBot(BOT_TOKEN)

# 绑定 Bangumi
@bot.message_handler(commands=['start'])
def send_start(message):
    if message.chat.type == "private": # 当私人聊天
        test_id = message.from_user.id
        if data_seek_get(test_id) == 'yes':
            bot.send_message(message.chat.id, "已绑定", timeout=20)
        else:
            text = {'请绑定您的Bangumi'}
            url= f'{WEBSITE_BASE}oauth_index?tg_id={test_id}'
            markup = telebot.types.InlineKeyboardMarkup()    
            markup.add(telebot.types.InlineKeyboardButton(text='绑定Bangumi',url=url))
            bot.send_message(message.chat.id, text=text, parse_mode='Markdown', reply_markup=markup ,timeout=20)
    else:
        if message.text == f'/start@{BOT_USERNAME}':
            bot.send_message(message.chat.id, '请私聊我进行Bangumi绑定', parse_mode='Markdown' ,timeout=20)
        else:
            pass

# 查询 Bangumi 用户收藏统计
@bot.message_handler(commands=['my'])
def send_my(message):
    message_data = message.text.split(' ')
    test_id = message.from_user.id
    if len(message_data) == 1:
        if data_seek_get(test_id) == 'no':
            bot.send_message(message.chat.id, "未绑定Bangumi，请私聊使用[/start](https://t.me/"+BOT_USERNAME+"?start=none)进行绑定", parse_mode='Markdown', timeout=20)
        else:
            msg = bot.send_message(message.chat.id, "正在查询请稍后...", reply_to_message_id=message.message_id, parse_mode='Markdown', timeout=20)
            access_token = user_data_get(test_id).get('access_token')
            params = {'app_id': APP_ID}
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
                'Authorization': 'Bearer ' + access_token}

            url = 'https://api.bgm.tv/user/' + str(user_data_get(test_id).get('user_id')) + '/collections/status'
            r = requests.get(url=url, params=params, headers=headers)
            startus_data = json.loads(r.text)
            if startus_data == None:
                bot.delete_message(message.chat.id, message_id=msg.message_id, timeout=20)
                bot.send_message(message.chat.id, text='您没有观看记录，快去bgm上点几个格子吧~', parse_mode='Markdown', timeout=20)
            else:
                book = None
                book_do = 0
                book_collect = 0
                for i in startus_data:
                    if i.get('name') == 'book':
                        book = i.get('collects')
                        for i in book:
                            if i.get('status').get('type') == 'do':
                                book_do = i.get('count')
                            if i.get('status').get('type') == 'collect':
                                book_collect = i.get('count')
                anime = None
                anime_do = 0
                anime_collect = 0
                for i in startus_data:
                    if i.get('name') == 'anime':
                        anime = i.get('collects')
                        for i in anime:
                            if i.get('status').get('type') == 'do':
                                anime_do = i.get('count')
                            if i.get('status').get('type') == 'collect':
                                anime_collect = i.get('count')
                music = None
                music_do = 0
                music_collect = 0
                for i in startus_data:
                    if i.get('name') == 'music':
                        music = i.get('collects')
                        for i in music:
                            if i.get('status').get('type') == 'do':
                                music_do = i.get('count')
                            if i.get('status').get('type') == 'collect':
                                music_collect = i.get('count')
                game = None
                game_do = 0
                game_collect = 0
                for i in startus_data:
                    if i.get('name') == 'game':
                        game = i.get('collects')
                        for i in game:
                            if i.get('status').get('type') == 'do':
                                game_do = i.get('count')
                            if i.get('status').get('type') == 'collect':
                                game_collect = i.get('count')

                text = {'*Bangumi 用户数据统计：\n\n'+ 
                        bgmuser_data(test_id)['nickname'] +'*\n'
                        '➤ 动画：`'+ str(anime_do) +'在看，'+ str(anime_collect) +'看过`\n'
                        '➤ 图书：`'+ str(book_do)  +'在读，'+ str(book_collect)  +'读过`\n'
                        '➤ 音乐：`'+ str(music_do) +'在听，'+ str(music_collect) +'听过`\n'
                        '➤ 游戏：`'+ str(game_do)  +'在玩，'+ str(game_collect)  +'玩过`\n\n'

                        '[🏠 个人主页](https://bgm.tv/user/'+ str(user_data_get(test_id).get('user_id')) +')\n'
                        }
                
                img_url = 'https://bgm.tv/chart/img/' + str(user_data_get(test_id).get('user_id'))

                bot.delete_message(message.chat.id, message_id=msg.message_id, timeout=20)
                bot.send_photo(chat_id=message.chat.id, photo=img_url, caption=text, parse_mode='Markdown')
                # bot.send_message(message.chat.id, text=text, parse_mode='Markdown', timeout=20)
    else:
        username = message_data[1]
        msg = bot.send_message(message.chat.id, "正在查询请稍后...", reply_to_message_id=message.message_id, parse_mode='Markdown', timeout=20)
        params = {'app_id': APP_ID}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
        url = 'https://api.bgm.tv/user/' + username + '/collections/status'
        r = requests.get(url=url, params=params, headers=headers)
        startus_data = json.loads(r.text)
        try:
            if startus_data.get('code') == 404:
                bot.delete_message(message.chat.id, message_id=msg.message_id, timeout=20)
                bot.send_message(message.chat.id, text='出错了，没有查询到该用户', parse_mode='Markdown', timeout=20)
        except AttributeError:
            if startus_data == None:
                bot.delete_message(message.chat.id, message_id=msg.message_id, timeout=20)
                bot.send_message(message.chat.id, text='您没有观看记录，快去bgm上点几个格子吧~', parse_mode='Markdown', timeout=20)
            else:
                book = None
                book_do = 0
                book_collect = 0
                for i in startus_data:
                    if i.get('name') == 'book':
                        book = i.get('collects')
                        for i in book:
                            if i.get('status').get('type') == 'do':
                                book_do = i.get('count')
                            if i.get('status').get('type') == 'collect':
                                book_collect = i.get('count')
                anime = None
                anime_do = 0
                anime_collect = 0
                for i in startus_data:
                    if i.get('name') == 'anime':
                        anime = i.get('collects')
                        for i in anime:
                            if i.get('status').get('type') == 'do':
                                anime_do = i.get('count')
                            if i.get('status').get('type') == 'collect':
                                anime_collect = i.get('count')
                music = None
                music_do = 0
                music_collect = 0
                for i in startus_data:
                    if i.get('name') == 'music':
                        music = i.get('collects')
                        for i in music:
                            if i.get('status').get('type') == 'do':
                                music_do = i.get('count')
                            if i.get('status').get('type') == 'collect':
                                music_collect = i.get('count')
                game = None
                game_do = 0
                game_collect = 0
                for i in startus_data:
                    if i.get('name') == 'game':
                        game = i.get('collects')
                        for i in game:
                            if i.get('status').get('type') == 'do':
                                game_do = i.get('count')
                            if i.get('status').get('type') == 'collect':
                                game_collect = i.get('count')
                
                url = 'https://api.bgm.tv/user/' + username
                r2 = requests.get(url=url, headers=headers)
                user_data = json.loads(r2.text)
                nickname = user_data.get('nickname') # 获取用户昵称
                uid = user_data.get('id') #获取用户UID

                text = {'*Bangumi 用户数据统计：\n\n'+ 
                        nickname +'*\n'
                        '➤ 动画：`'+ str(anime_do) +'在看，'+ str(anime_collect) +'看过`\n'
                        '➤ 图书：`'+ str(book_do)  +'在读，'+ str(book_collect)  +'读过`\n'
                        '➤ 音乐：`'+ str(music_do) +'在听，'+ str(music_collect) +'听过`\n'
                        '➤ 游戏：`'+ str(game_do)  +'在玩，'+ str(game_collect)  +'玩过`\n\n'

                        f'[🏠 个人主页](https://bgm.tv/user/{uid})\n'
                        }
                
                img_url = f'https://bgm.tv/chart/img/{uid}'

                bot.delete_message(message.chat.id, message_id=msg.message_id, timeout=20)
                bot.send_photo(chat_id=message.chat.id, photo=img_url, caption=text, parse_mode='Markdown')

# 动画条目搜索/查询 Bangumi 用户在看动画
@bot.message_handler(commands=['anime'])
def send_anime(message):
    message_data = message.text.split(' ')
    test_id = message.from_user.id
    if len(message_data) == 1: # 查询 Bangumi 用户在看动画
        if data_seek_get(test_id) == 'no':
            bot.send_message(message.chat.id, "未绑定Bangumi，请私聊使用[/start](https://t.me/"+BOT_USERNAME+"?start=none)进行绑定", parse_mode='Markdown', timeout=20)
        else:
            msg = bot.send_message(message.chat.id, "正在查询请稍后...", reply_to_message_id=message.message_id, parse_mode='Markdown', timeout=20)
            access_token = user_data_get(test_id).get('access_token')
            params = {'subject_type': 2,
                      'type': 3,
                      'limit': 5, # 每页条数
                      'offset': 0 # 开始页
                    }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
                'Authorization': 'Bearer ' + access_token}

            url = 'https://api.bgm.tv/v0/users/'+bgmuser_data(test_id)['username']+'/collections'
            try:
                r = requests.get(url=url, params=params, headers=headers)
            except requests.ConnectionError:
                r = requests.get(url=url, params=params, headers=headers)
            anime_data = json.loads(r.text)
            anime_count = anime_data.get('total') # 总在看数 int
            subject_id_li = [i['subject_id'] for i in anime_data.get('data')] # subject_id 列表 int
            name_li = [subject_info_get(subject_id)['name'] for subject_id in subject_id_li] # 番剧名字 str
            name_cn_li = [subject_info_get(subject_id)['name_cn'] for subject_id in subject_id_li] # 番剧中文名字 str
                
            if subject_id_li == []:
                bot.delete_message(message.chat.id, message_id=msg.message_id, timeout=20)
                bot.send_message(message.chat.id, text='出错啦，您貌似没有收藏的再看', parse_mode='Markdown', timeout=20)
            else:    
                markup = telebot.types.InlineKeyboardMarkup()
                no_li = list(range(1, len(subject_id_li)+ 1))
                markup.add(*[telebot.types.InlineKeyboardButton(text=item[0],callback_data='anime_do'+'|'+str(test_id)+'|'+str(item[1])+'|0'+'|0') for item in list(zip(no_li,subject_id_li))], row_width=5)
                if anime_count > 5:
                    markup.add(telebot.types.InlineKeyboardButton(text='下一页',callback_data='anime_do_page'+'|'+str(test_id)+'|'+'5'))
                eps_li = [eps_get(test_id, subject_id)['progress'] for subject_id in subject_id_li]
                anime_text_data = ''.join(['*['+str(a)+']* '+b+'\n'+c+' `['+ d +']`\n\n' for a,b,c,d in zip(no_li,name_li,name_cn_li,eps_li)])

                text = {'*'+ bgmuser_data(test_id)['nickname'] +' 在看的动画*\n\n'+
                        anime_text_data +
                        '共'+ str(anime_count) +'部'}

                bot.delete_message(message.chat.id, message_id=msg.message_id, timeout=20)
                bot.send_message(message.chat.id, text=text, parse_mode='Markdown', reply_markup=markup , timeout=20)
    else: # 动画条目搜索
        msg = bot.send_message(message.chat.id, "正在搜索请稍后...", reply_to_message_id=message.message_id, parse_mode='Markdown', timeout=20)
        anime_search_keywords = message_data[1]
        subject_type = 2 # 条目类型 1 = book 2 = anime 3 = music 4 = game 6 = real
        start = 0
        search_results_n = search_get(anime_search_keywords, subject_type, start)['search_results_n'] # 搜索结果数量
        if search_results_n == 0:
            bot.send_message(message.chat.id, text='抱歉，没能搜索到您想要的内容', parse_mode='Markdown', timeout=20)
        else:
            search_subject_id_li = search_get(anime_search_keywords, subject_type, start)['subject_id_li'] # 所有查询结果id列表
            search_name_li = search_get(anime_search_keywords, subject_type, start)['name_li'] # 所有查询结果名字列表
            markup = telebot.types.InlineKeyboardMarkup()
            for item in list(zip(search_name_li,search_subject_id_li)):
                markup.add(telebot.types.InlineKeyboardButton(text=item[0],callback_data='animesearch'+'|'+str(anime_search_keywords)+'|'+str(item[1])+'|'+'0'+'|0'))
            if search_results_n > 5:
                markup.add(telebot.types.InlineKeyboardButton(text='下一页',callback_data='spage'+'|'+str(anime_search_keywords)+'|'+'5'))

            text = {'*关于您的 “*`'+ str(anime_search_keywords) +'`*” 搜索结果*\n\n'+
                        
                    '🔍 共'+ str(search_results_n) +'个结果'}

            bot.delete_message(message.chat.id, message_id=msg.message_id, timeout=20)
            bot.send_message(message.chat.id, text=text, parse_mode='Markdown', reply_markup=markup , timeout=20)

# 每日放送查询
@bot.message_handler(commands=['week'])
def send_week(message):
    data = message.text.split(' ')
    if data[0] != "/week":
        bot.send_message(message.chat.id, "输入错误 请输入：`/week 1~7`", parse_mode='Markdown', timeout=20)
    else:
        if len(data) == 2:
            day = data[1]
            check = is_number(day)
            if check is False:
                bot.send_message(message.chat.id, "输入错误 请输入：`/week 1~7`", parse_mode='Markdown', timeout=20)
            else:
                if int(day) > 7:
                    bot.send_message(message.chat.id, "输入错误 请输入：`/week 1~7`", parse_mode='Markdown', timeout=20)
                else:
                    msg = bot.send_message(message.chat.id, "正在搜索请稍后...", reply_to_message_id=message.message_id, parse_mode='Markdown', timeout=20)
                    text = week_text(day)['text']
                    markup = week_text(day)['markup']
                    bot.delete_message(message.chat.id, message_id=msg.message_id, timeout=20)
                    bot.send_message(message.chat.id, text=text, parse_mode='Markdown', reply_markup=markup , timeout=20)
        else:
            bot.send_message(message.chat.id, "输入错误 请输入：`/week 1~7`", parse_mode='Markdown', timeout=20)

# 判断输入是否是数字
def is_number(str):
    try:
        float(str)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(str)
        return True
    except (ValueError, TypeError):
        pass

    return False

# 判断是否绑定Bangumi
def data_seek_get(test_id):
    with open('bgm_data.json') as f:                        # 打开文件
        data_seek = json.loads(f.read())                    # 读取
    data_li = [i['tg_user_id'] for i in data_seek]          # 写入列表
    if int(test_id) in data_li:                             # 判断列表内是否有被验证的UID
        data_back = 'yes'
    else:
        data_back = 'no'
    return data_back

# 获取用户数据
def user_data_get(test_id):
    with open('bgm_data.json') as f:
        data_seek = json.loads(f.read())
    user_data = None
    for i in data_seek:
        if i.get('tg_user_id') == test_id:
            expiry_time = i.get('expiry_time')
            now_time = datetime.datetime.now().strftime("%Y%m%d")
            if now_time >= expiry_time:   # 判断密钥是否过期
                user_data = expiry_data_get(test_id)
            else:
                user_data = i.get('data',{})
    return user_data

# 更新过期用户数据
def expiry_data_get(test_id):
    with open('bgm_data.json') as f:
        data_seek = json.loads(f.read())
    refresh_token = None
    for i in data_seek:
        if i.get('tg_user_id') == test_id:
            refresh_token = i.get('data',{}).get('refresh_token')
    CALLBACK_URL = f'{WEBSITE_BASE}oauth_callback'
    resp = requests.post(
        'https://bgm.tv/oauth/access_token',
        data={
            'grant_type': 'refresh_token',
            'client_id': APP_ID,
            'client_secret': APP_SECRET,
            'refresh_token': refresh_token,
            'redirect_uri': CALLBACK_URL,
        },
        headers = {
        "User-Agent": "",
        }
    )
    access_token = json.loads(resp.text).get('access_token')    #更新access_token
    refresh_token = json.loads(resp.text).get('refresh_token')  #更新refresh_token
    expiry_time = (datetime.datetime.now()+datetime.timedelta(days=7)).strftime("%Y%m%d")#更新过期时间
    
    # 替换数据
    if access_token or refresh_token != None:
        with open("bgm_data.json", 'r+', encoding='utf-8') as f:
            data = json.load(f)
            for i in data:
                if i['tg_user_id'] == test_id:
                    i['data']['access_token'] = access_token
                    i['data']['refresh_token'] = refresh_token
                    i['expiry_time'] = expiry_time
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.truncate()
    
    # 读取数据
    with open('bgm_data.json') as f:
        data_seek = json.loads(f.read())
    user_data = None
    for i in data_seek:
        if i.get('tg_user_id') == test_id:
            user_data = i.get('data',{})
    return user_data

# 获取BGM用户信息
def bgmuser_data(test_id):
    access_token = user_data_get(test_id).get('access_token')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
        'Authorization': 'Bearer ' + access_token}
    url = 'https://api.bgm.tv/user/' + str(user_data_get(test_id).get('user_id'))
    try:
        r = requests.get(url=url, headers=headers)
    except requests.ConnectionError:
        r = requests.get(url=url, headers=headers)
    user_data = json.loads(r.text)

    nickname = user_data.get('nickname')
    username = user_data.get('username')

    user_data = {
        'nickname': nickname, # 用户昵称 str
        'username': username  # 用户username 没有设置则返回 uid str
    }
    return user_data

# 获取用户观看eps
def eps_get(test_id, subject_id):
    access_token = user_data_get(test_id).get('access_token')
    params = {
        'subject_id': subject_id,
        'type': 0}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
        'Authorization': 'Bearer ' + access_token}
    url = 'https://api.bgm.tv/v0/episodes'

    try:
        r = requests.get(url=url, params=params, headers=headers)
    except requests.ConnectionError:
        r = requests.get(url=url, params=params, headers=headers)

    data_eps = json.loads(r.text).get('data')
    epsid_li = [i['id'] for i in data_eps] # 所有eps_id

    params = {
        'subject_id': subject_id}
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
        'Authorization': 'Bearer ' + access_token}
    url = 'https://api.bgm.tv/user/' + str(user_data_get(test_id).get('user_id')) + '/progress'
    try:
        r = requests.get(url=url, params=params, headers=headers)
    except requests.ConnectionError:
        r = requests.get(url=url, params=params, headers=headers)
    
    try:
        data_watched = json.loads(r.text).get('eps')
    except AttributeError:
        watched_id_li = [0] # 无观看集数
    else:
        watched_id_li = [i['id'] for i in data_watched] # 已观看 eps_id

    eps_n = len(set(epsid_li)) # 总集数
    watched_n = len(set(epsid_li) & set(watched_id_li)) # 已观看了集数
    
    unwatched_id = epsid_li # 去除已观看过集数的 eps_id
    try:
        for watched_li in watched_id_li:
            unwatched_id.remove(watched_li)
    except ValueError:
        pass

    # 输出
    eps_data = {'progress': str(watched_n) + '/' + str(eps_n),   # 已观看/总集数 进度 str
                'watched': str(watched_n),                       # 已观看集数 str
                'eps_n': str(eps_n),                             # 总集数 str
                'unwatched_id': unwatched_id}                    # 未观看 eps_di list

    return eps_data

# 剧集信息获取 不需Access Token
def subject_info_get(subject_id):
    with open('subject_info_data.json', encoding='utf-8') as f:
        info_data = json.loads(f.read())
    id_li = [i['subject_id'] for i in info_data]
    if int(subject_id) in id_li:
        name = [i['name'] for i in info_data if i['subject_id'] == int(subject_id)][0]
        name_cn = [i['name_cn'] for i in info_data if i['subject_id'] == int(subject_id)][0]
        eps_count = [i['eps_count'] for i in info_data if i['subject_id'] == int(subject_id)][0]
        air_date = [i['air_date'] for i in info_data if i['subject_id'] == int(subject_id)][0]
        platform = [i['platform'] for i in info_data if i['subject_id'] == int(subject_id)][0]
        air_weekday = [i['air_weekday'] for i in info_data if i['subject_id'] == int(subject_id)][0]
        score = [i['score'] for i in info_data if i['subject_id'] == int(subject_id)][0]
        # 输出
        subject_info_data = {'name' : name,                 # 剧集名 str
                             'name_cn': name_cn,            # 剧集中文名 str
                             'eps_count': eps_count,        # 总集数 int
                             'air_date': air_date,          # 放送开始日期 str
                             'platform': platform,          # 放送类型 str
                             'air_weekday': air_weekday,    # 每周放送星期 str
                             'score': score}                # BGM 评分 int
    else:
        params = {'responseGroup': 'large'}
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
        url = f'https://api.bgm.tv/v0/subjects/{subject_id}'
        try:
            r = requests.get(url=url, params=params, headers=headers)
        except requests.ConnectionError:
            r = requests.get(url=url, params=params, headers=headers)
        info_data = json.loads(r.text)
        name = info_data.get('name')
        name_cn = info_data.get('name_cn')
        eps_count = info_data.get('eps')
        air_date = info_data.get('date')
        platform = info_data.get('platform')
        try:
            air_weekday = [i['value'] for i in info_data.get('infobox') if i['key'] == '放送星期'][0]
        except IndexError:
            air_weekday = 'None'
        try:
            score = info_data.get('rating').get('score')
        except AttributeError:
            score = 0
        # 输出
        subject_info_data = {'subject_id': int(subject_id),
                             'name' : name,                 # 剧集名 str
                             'name_cn': name_cn,            # 剧集中文名 str
                             'eps_count': eps_count,        # 总集数 int
                             'air_date': air_date,          # 放送开始日期 str
                             'platform': platform,          # 放送类型 str
                             'air_weekday': air_weekday,    # 每周放送星期 str
                             'score': score}                # BGM 评分 int

        with open("subject_info_data.json", 'r+', encoding='utf-8') as f:    # 打开文件
            try:
                data = json.load(f)                                          # 读取
            except:
                data = []                                                    # 空文件
            data.append(subject_info_data)                                   # 添加
            f.seek(0, 0)                                                     # 重新定位回开头
            json.dump(data, f, ensure_ascii=False, indent=4)                 # 写入

    return subject_info_data

# 更新收视进度状态
def eps_status_get(test_id, eps_id, status):
    access_token = user_data_get(test_id).get('access_token')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
        'Authorization': 'Bearer ' + access_token}

    url = f'https://api.bgm.tv/ep/{eps_id}/status/{status}'

    r = requests.get(url=url, headers=headers)
    
    return r

# 更新收藏状态
def collection_post(test_id, subject_id, status, rating):
    access_token = user_data_get(test_id).get('access_token')
    if rating == None or rating == 0:
        params = {"status": (None, status)}
    else:
        params = {"status": (None, status),"rating": (None, rating)}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
        'Authorization': 'Bearer ' + access_token}

    url = f'https://api.bgm.tv/collection/{subject_id}/update'

    r = requests.post(url=url, files=params, headers=headers)

    return r

# 获取用户评分
def user_rating_get(test_id, subject_id):
    access_token = user_data_get(test_id).get('access_token')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
        'Authorization': 'Bearer ' + access_token}

    url = f'https://api.bgm.tv/collection/{subject_id}'

    r = requests.get(url=url, headers=headers)
    user_rating_data = json.loads(r.text)
    try:
        user_startus = user_rating_data.get('status',{}).get('type')
    except:
        user_startus = 'collect'
    user_rating = user_rating_data.get('rating')

    user_rating_data = {'user_startus': user_startus,   # 用户收藏状态 str
                        'user_rating': user_rating}     # 用户评分 int

    return user_rating_data

# 动画简介图片获取 不需Access Token
def anime_img(subject_id):
    anime_name = subject_info_get(subject_id)['name']
    query = '''
    query ($id: Int, $page: Int, $perPage: Int, $search: String) {
        Page (page: $page, perPage: $perPage) {
            pageInfo {
                total
                currentPage
                lastPage
                hasNextPage
                perPage
            }
            media (id: $id, search: $search) {
                id
                title {
                    romaji
                }
            }
        }
    }
    '''
    variables = {
        'search': anime_name,
        'page': 1,
        'perPage': 1
    }
    url = 'https://graphql.anilist.co'
    try:
        r = requests.post(url, json={'query': query, 'variables': variables})
    except requests.ConnectionError:
        r = requests.post(url, json={'query': query, 'variables': variables})
    
    anilist_data = json.loads(r.text).get('data').get('Page').get('media')

    try:
        anilist_id = [i['id'] for i in anilist_data][0]
    except IndexError:
        img_url = None
    else:
        img_url = f'https://img.anili.st/media/{anilist_id}'

    return img_url

# 条目搜索 不需Access Token
def search_get(keywords, type, start):
    
    max_results = 5 # 每页最大条数 5 个
    params = {
        'type': type,
        'start': start,
        'max_results': max_results}
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
    url = f'https://api.bgm.tv/search/subject/{keywords}'

    try:
        r = requests.get(url=url, params=params, headers=headers)
    except requests.ConnectionError:
        r = requests.get(url=url, params=params, headers=headers)

    try:
        data_search = json.loads(r.text)
    except:
        search_results_n = 0
        subject_id_li = []
        name_li = []
    else:
        search_results_n = data_search.get('results')
    
        subject_id_data = data_search.get('list')
        subject_id_li = [i['id'] for i in subject_id_data]
        name_li = [i['name'] for i in subject_id_data]

    # 输出
    search_data = {'search_results_n': search_results_n, # 搜索结果数量 int
                   'subject_id_li': subject_id_li,       # 所有查询结果id列表 list
                   'name_li': name_li}                   # 所有查询结果名字列表 list

    return search_data

# 每日放送查询输出文字及其按钮
def week_text(day):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',}
    url = 'https://api.bgm.tv/calendar'
    try:
        r = requests.get(url=url, headers=headers)
    except requests.ConnectionError:
        r = requests.get(url=url, headers=headers)
    week_data = json.loads(r.text)
    for i in week_data:
        if i.get('weekday',{}).get('id') == int(day):
            items = i.get('items')
            subject_id_li = [i['id'] for i in items]
            name_li = [i['name'] for i in items]
            name_cn_li = [i['name_cn'] for i in items]
            no_li = list(range(1, len(subject_id_li)+ 1))
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(*[telebot.types.InlineKeyboardButton(text=item[0],callback_data='animesearch'+'|'+'week'+'|'+str(item[1])+'|'+str(day)+'|0') for item in list(zip(no_li,subject_id_li))])

            air_weekday = str(day).replace('1', '星期一').replace('2', '星期二').replace('3', '星期三').replace('4', '星期四').replace('5', '星期五').replace('6', '星期六').replace('7', '星期日') # 放送日期
            text_data = ''.join(['*['+str(a)+']* '+b+'\n'+c+'\n\n' for a,b,c in zip(no_li,name_li,name_cn_li)])
            anime_count = len(subject_id_li)
            text = {'*在 '+ air_weekday +' 放送的节目*\n\n'+
                    text_data +
                    '共'+ str(anime_count) +'部'}

            week_text_data = {
                'text': text,    # 查询文字
                'markup': markup # 按钮
            }

    return week_text_data

# 动画再看详情
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'anime_do')
def anime_do_callback(call):
    tg_from_id = call.from_user.id
    test_id = int(call.data.split('|')[1])
    subject_id = call.data.split('|')[2]
    back = int(call.data.split('|')[3])
    back_page = call.data.split('|')[4]

    if tg_from_id == test_id:
        img_url = anime_img(subject_id)

        text = {'*'+ subject_info_get(subject_id)['name_cn'] +'*\n'
                ''+ subject_info_get(subject_id)['name'] +'\n\n'

                'BGM ID：`' + str(subject_id) + '`\n'
                '➤ BGM 平均评分：`'+ str(subject_info_get(subject_id)['score']) +'`🌟\n'
                '➤ 您的评分：`'+ str(user_rating_get(test_id, subject_id)['user_rating']) +'`🌟\n'
                '➤ 放送类型：`'+ subject_info_get(subject_id)['platform'] +'`\n'
                '➤ 放送开始：`'+ subject_info_get(subject_id)['air_date'] + '`\n'
                '➤ 放送星期：`'+ subject_info_get(subject_id)['air_weekday'] + '`\n'
                '➤ 观看进度：`'+ eps_get(test_id, subject_id)['progress'] + '`\n\n'
                
                '💬 [吐槽箱](https://bgm.tv/subject/'+ str(subject_id) +'/comments)\n'}

        markup = telebot.types.InlineKeyboardMarkup()
        unwatched_id = eps_get(test_id, subject_id)['unwatched_id']
        if unwatched_id == []:
            markup.add(telebot.types.InlineKeyboardButton(text='返回',callback_data='anime_do_page'+'|'+str(test_id)+'|'+back_page),telebot.types.InlineKeyboardButton(text='评分',callback_data='rating'+'|'+str(test_id)+'|'+'0'+'|'+str(subject_id)+'|'+back_page))
            markup.add(telebot.types.InlineKeyboardButton(text='收藏管理',callback_data='collection'+'|'+str(tg_from_id)+'|'+str(subject_id)+'|'+'anime_do'+'|'+'0'+'|'+'null'+'|'+back_page))
        else:    
            markup.add(telebot.types.InlineKeyboardButton(text='返回',callback_data='anime_do_page'+'|'+str(test_id)+'|'+back_page),telebot.types.InlineKeyboardButton(text='评分',callback_data='rating'+'|'+str(test_id)+'|'+'0'+'|'+str(subject_id)+'|'+back_page),telebot.types.InlineKeyboardButton(text='已看最新',callback_data='anime_eps'+'|'+str(test_id)+'|'+str(unwatched_id[0])+'|'+str(subject_id)+'|'+back_page))
            markup.add(telebot.types.InlineKeyboardButton(text='收藏管理',callback_data='collection'+'|'+str(tg_from_id)+'|'+str(subject_id)+'|'+'anime_do'+'|'+'0'+'|'+'null'+'|'+back_page))
        if back == 1:
            if call.message.content_type == 'photo':
                bot.edit_message_caption(caption=text, chat_id=call.message.chat.id , message_id=call.message.message_id, parse_mode='Markdown', reply_markup=markup)
            else:
                bot.edit_message_text(text=text, parse_mode='Markdown', chat_id=call.message.chat.id , message_id=call.message.message_id, reply_markup=markup)
        else:
            bot.delete_message(chat_id=call.message.chat.id , message_id=call.message.message_id, timeout=20) # 删除用户在看动画列表消息
            if img_url == None: # 是否有动画简介图片
                bot.send_message(chat_id=call.message.chat.id, text=text, parse_mode='Markdown', reply_markup=markup, timeout=20)
            else:
                bot.send_photo(chat_id=call.message.chat.id, photo=img_url, caption=text, parse_mode='Markdown', reply_markup=markup)
            # bot.edit_message_text(text=text, parse_mode='Markdown', chat_id=call.message.chat.id , message_id=call.message.message_id, reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, text='和你没关系，别点了~', show_alert=True)

# 评分
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'rating')
def rating_callback(call):
    tg_from_id = call.from_user.id
    test_id = int(call.data.split('|')[1])
    if tg_from_id == test_id:
        rating_data = int(call.data.split('|')[2])
        subject_id = call.data.split('|')[3]
        back_page = call.data.split('|')[4]
        def rating_text():
            text = {'*'+ subject_info_get(subject_id)['name_cn'] +'*\n'
                    ''+ subject_info_get(subject_id)['name'] +'\n\n'

                    'BGM ID：`' + str(subject_id) + '`\n\n'

                    '➤ BGM 平均评分：`'+ str(subject_info_get(subject_id)['score']) +'`🌟\n'
                    '➤ 您的评分：`'+ str(user_rating_get(test_id, subject_id)['user_rating']) +'`🌟\n\n'

                    '➤ 观看进度：`'+ eps_get(test_id, subject_id)['progress'] + '`\n\n'

                    '💬 [吐槽箱](https://bgm.tv/subject/'+ str(subject_id) +'/comments)\n\n'

                    '请点按下列数字进行评分'}

            markup = telebot.types.InlineKeyboardMarkup()       
            markup.add(telebot.types.InlineKeyboardButton(text='返回',callback_data='anime_do'+'|'+str(test_id)+'|'+str(subject_id)+'|1'+'|'+back_page),telebot.types.InlineKeyboardButton(text='1',callback_data='rating'+'|'+str(test_id)+'|'+'1'+'|'+str(subject_id)),telebot.types.InlineKeyboardButton(text='2',callback_data='rating'+'|'+str(test_id)+'|'+'2'+'|'+str(subject_id)),telebot.types.InlineKeyboardButton(text='3',callback_data='rating'+'|'+str(test_id)+'|'+'3'+'|'+str(subject_id)),telebot.types.InlineKeyboardButton(text='4',callback_data='rating'+'|'+str(test_id)+'|'+'4'+'|'+str(subject_id)),telebot.types.InlineKeyboardButton(text='5',callback_data='rating'+'|'+str(test_id)+'|'+'5'+'|'+str(subject_id)),telebot.types.InlineKeyboardButton(text='6',callback_data='rating'+'|'+str(test_id)+'|'+'6'+'|'+str(subject_id)),telebot.types.InlineKeyboardButton(text='7',callback_data='rating'+'|'+str(test_id)+'|'+'7'+'|'+str(subject_id)),telebot.types.InlineKeyboardButton(text='8',callback_data='rating'+'|'+str(test_id)+'|'+'8'+'|'+str(subject_id)),telebot.types.InlineKeyboardButton(text='9',callback_data='rating'+'|'+str(test_id)+'|'+'9'+'|'+str(subject_id)),telebot.types.InlineKeyboardButton(text='10',callback_data='rating'+'|'+str(test_id)+'|'+'10'+'|'+str(subject_id)))
            if call.message.content_type == 'photo':
                bot.edit_message_caption(caption=text, chat_id=call.message.chat.id , message_id=call.message.message_id, parse_mode='Markdown', reply_markup=markup)
            else:
                bot.edit_message_text(text=text, parse_mode='Markdown', chat_id=call.message.chat.id , message_id=call.message.message_id, reply_markup=markup)
            
        if rating_data == 0:
            rating_text()
        status = user_rating_get(test_id, subject_id)['user_startus']
        if rating_data == 1:
            rating = '1'
            collection_post(test_id, subject_id, status, rating)
            rating_text()
        if rating_data == 2:
            rating = '2'
            collection_post(test_id, subject_id, status, rating)
            rating_text()
        if rating_data == 3:
            rating = '3'
            collection_post(test_id, subject_id, status, rating)
            rating_text()
        if rating_data == 4:
            rating = '4'
            collection_post(test_id, subject_id, status, rating)
            rating_text()
        if rating_data == 5:
            rating = '5'
            collection_post(test_id, subject_id, status, rating)
            rating_text()
        if rating_data == 6:
            rating = '6'
            collection_post(test_id, subject_id, status, rating)
            rating_text()
        if rating_data == 7:
            rating = '7'
            collection_post(test_id, subject_id, status, rating)
            rating_text()
        if rating_data == 8:
            rating = '8'
            collection_post(test_id, subject_id, status, rating)
            rating_text()
        if rating_data == 9:
            rating = '9'
            collection_post(test_id, subject_id, status, rating)
            rating_text()
        if rating_data == 3:
            rating = '10'
            collection_post(test_id, subject_id, status, rating) 
            rating_text()          
    else:
        bot.answer_callback_query(call.id, text='和你没关系，别点了~', show_alert=True)

# 已看最新
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'anime_eps')
def anime_eps_callback(call):
    tg_from_id = call.from_user.id
    test_id = int(call.data.split('|')[1])
    if tg_from_id == test_id:
        eps_id = int(call.data.split('|')[2])
        try:
            remove = call.data.split('|')[5]
            if remove == 'remove':
                eps_status_get(test_id, eps_id, 'remove')  # 更新观看进度为撤销
                bot.send_message(chat_id=call.message.chat.id, text='已撤销，已看最新集数', parse_mode='Markdown', timeout=20)
        except IndexError:
                eps_status_get(test_id, eps_id, 'watched') # 更新观看进度为看过

        subject_id = int(call.data.split('|')[3])
        back_page = call.data.split('|')[4]
        rating = str(user_rating_get(test_id, subject_id)['user_rating'])

        text = {'*'+ subject_info_get(subject_id)['name_cn'] +'*\n'
                ''+ subject_info_get(subject_id)['name'] +'\n\n'

                'BGM ID：`' + str(subject_id) + '`\n'
                '➤ BGM 平均评分：`'+ str(subject_info_get(subject_id)['score']) +'`🌟\n'
                '➤ 您的评分：`'+ str(rating) +'`🌟\n'
                '➤ 放送类型：`'+ subject_info_get(subject_id)['platform'] +'`\n'
                '➤ 放送开始：`'+ subject_info_get(subject_id)['air_date'] + '`\n'
                '➤ 放送星期：`'+ subject_info_get(subject_id)['air_weekday'] + '`\n'
                '➤ 观看进度：`'+ eps_get(test_id, subject_id)['progress'] + '`\n\n'
                
                '💬 [吐槽箱](https://bgm.tv/subject/'+ str(subject_id) +'/comments)\n'
                '📝 [第'+ eps_get(test_id, subject_id)['watched'] +'话评论](https://bgm.tv/ep/'+ str(eps_id) +')\n'}

        markup = telebot.types.InlineKeyboardMarkup()
        unwatched_id = eps_get(test_id, subject_id)['unwatched_id']
        if unwatched_id == []:
            status = 'collect'
            collection_post(test_id, subject_id, status, rating) # 看完最后一集自动更新收藏状态为看过
            markup.add(telebot.types.InlineKeyboardButton(text='返回',callback_data='anime_do_page'+'|'+str(test_id)+'|'+back_page),telebot.types.InlineKeyboardButton(text='评分',callback_data='rating'+'|'+str(test_id)+'|'+'0'+'|'+str(subject_id)+'|'+back_page))
            markup.add(telebot.types.InlineKeyboardButton(text='收藏管理',callback_data='collection'+'|'+str(tg_from_id)+'|'+str(subject_id)+'|'+'anime_do'+'|'+'0'+'|'+'null'+'|'+back_page),telebot.types.InlineKeyboardButton(text='撤销最新观看',callback_data='anime_eps'+'|'+str(test_id)+'|'+str(eps_id)+'|'+str(subject_id)+'|'+back_page+'|remove'))
        else:    
            markup.add(telebot.types.InlineKeyboardButton(text='返回',callback_data='anime_do_page'+'|'+str(test_id)+'|'+back_page),telebot.types.InlineKeyboardButton(text='评分',callback_data='rating'+'|'+str(test_id)+'|'+'0'+'|'+str(subject_id)+'|'+back_page),telebot.types.InlineKeyboardButton(text='已看最新',callback_data='anime_eps'+'|'+str(test_id)+'|'+str(unwatched_id[0])+'|'+str(subject_id)+'|'+back_page))
            markup.add(telebot.types.InlineKeyboardButton(text='收藏管理',callback_data='collection'+'|'+str(tg_from_id)+'|'+str(subject_id)+'|'+'anime_do'+'|'+'0'+'|'+'null'+'|'+back_page),telebot.types.InlineKeyboardButton(text='撤销最新观看',callback_data='anime_eps'+'|'+str(test_id)+'|'+str(eps_id)+'|'+str(subject_id)+'|'+back_page+'|remove'))
        if call.message.content_type == 'photo':
            bot.edit_message_caption(caption=text, chat_id=call.message.chat.id , message_id=call.message.message_id, parse_mode='Markdown', reply_markup=markup)
        else:
            bot.edit_message_text(text=text, parse_mode='Markdown', chat_id=call.message.chat.id , message_id=call.message.message_id, reply_markup=markup)
            # bot.edit_message_text(text=text, parse_mode='Markdown', chat_id=call.message.chat.id , message_id=call.message.message_id, reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, text='和你没关系，别点了~', show_alert=True)

# 动画再看详情页返回翻页
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'anime_do_page')
def anime_do_page_callback(call):
    test_id = int(call.data.split('|')[1])
    offset = int(call.data.split('|')[2])
    tg_from_id = call.from_user.id
    if tg_from_id == test_id:
        access_token = user_data_get(test_id).get('access_token')
        params = {'subject_type': 2,
                  'type': 3,
                  'limit': 5, # 每页条数
                  'offset': offset # 开始页
                }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36',
            'Authorization': 'Bearer ' + access_token}

        url = 'https://api.bgm.tv/v0/users/'+bgmuser_data(test_id)['username']+'/collections'
        try:
            r = requests.get(url=url, params=params, headers=headers)
        except requests.ConnectionError:
            r = requests.get(url=url, params=params, headers=headers)
        anime_data = json.loads(r.text)
        anime_count = anime_data.get('total') # 总在看数 int
        subject_id_li = [i['subject_id'] for i in anime_data.get('data')] # subject_id 列表 int
        name_li = [subject_info_get(subject_id)['name'] for subject_id in subject_id_li] # 番剧名字 str
        name_cn_li = [subject_info_get(subject_id)['name_cn'] for subject_id in subject_id_li] # 番剧中文名字 str

        markup = telebot.types.InlineKeyboardMarkup()
        no_li = list(range(1, len(subject_id_li)+ 1))
        markup.add(*[telebot.types.InlineKeyboardButton(text=item[0],callback_data='anime_do'+'|'+str(test_id)+'|'+str(item[1])+'|0'+'|'+str(offset)) for item in list(zip(no_li,subject_id_li))], row_width=5)
        
        if anime_count <= 5:
            markup.add()
        elif offset == 0:
            markup.add(telebot.types.InlineKeyboardButton(text='下一页',callback_data='anime_do_page'+'|'+str(test_id)+'|'+str(offset+5)))
        elif offset+5 >= anime_count:
            markup.add(telebot.types.InlineKeyboardButton(text='上一页',callback_data='anime_do_page'+'|'+str(test_id)+'|'+str(offset-5)))
        else:
            markup.add(telebot.types.InlineKeyboardButton(text='上一页',callback_data='anime_do_page'+'|'+str(test_id)+'|'+str(offset-5)),telebot.types.InlineKeyboardButton(text='下一页',callback_data='anime_do_page'+'|'+str(test_id)+'|'+str(offset+5)))

        eps_li = [eps_get(test_id, subject_id)['progress'] for subject_id in subject_id_li]
        anime_text_data = ''.join(['*['+str(a)+']* '+b+'\n'+c+' `['+ d +']`\n\n' for a,b,c,d in zip(no_li,name_li,name_cn_li,eps_li)])

        text = {'*'+ bgmuser_data(test_id)['nickname'] +' 在看的动画*\n\n'+
                anime_text_data +
                '共'+ str(anime_count) +'部'}
        
        if call.message.content_type == 'photo':
            bot.delete_message(chat_id=call.message.chat.id , message_id=call.message.message_id, timeout=20)
            bot.send_message(chat_id=call.message.chat.id, text=text, parse_mode='Markdown', reply_markup=markup, timeout=20)
        else:
            bot.edit_message_text(text=text, parse_mode='Markdown', chat_id=call.message.chat.id , message_id=call.message.message_id, reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, text='和你没关系，别点了~', show_alert=True)

# 搜索翻页
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'spage')
def spage_callback(call):
    anime_search_keywords = call.data.split('|')[1]
    start = int(call.data.split('|')[2])
    subject_type = 2 # 条目类型 1 = book 2 = anime 3 = music 4 = game 6 = real
    search_results_n = search_get(anime_search_keywords, subject_type, start)['search_results_n'] # 搜索结果数量
    if search_results_n == 0:
        text= '已经没有了'
    else:
        search_subject_id_li = search_get(anime_search_keywords, subject_type, start)['subject_id_li'] # 所有查询结果id列表
        search_name_li = search_get(anime_search_keywords, subject_type, start)['name_li'] # 所有查询结果名字列表
        markup = telebot.types.InlineKeyboardMarkup()
        for item in list(zip(search_name_li,search_subject_id_li)):
            markup.add(telebot.types.InlineKeyboardButton(text=item[0],callback_data='animesearch'+'|'+str(anime_search_keywords)+'|'+str(item[1])+'|'+str(start)+'|0'))
        
        if search_results_n <= 5:
            markup.add()
        elif start == 0:
            markup.add(telebot.types.InlineKeyboardButton(text='下一页',callback_data='spage'+'|'+str(anime_search_keywords)+'|'+str(start+5)))
        elif start+5 >= search_results_n:
            markup.add(telebot.types.InlineKeyboardButton(text='上一页',callback_data='spage'+'|'+str(anime_search_keywords)+'|'+str(start-5)))
        else:
            markup.add(telebot.types.InlineKeyboardButton(text='上一页',callback_data='spage'+'|'+str(anime_search_keywords)+'|'+str(start-5)),telebot.types.InlineKeyboardButton(text='下一页',callback_data='spage'+'|'+str(anime_search_keywords)+'|'+str(start+5)))

        text = {'*关于您的 “*`'+ str(anime_search_keywords) +'`*” 搜索结果*\n\n'+
                    
                '🔍 共'+ str(search_results_n) +'个结果'}
    
    if call.message.content_type == 'photo':
        bot.delete_message(chat_id=call.message.chat.id , message_id=call.message.message_id, timeout=20)
        bot.send_message(chat_id=call.message.chat.id, text=text, parse_mode='Markdown', reply_markup=markup, timeout=20)
    else:
        bot.edit_message_text(text=text, parse_mode='Markdown', chat_id=call.message.chat.id , message_id=call.message.message_id, reply_markup=markup)

# 搜索动画详情页
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'animesearch')
def animesearch_callback(call):
    anime_search_keywords = call.data.split('|')[1]
    subject_id = call.data.split('|')[2]
    start = int(call.data.split('|')[3])
    back = int(call.data.split('|')[4])
    
    img_url = anime_img(subject_id)

    text = {'*'+ subject_info_get(subject_id)['name_cn'] +'*\n'
            ''+ subject_info_get(subject_id)['name'] +'\n\n'

            'BGM ID：`' + str(subject_id) + '`\n'
            '➤ BGM 平均评分：`'+ str(subject_info_get(subject_id)['score']) +'`🌟\n'
            '➤ 放送类型：`'+ subject_info_get(subject_id)['platform'] +'`\n'
            '➤ 集数：共`'+ str(subject_info_get(subject_id)['eps_count']) +'`集\n'
            '➤ 放送开始：`'+ subject_info_get(subject_id)['air_date'] + '`\n'
            '➤ 放送星期：`'+ subject_info_get(subject_id)['air_weekday'] + '`\n\n' 
            
            '📖 [详情](https://bgm.tv/subject/'+ str(subject_id) +')\n'
            '💬 [吐槽箱](https://bgm.tv/subject/'+ str(subject_id) +'/comments)\n'}

    markup = telebot.types.InlineKeyboardMarkup()
    if anime_search_keywords == 'week':
        tg_from_id = call.from_user.id
        markup.add(telebot.types.InlineKeyboardButton(text='返回',callback_data='back_week'+'|'+str(start)), telebot.types.InlineKeyboardButton(text='收藏',callback_data='collection'+'|'+str(tg_from_id)+'|'+str(subject_id)+'|'+str(anime_search_keywords)+'|'+str(start)+'|'+'null'))
    else:    
        tg_from_id = call.from_user.id
        markup.add(telebot.types.InlineKeyboardButton(text='返回',callback_data='spage'+'|'+str(anime_search_keywords)+'|'+str(start)), telebot.types.InlineKeyboardButton(text='收藏',callback_data='collection'+'|'+str(tg_from_id)+'|'+str(subject_id)+'|'+str(anime_search_keywords)+'|'+str(start)+'|'+'null'))
    
    if back == 1:
        if call.message.content_type == 'photo':
                bot.edit_message_caption(caption=text, chat_id=call.message.chat.id , message_id=call.message.message_id, parse_mode='Markdown', reply_markup=markup)
        else:
            bot.edit_message_text(text=text, parse_mode='Markdown', chat_id=call.message.chat.id , message_id=call.message.message_id, reply_markup=markup)
    else:
        bot.delete_message(chat_id=call.message.chat.id , message_id=call.message.message_id, timeout=20)
        if img_url == None:
            bot.send_message(chat_id=call.message.chat.id, text=text, parse_mode='Markdown', reply_markup=markup, timeout=20)
        else:
            bot.send_photo(chat_id=call.message.chat.id, photo=img_url, caption=text, parse_mode='Markdown', reply_markup=markup)

# 收藏
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'collection')
def collection_callback(call):
    test_id = int(call.data.split('|')[1])
    subject_id = call.data.split('|')[2]
    anime_search_keywords = call.data.split('|')[3]
    start = call.data.split('|')[4]
    status = call.data.split('|')[5]
    tg_from_id = call.from_user.id
    
    if status == 'null':
        if data_seek_get(tg_from_id) == 'no':
            bot.send_message(chat_id=call.message.chat.id, text='您未绑定Bangumi，请私聊使用[/start](https://t.me/'+BOT_USERNAME+'?start=none)进行绑定', parse_mode='Markdown', timeout=20)
        else:
            text = {'*您想将 “*`'+ subject_info_get(subject_id)['name'] +'`*” 收藏为*\n\n'}
            markup = telebot.types.InlineKeyboardMarkup()
            if anime_search_keywords == 'anime_do':
                back_page = call.data.split('|')[6]
                markup.add(telebot.types.InlineKeyboardButton(text='返回',callback_data='anime_do'+'|'+str(test_id)+'|'+str(subject_id)+'|1'+'|'+back_page), telebot.types.InlineKeyboardButton(text='想看',callback_data='collection'+'|'+str(test_id)+'|'+str(subject_id)+'|'+str(anime_search_keywords)+'|'+str(start)+'|'+'wish'), telebot.types.InlineKeyboardButton(text='看过',callback_data='collection'+'|'+str(test_id)+'|'+str(subject_id)+'|'+str(anime_search_keywords)+'|'+str(start)+'|'+'collect'), telebot.types.InlineKeyboardButton(text='在看',callback_data='collection'+'|'+str(test_id)+'|'+str(subject_id)+'|'+str(anime_search_keywords)+'|'+str(start)+'|'+'do'), telebot.types.InlineKeyboardButton(text='搁置',callback_data='collection'+'|'+str(test_id)+'|'+str(subject_id)+'|'+str(anime_search_keywords)+'|'+str(start)+'|'+'on_hold'), telebot.types.InlineKeyboardButton(text='抛弃',callback_data='collection'+'|'+str(test_id)+'|'+str(subject_id)+'|'+str(anime_search_keywords)+'|'+str(start)+'|'+'dropped'))
            else:
                markup.add(telebot.types.InlineKeyboardButton(text='返回',callback_data='animesearch'+'|'+str(anime_search_keywords)+'|'+str(subject_id)+'|'+str(start)+'|1'), telebot.types.InlineKeyboardButton(text='想看',callback_data='collection'+'|'+str(tg_from_id)+'|'+str(subject_id)+'|'+str(anime_search_keywords)+'|'+str(start)+'|'+'wish'), telebot.types.InlineKeyboardButton(text='看过',callback_data='collection'+'|'+str(tg_from_id)+'|'+str(subject_id)+'|'+str(anime_search_keywords)+'|'+str(start)+'|'+'collect'), telebot.types.InlineKeyboardButton(text='在看',callback_data='collection'+'|'+str(tg_from_id)+'|'+str(subject_id)+'|'+str(anime_search_keywords)+'|'+str(start)+'|'+'do'), telebot.types.InlineKeyboardButton(text='搁置',callback_data='collection'+'|'+str(tg_from_id)+'|'+str(subject_id)+'|'+str(anime_search_keywords)+'|'+str(start)+'|'+'on_hold'), telebot.types.InlineKeyboardButton(text='抛弃',callback_data='collection'+'|'+str(tg_from_id)+'|'+str(subject_id)+'|'+str(anime_search_keywords)+'|'+str(start)+'|'+'dropped'))
            if call.message.content_type == 'photo':
                bot.edit_message_caption(caption=text, chat_id=call.message.chat.id , message_id=call.message.message_id, parse_mode='Markdown', reply_markup=markup)
            else:
                bot.edit_message_text(text=text, parse_mode='Markdown', chat_id=call.message.chat.id , message_id=call.message.message_id, reply_markup=markup)
    if status == 'wish':    # 想看
        if tg_from_id == test_id:
            rating = str(user_rating_get(test_id, subject_id)['user_rating'])
            collection_post(test_id, subject_id, status, rating)
            bot.send_message(chat_id=call.message.chat.id, text='已将 “`'+ subject_info_get(subject_id)['name'] +'`” 收藏更改为想看', parse_mode='Markdown', timeout=20)
        else:
            bot.answer_callback_query(call.id, text='和你没关系，别点了~', show_alert=True)
    if status == 'collect': # 看过
        if tg_from_id == test_id:
            rating = str(user_rating_get(test_id, subject_id)['user_rating'])
            collection_post(test_id, subject_id, status, rating)
            bot.send_message(chat_id=call.message.chat.id, text='已将 “`'+ subject_info_get(subject_id)['name'] +'`” 收藏更改为看过', parse_mode='Markdown', timeout=20)
        else:
            bot.answer_callback_query(call.id, text='和你没关系，别点了~', show_alert=True)
    if status == 'do':      # 在看
        if tg_from_id == test_id:
            rating = str(user_rating_get(test_id, subject_id)['user_rating'])
            collection_post(test_id, subject_id, status, rating)
            bot.send_message(chat_id=call.message.chat.id, text='已将 “`'+ subject_info_get(subject_id)['name'] +'`” 收藏更改为在看', parse_mode='Markdown', timeout=20)
        else:
            bot.answer_callback_query(call.id, text='和你没关系，别点了~', show_alert=True)
    if status == 'on_hold': # 搁置
        if tg_from_id == test_id:
            rating = str(user_rating_get(test_id, subject_id)['user_rating'])
            collection_post(test_id, subject_id, status, rating)
            bot.send_message(chat_id=call.message.chat.id, text='已将 “`'+ subject_info_get(subject_id)['name'] +'`” 收藏更改为搁置', parse_mode='Markdown', timeout=20)
        else:
            bot.answer_callback_query(call.id, text='和你没关系，别点了~', show_alert=True)
    if status == 'dropped': # 抛弃
        if tg_from_id == test_id:
            rating = str(user_rating_get(test_id, subject_id)['user_rating'])
            collection_post(test_id, subject_id, status, rating)
            bot.send_message(chat_id=call.message.chat.id, text='已将 “`'+ subject_info_get(subject_id)['name'] +'`” 收藏更改为抛弃', parse_mode='Markdown', timeout=20)
        else:
            bot.answer_callback_query(call.id, text='和你没关系，别点了~', show_alert=True)

# week 返回
@bot.callback_query_handler(func=lambda call: call.data.split('|')[0] == 'back_week')
def back_week_callback(call):
    day = int(call.data.split('|')[1])
    text = week_text(day)['text']
    markup = week_text(day)['markup']
    bot.delete_message(chat_id=call.message.chat.id , message_id=call.message.message_id, timeout=20)
    bot.send_message(chat_id=call.message.chat.id, text=text, parse_mode='Markdown', reply_markup=markup, timeout=20)

# 开始启动
if __name__ == '__main__':
    bot.polling()