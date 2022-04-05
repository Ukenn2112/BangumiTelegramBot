"""api 调用

https://bangumi.github.io/api/"""

import datetime
import json
import logging
import random
import sqlite3
import threading
import time
from threading import Thread
from typing import Optional, Literal, List
from urllib import parse

import redis
import requests
import schedule
from lxml import etree

from config import APP_ID, APP_SECRET, WEBSITE_BASE, REDIS_HOST, REDIS_PORT, REDIS_DATABASE
# FIXME 似乎不应该在这里创建对象
from model.exception import TokenExpired

redis_cli = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DATABASE)
sql_con = sqlite3.connect("bot.db", check_same_thread=False)


def create_sql():
    """创建数据库"""

    sql_con.execute(f"""create table if not exists
        user(
        id integer primary key AUTOINCREMENT,
        tg_id integer,
        bgm_id integer,
        access_token varchar(128),
        refresh_token varchar(128),
        cookie varchar(128),
        expiry_time timestamp,
        create_time timestamp,
        update_time timestamp)
        """)

    sql_con.execute(f"""create unique index if not exists tg_id_index on user (tg_id)""")


def data_seek_get(tg_id):
    """ 判断是否绑定Bangumi """
    data = sql_con.execute(f"select tg_id from user where tg_id=?", (tg_id,)).fetchone()
    return bool(data)


def user_data_delete(tg_id):
    sql_con.execute(f"delete from user where tg_id = ?", (tg_id,))
    sql_con.commit()


def user_data_get(tg_id):
    """ 返回用户数据,如果过期则更新 """
    data = sql_con.execute(
        f"select tg_id,bgm_id,access_token,cookie,expiry_time from user where tg_id=?", (tg_id,)).fetchone()
    if data is None:
        return None
    expiry_time = data[4]
    now_time = datetime.datetime.now().timestamp() // 1000
    if now_time >= expiry_time:  # 判断密钥是否过期
        expiry_data_get(tg_id)
        data = sql_con.execute(f"select bgm_id,access_token,cookie from user where tg_id=?", (tg_id,)).fetchone()
        return {"user_id": data[0], "access_token": data[1], 'cookie': data[2]}
    else:
        return {"user_id": data[1], "access_token": data[2], "cookie": data[3]}


def nsfw_token():
    """ 返回可以查看NSFW内容的token"""
    data = sql_con.execute("select access_token from user limit 1").fetchone()
    return data[0]


def expiry_data_get(tg_id):
    """更新过期用户数据"""
    cur = sql_con.cursor()
    refresh_token = cur.execute(
        f"select refresh_token from user where tg_id=?", (tg_id,)).fetchone()[0]
    callback_url = f'{WEBSITE_BASE}oauth_callback'
    resp = requests.post(
        'https://bgm.tv/oauth/access_token',
        data={
            'grant_type': 'refresh_token',
            'client_id': APP_ID,
            'client_secret': APP_SECRET,
            'refresh_token': refresh_token,
            'redirect_uri': callback_url,
        },
        headers={
            "User-Agent": "",
        }
    )
    access_token = json.loads(resp.text).get('access_token')  # 更新access_token
    refresh_token = json.loads(resp.text).get('refresh_token')  # 更新refresh_token
    expiry_time = (datetime.datetime.now() +
                   datetime.timedelta(days=7)).timestamp() // 1000  # 更新过期时间

    # 替换数据
    cur.execute(
        f"update user set access_token=?,refresh_token=?,expiry_time=?,update_time=? where tg_id=?",
        (access_token, refresh_token, expiry_time, datetime.datetime.now().timestamp() // 1000, tg_id,))
    sql_con.commit()


# 获取BGM用户信息 TODO 存入数据库
def bgmuser_data(test_id):
    user = user_data_get(test_id)
    access_token = user['access_token']
    url = f"https://api.bgm.tv/user/{user['user_id']}"
    user_data = requests_get(url, access_token=access_token)
    return user_data


@schedule.repeat(schedule.every().day.at("03:00"))
def check_expiry_user():
    """检查是否有过期用户"""
    data = sql_con.execute("select tg_id, expiry_time from user where ? > expiry_time",
                           (datetime.datetime.now().timestamp() // 1000,)).fetchall()
    for i in data:
        expiry_data_get(i[0])


def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    https://schedule.readthedocs.io/en/stable/background-execution.html
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                schedule.run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


def requests_get(url, params: Optional[dict] = None, access_token: Optional[str] = None, max_retry_times: int = 3):
    """requests_get 请求"""
    r = None
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'}
    if access_token is not None:
        headers.update({'Authorization': 'Bearer ' + access_token})
    for num in range(max_retry_times):  # 如api请求错误 重试3次
        try:
            r = requests.get(url=url, params=params, headers=headers)
            break
        except requests.ConnectionError as err:
            if num + 1 >= max_retry_times:
                raise
            else:
                logging.warning(f'api请求错误，重试中...{str(err)}')
    if r.status_code != 200:
        if r.status_code == 401:  # and "expired" in r.text:
            raise TokenExpired()
        raise requests.exceptions.BaseHTTPError(r.status_code)
    else:
        try:
            return json.loads(r.text)
        except json.JSONDecodeError:
            raise


# def eps_get(test_id, subject_id):
#     """获取用户观看eps数据"""
#     user_data = user_data_get(test_id)
#     access_token = user_data['access_token']
#     params = {
#         'subject_id': subject_id,
#         'type': 0}
#     url = 'https://api.bgm.tv/v0/episodes'
#     data_eps = requests_get(url, params, access_token)
#     epsid_li = [i['id'] for i in data_eps['data']]  # 所有eps_id
#
#     params = {'subject_id': subject_id}
#     url = f"https://api.bgm.tv/user/{user_data['user_id']}/progress"
#     data_watched = requests_get(url, params, access_token)
#     if data_watched is not None:
#         watched_id_li = [i['id'] for i in data_watched['eps']]  # 已观看 eps_id
#     else:
#         watched_id_li = [0]  # 无观看集数
#     eps_n = len(set(epsid_li))  # 总集数
#     watched_n = len(set(epsid_li) & set(watched_id_li))  # 已观看了集数
#     unwatched_id = epsid_li  # 去除已观看过集数的 eps_id
#     try:
#         for watched_li in watched_id_li:
#             unwatched_id.remove(watched_li)
#     except ValueError:
#         pass
#     # 输出
#     eps_data = {'progress': str(watched_n) + '/' + str(eps_n),  # 已观看/总集数 进度 str
#                 'watched': watched_n,  # 已观看集数 int
#                 'eps_n': str(eps_n),  # 总集数 str
#                 'unwatched_id': unwatched_id}  # 未观看 eps_di list
#     return eps_data


# 更新收视进度状态
# def eps_status_get(test_id, eps_id, status):
#     """更新收视进度状态"""
#     access_token = user_data_get(test_id).get('access_token')
#     url = f'https://api.bgm.tv/ep/{eps_id}/status/{status}'
#     return requests_get(url, access_token=access_token)


# 更新收视进度状态
def post_eps_status(tg_id: int, id_: int, status, ep_id: List[int] = None, access_token=None):
    """更新收视进度状态
    :param tg_id:Telegram 用户id
    :param id_: 章节 ID
    :param status:收视类型
    :param ep_id:使用 POST 批量更新 将章节以半角逗号分隔，如 3697,3698,3699。请求时 URL 中的 ep_id 为最后一个章节 ID
    :param access_token:
    :return:
    """

    if access_token is None:
        access_token = user_data_get(tg_id).get('access_token')
    url = f'https://api.bgm.tv/ep/{id_}/status/{status}'
    headers = {'Authorization': 'Bearer ' + access_token}

    params = None
    if ep_id:
        eps = ''
        for i in ep_id:
            eps += f'{i},'
        params = {'ep_id': eps[:-1]}
    return requests.post(url=url, headers=headers, data=params)


def post_collection(tg_id, subject_id, status: str, comment: str = None, tag: str = None, rating: str = None, privacy: int = None, access_token: str = None):
    r"""收藏管理  token 和 tg_id须传一个
    :param tg_id: Telegram 用户id
    :param subject_id: 条目 ID
    :param status: 收藏类型: wish = 想看 collect = 看过 do = 在看 on_hold = 搁置 dropped = 抛弃
    :param comment: 简评
    :param tag: 标签 多个以以半角空格分割
    :param rating: 评分 不填默认重置为未评分
    :param privacy: 收藏私密状态 0 = 公开 1 = 私密 不填默认为0
    :param access_token: 用户密钥"""
    if not access_token:
        access_token = user_data_get(tg_id).get('access_token')
    params = {"status": status}
    if comment:
        params["comment"] = comment
    if tag:
        params["tag"] = tag
    if rating:
        params["rating"] = rating
    if privacy:
        params["privacy"] = privacy
    headers = {'Authorization': f'Bearer {access_token}'}
    url = f'https://api.bgm.tv/collection/{subject_id}/update'
    return requests.post(url=url, data=params, headers=headers)


def user_collection_get(test_id, subject_id, access_token=None):
    """获取指定条目收藏信息"""
    if access_token is None:
        access_token = user_data_get(test_id).get('access_token')
    url = f'https://api.bgm.tv/collection/{subject_id}'
    return requests_get(url, access_token=access_token)


def get_user_progress(tg_id, subject_id):
    """用户收视进度 这接口废弃了 少用..."""
    userdata = user_data_get(tg_id)
    access_token = userdata.get('access_token')
    url = f'https://api.bgm.tv/user/{userdata["user_id"]}/progress'
    return requests_get(url=url, access_token=access_token, params={'subject_id': subject_id})


def get_calendar() -> dict:
    """获取每日放送动漫"""
    data = redis_cli.get("calendar")
    if data:
        return json.loads(data)
    else:
        calendar = requests_get(url='https://api.bgm.tv/calendar')
        redis_cli.set("calendar", json.dumps(calendar), ex=3600)
        return calendar


def get_subject_info(subject_id, t_dict=None):
    """获取指定条目信息 并使用Redis缓存"""
    subject = redis_cli.get(f"subject:{subject_id}")
    if subject:
        if subject == b"None__":
            raise FileNotFoundError(f"subject_id:{subject_id}获取失败_缓存")
        loads = json.loads(subject)
    else:
        url = f'https://api.bgm.tv/v0/subjects/{subject_id}'
        loads = requests_get(url=url, access_token=nsfw_token())
        if loads is None:
            redis_cli.set(f"subject:{subject_id}",
                          "None__", ex=60 * 10)  # 不存在时 防止缓存穿透
            raise FileNotFoundError(f"subject_id:{subject_id}获取失败")
        loads['_air_weekday'] = None
        for info in loads['infobox']:
            if info['key'] == '放送星期':
                loads['_air_weekday'] = info['value']  # 加一个下划线 用于区别
                break
        redis_cli.set(f"subject:{subject_id}", json.dumps(
            loads), ex=60 * 60 * 24 + random.randint(-3600, 3600))
    if t_dict:
        t_dict["subject_info"] = loads
    return loads


def get_person_info(person_id):
    """获取人物信息 并使用Redis缓存"""
    person_info = redis_cli.get(f"person_info:{person_id}")
    if person_info:
        if person_info == b"None__":
            raise FileNotFoundError(f"person_id:{person_id}获取人物信息失败_缓存")
        loads = json.loads(person_info)
    else:
        url = f'https://api.bgm.tv/v0/persons/{person_id}'
        loads = requests_get(url=url, access_token=nsfw_token())
        if loads is None:
            redis_cli.set(f"person_info:{person_id}",
                          "None__", ex=60 * 10)  # 不存在时 防止缓存穿透
            raise FileNotFoundError(f"person_id:{person_id}获取人物信息失败")
        redis_cli.set(f"person_info:{person_id}", json.dumps(
            loads), ex=60 * 60 * 24 * 7 + random.randint(-3600, 3600))
    return loads


def get_subject_characters(subject_id):
    """获取指定条目角色信息 并使用Redis缓存"""
    subject_characters = redis_cli.get(f"subject_characters:{subject_id}")
    if subject_characters:
        if subject_characters == b"None__":
            raise FileNotFoundError(f"subject_id:{subject_id}角色数据获取失败_缓存")
        loads = json.loads(subject_characters)
    else:
        url = f'https://api.bgm.tv/v0/subjects/{subject_id}/characters'
        loads = requests_get(url=url, access_token=nsfw_token())
        if loads is None:
            redis_cli.set(f"subject_characters:{subject_id}",
                          "None__", ex=60 * 10)  # 不存在时 防止缓存穿透
            raise FileNotFoundError(f"subject_id:{subject_id}角色数据获取失败")
        redis_cli.set(f"subject_characters:{subject_id}", json.dumps(
            loads), ex=60 * 60 * 24 + random.randint(-3600, 3600))
    return loads


def get_subject_relations(subject_id):
    """获取章节关联条目信息 并使用Redis缓存"""
    subject_relations = redis_cli.get(f"subject_relations:{subject_id}")
    if subject_relations:
        if subject_relations == b"None__":
            raise FileNotFoundError(f"subject_id:{subject_id}获取章节关联条目信息失败_缓存")
        loads = json.loads(subject_relations)
    else:
        url = f'https://api.bgm.tv/v0/subjects/{subject_id}/subjects'
        loads = requests_get(url=url, access_token=nsfw_token())
        if loads is None:
            redis_cli.set(f"subject_relations:{subject_id}",
                          "None__", ex=60 * 10)  # 不存在时 防止缓存穿透
            raise FileNotFoundError(f"subject_id:{subject_id}获取章节关联条目信息失败")
        redis_cli.set(f"subject_relations:{subject_id}", json.dumps(
            loads), ex=60 * 60 * 24 * 7 + random.randint(-3600, 3600))
    return loads


def get_person_related_subjects(person_id):
    """获取人物关联条目信息 并使用Redis缓存"""
    person_related_subjects = redis_cli.get(f"person_related_subjects:{person_id}")
    if person_related_subjects:
        if person_related_subjects == b"None__":
            raise FileNotFoundError(f"person_id:{person_id}获取人物关联条目信息失败_缓存")
        loads = json.loads(person_related_subjects)
    else:
        url = f'https://api.bgm.tv/v0/persons/{person_id}/subjects'
        loads = requests_get(url=url, access_token=nsfw_token())
        if loads is None:
            redis_cli.set(f"person_related_subjects:{person_id}",
                          "None__", ex=60 * 10)  # 不存在时 防止缓存穿透
            raise FileNotFoundError(f"person_id:{person_id}获取人物关联条目信息失败")
        redis_cli.set(f"person_related_subjects:{person_id}", json.dumps(
            loads), ex=60 * 60 * 24 * 7 + random.randint(-3600, 3600))
    return loads


def get_subject_episode(subject_id: int, type_: Literal[0, 1, 2, 3, None] = None, limit=100, offset=0):
    """获取条目章节

    :param subject_id:条目id
    :param type_: 0,1,2,3 代表 本篇，sp，op，ed
    :param limit: 每页数量
    :param offset: 偏移量
    """
    episode = redis_cli.get(f"subject_episode:{subject_id}:{type_}:{limit}:{offset}")
    if episode:
        if episode == b"None__":
            raise FileNotFoundError(f"subject_id:{subject_id}获取失败_缓存")
        loads = json.loads(episode)
    else:
        url = f'https://api.bgm.tv/v0/episodes'
        params = {
            'subject_id': subject_id,
            'type': type_,
            'limit': limit,
            'offset': offset
        }
        loads = requests_get(url=url, params=params, access_token=nsfw_token())
        Thread(target=cache_subject_episode, args=[limit, loads, offset, subject_id, type_])
    return loads


def cache_subject_episode(limit, loads, offset, subject_id, type_):
    if not loads:
        redis_cli.set(f"subject_episode:{subject_id}:{type_}:{limit}:{offset}",
                      "None__", ex=60 * 10)  # 不存在时 防止缓存穿透
        raise FileNotFoundError(f"subject_id:{subject_id}获取失败")
    redis_cli.set(f"subject_episode:{subject_id}:{type_}:{limit}:{offset}",
                  json.dumps(loads), ex=60 * 60 * 24 + random.randint(-3600, 3600))
    for eps in loads['eps']:
        eps['subject_id'] = int(subject_id)
        redis_cli.set(f"episode:{eps['id']}",
                      json.dumps(eps), ex=60 * 60 * 24 + random.randint(-3600, 3600))


def get_episode_info(episode_id: int):
    episode = redis_cli.get(f"episode:{episode_id}")
    if episode:
        if episode == b"None__":
            raise FileNotFoundError(f"episode_id:{episode_id}获取失败_缓存")
        loads = json.loads(episode)
    else:
        url = f'https://api.bgm.tv/v0/episodes/{episode_id}'
        loads = requests_get(url=url, access_token=nsfw_token())
        if loads is None:
            redis_cli.set(f"episode:{episode_id}",
                          "None__", ex=60 * 10)  # 不存在时 防止缓存穿透
            raise FileNotFoundError(f"subject_id:{episode_id}获取失败")
        redis_cli.set(f"episode:{episode_id}", json.dumps(
            loads), ex=60 * 60 * 24 + random.randint(-3600, 3600))
    return loads


def anime_img(subject_id):
    """动画简介图片获取 不需Access Token 并使用Redis缓存"""
    img_url = redis_cli.get(f"anime_img:{subject_id}")
    if img_url:
        if img_url == b"None__":
            return None
        return img_url.decode()
    subject_info = get_subject_info(subject_id)
    if subject_info['type'] != 2 and subject_info['type'] != 1 and 'images' in subject_info:
        img_url = None
        if 'large' in subject_info['images'] and subject_info['images']['large']:
            img_url = subject_info['images']['large']
        elif 'common' in subject_info['images'] and subject_info['images']['common']:
            img_url = subject_info['images']['common']
        elif 'medium' in subject_info['images'] and subject_info['images']['medium']:
            img_url = subject_info['images']['medium']
        if img_url:
            redis_cli.set(f"anime_img:{subject_id}", img_url,
                          ex=60 * 60 * 24 + random.randint(-3600, 3600))
            return img_url
    anime_name = get_subject_info(subject_id)['name']
    query = '''
    query ($id: Int, $page: Int, $perPage: Int, $search: String) {
        Page (page: $page, perPage: $perPage) {
            media (id: $id, search: $search) {
                id
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
    if len(anilist_data) > 0:
        img_url = f'https://img.anili.st/media/{anilist_data[0]["id"]}'
        redis_cli.set(f"anime_img:{subject_id}", img_url,
                      ex=60 * 60 * 24 + random.randint(-3600, 3600))
        return img_url
    else:
        if 'large' in subject_info['images'] and subject_info['images']['large']:
            img_url = subject_info['images']['large']
        elif 'common' in subject_info['images'] and subject_info['images']['common']:
            img_url = subject_info['images']['common']
        elif 'medium' in subject_info['images'] and subject_info['images']['medium']:
            img_url = subject_info['images']['medium']
        if img_url:
            redis_cli.set(f"anime_img:{subject_id}", img_url,
                          ex=60 * 60 * 24 + random.randint(-3600, 3600))
            return img_url
        else:
            redis_cli.set(f"anime_img:{subject_id}",
                          "None__", ex=60 * 10)  # 不存在时 防止缓存穿透
        return None


def search_subject(keywords: str,
                   type_: int = None,
                   response_group: str = 'small',
                   start: int = 0,
                   max_results: int = 25) -> dict:
    """搜索条目

    :param keywords: 关键词
    :param type_: 条目类型 1=book 2=anime 3=music 4=game 6=real
    :param response_group: 返回数据大小 small medium
    :param start: 开始条数
    :param max_results: 每页条数 最多 25
    """
    keywords = keywords.strip()
    data = redis_cli.get(f"subject_search:{keywords}:{type_}:{response_group}:{max_results}:{start}")
    if data:
        if data == b"None__":
            raise FileNotFoundError
        else:
            return json.loads(data)
    params = {"type": type_, "responseGroup": response_group,
              "start": start, "max_results": max_results}
    url = f'https://api.bgm.tv/search/subject/{keywords}'
    try:
        data = requests_get(url=url, params=params, access_token=nsfw_token())
    except:
        data = {"results": 0, 'list': []}
    redis_cli.set(f"subject_search:{keywords}:{type_}:{response_group}:{max_results}:{start}", json.dumps(data),
                  ex=3600 * 24)
    return data


def get_collection(subject_id: str, token: str = "", tg_id=""):
    """获取用户指吧定条目收藏信息 token 和tg_id须传一个"""
    if token == "":
        if tg_id == "":
            raise ValueError("参数错误,token 和tg_id须传一个")
        token = user_data_get(tg_id).get('access_token')
    if subject_id is None or subject_id == "":
        raise ValueError("subject_id不能为空")
    url = f"https://api.bgm.tv/collection/{subject_id}"
    return requests_get(url=url, access_token=token)


def get_user(bgm_id: str) -> dict:
    """通过bgm_id 获取用户名"""
    data = redis_cli.get(f"bgm_user:{bgm_id}")
    if data:
        if data == b"None__":
            raise FileNotFoundError
        else:
            return json.loads(data)
    user_data = requests_get(f'https://api.bgm.tv/user/{bgm_id}')
    if isinstance(user_data, dict) and user_data.get('code') == 404:
        redis_cli.set(f"bgm_user:{bgm_id}", "None__", ex=3600)
        raise FileNotFoundError
    else:
        redis_cli.set(f"bgm_user:{bgm_id}", json.dumps(
            user_data), ex=3600 * 24 * 7)
        return user_data


def post_eps_reply(tg_id, ep_id, reply_text):
    """章节评论"""
    cookie = user_data_get(tg_id).get('cookie')
    if cookie is None:
        raise RuntimeError("未添加Cookie")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36',
        'Cookie': cookie
    }
    result = requests.get(f'https://bgm.tv/ep/{ep_id}', headers=headers)
    html = etree.HTML(result.text.encode('utf-8'))
    formhash = html.xpath('//input[@name="formhash"]/@value')[0]
    lastview = html.xpath('//input[@name="lastview"]/@value')[0]
    reply_text += '\n[i]# 此消息由 [url=https://github.com/Ukenn2112/BangumiTelegramBot]BangumiTelegramBot[/url] 发送 [i](bgm24)'
    FormData = {
        'content': reply_text,
        'related_photo': 0,
        'formhash': formhash,
        'lastview': lastview,
        'submit': 'submit'
    }
    data = parse.urlencode(FormData)
    headers.update({'Content-Type': 'application/x-www-form-urlencoded'})
    return requests.post(f'https://bgm.tv/subject/ep/{ep_id}/new_reply', headers=headers, data=data)


def removesuffix(self: str, suffix: str, /) -> str:
    """ This method does the same as Python3.9:func:`builtins.str.removesuffix`"""
    if self.endswith(suffix):
        return self[:-len(suffix)]
    else:
        return self[:]


session = requests.session()


def get_mono_search(keywords: str, page: int = 1, cat: Literal['all', 'crt', 'prsn'] = 'all'):
    """搜索人物"""
    keywords = keywords.strip()
    data = redis_cli.get(f"mono_search:{keywords}:{cat}:{page}")
    if data:
        if data == b"None__":
            raise FileNotFoundError
        else:
            return json.loads(data)

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.46",
    }
    cookies = {"chii_searchDateLine": "0"}
    params = {'cat': cat}
    if page is not None:
        params['page'] = page
    r = session.get(f"http://bgm.tv/mono_search/{keywords}", headers=headers, cookies=cookies, params=params)
    html = etree.HTML(r.content)
    error = html.xpath('//*[@id="colunmNotice"]/div/p[1]')
    if error:
        data = {'error': error[0].text, 'list': []}
    else:
        rows = html.xpath('//*[@id="columnSearchB"]/div[@class="light_odd clearit"]')
        list = []

        for row in rows:
            a = row.xpath('div/h2/a')
            name = removesuffix(a[0].text, ' / ') if a else None
            b = row.xpath('div/h2/a/span')
            name_cn = b[0].text if b else None
            c = row.xpath('a/img')
            img_url = "https:" + c[0].get('src') if c and c[0].get('src') != '/img/info_only.png' else None
            d = row.xpath('div[2]/div/span')
            info = d[0].text.strip() if d else None
            e = row.xpath('a')
            id_ = None
            type_ = None
            if e:
                e = e[0].get('href')
                if e.startswith('/character/'):
                    type_ = "character"
                    id_ = int(e[11:])
                elif e.startswith('/person/'):
                    type_ = "person"
                    id_ = int(e[8:])
            list.append({'id': id_, 'type': type_, 'name': name, 'name_cn': name_cn, 'img_url': img_url, 'info': info})
        data = {'error': None, 'list': list}
    redis_cli.set(f"mono_search:{keywords}:{cat}:{page}", json.dumps(data), ex=3600 * 24)
    return data
