"""
创建一个应用程序 https://bgm.tv/dev/app/create
Bangumi OAuth 用户授权机制文档 https://github.com/bangumi/api/blob/master/docs-raw/How-to-Auth.md

"""
import datetime
import json.decoder
import pathlib
import re
import sqlite3
import threading
import time
from os import path
from urllib import parse as url_parse

import redis
import requests
from requests.adapters import HTTPAdapter
from flask import Flask, jsonify, redirect, render_template, request
from more_itertools import chunked
from waitress import serve

import config
from config import (APP_ID, APP_SECRET, AUTH_KEY, BOT_USERNAME, REDIS_DATABASE,
                    REDIS_HOST, REDIS_PORT, WEBSITE_BASE)
from utils.api import (create_sql, get_subject_info, sub_repeat, sub_unadd,
                       sub_user_list)

if 'OAUTH_POST' in dir(config):
    OAUTH_POST = config.OAUTH_POST
else:
    OAUTH_POST = 6008

import logging

logging.getLogger().setLevel(logging.INFO)

logging.basicConfig(
    format='%(asctime)s %(message)s',
    handlers=[
        logging.FileHandler("data/oauth.log", encoding="UTF-8"),
        logging.StreamHandler(),
    ],
)

CALLBACK_URL = f'{WEBSITE_BASE}oauth_callback'

base_dir = pathlib.Path(path.dirname(__file__))

lock = threading.RLock()

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
redis_cli = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DATABASE)
sql_con = sqlite3.connect(
    "data/bot.db",
    check_same_thread=False,
    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
)


# 错误访问
@app.route('/')
def index():
    return render_template('error.html')  # 发生错误


@app.route('/health')
def health():
    return 'OK'  # 健康检查


# 获取code
@app.route('/oauth_index')
def oauth_index():
    try:
        state = request.args.get('state')
        if not state:
            logging.error(f"[E] oauth_index: 缺少参数 {state}")
            return render_template('error.html') # 发生错误
        redis_data = redis_cli.get("oauth:" + state)
        if not redis_data:
            logging.error(f"[E] oauth_index: 请求过期 {state}")
            return render_template('expired.html')
        params = json.loads(redis_data)
        if 'tg_id' not in params or not params['tg_id']:
            logging.error(f"[E] oauth_index: 读取缓存库出错 {params}")
            return render_template('error.html')  # 发生错误
        tg_id = params['tg_id']

        data = sql_con.execute(f"select * from user where tg_id={tg_id}").fetchone()
        if data is not None:
            logging.info(f"[I] oauth_index: {tg_id} 已经绑定")
            return render_template('verified.html') # 已经绑定

        USER_AUTH_URL = 'https://bgm.tv/oauth/authorize?' + url_parse.urlencode(
            {
                'client_id': APP_ID,
                'response_type': 'code',
                'redirect_uri': CALLBACK_URL,
                'state': state,
            }
        )
    except Exception as e:
        logging.error(f"[E] oauth_index: {e}")
        return render_template('error.html') # 发生错误
    return redirect(USER_AUTH_URL)


# code 换取 Access Token
@app.route('/oauth_callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not code or not state:
        logging.error(f"[E] oauth_callback: 缺少参数 {code} {state}")
        return render_template('error.html')  # 发生错误
    json_str = redis_cli.get("oauth:" + state)
    if not json_str:
        logging.error(f"[E] oauth_callback: 请求过期 {state}")
        return render_template('expired.html')  # 发生错误
    try:
        params = json.loads(json_str)
    except Exception as e:
        logging.error(f"[E] oauth_callback: 读取缓存库出错 {e}")
        return render_template('error.html')
    resp = requests.post(
        'https://bgm.tv/oauth/access_token',
        data={
            'grant_type': 'authorization_code',
            'client_id': APP_ID,
            'client_secret': APP_SECRET,
            'code': code,
            'redirect_uri': CALLBACK_URL,
        },
        headers={
            "User-Agent": "",
        },
    )
    try:
        r = resp.json()
        if 'error' in r:
            return jsonify(r)
    except json.decoder.JSONDecodeError:
        logging.error(f"[E] oauth_callback: 换取 access_token 出错 {r}")
        return render_template('error.html')  # 发生错误
    tg_id = int(params['tg_id'])
    bgm_id = r['user_id']
    access_token = r['access_token']
    refresh_token = r['refresh_token']
    cookie = None
    expiry_time = (datetime.datetime.now() + datetime.timedelta(days=7)).timestamp() // 1000
    sql_con.execute(
        "insert into user(tg_id,bgm_id,access_token,refresh_token,cookie,expiry_time,create_time) "
        "values(?,?,?,?,?,?,?)",
        (
            tg_id,
            bgm_id,
            access_token,
            refresh_token,
            cookie,
            expiry_time,
            datetime.datetime.now().timestamp() // 1000,
        ),
    )
    sql_con.commit()
    param = "None"
    if 'param' in params:
        param = params['param']
    return redirect(f'https://t.me/{BOT_USERNAME}?start={param}')


'''
{
  "access_token": "xxxxxxxxxxxxxxxx", api请求密钥
  "expires_in": 604800, 有效期7天
  "refresh_token": "xxxxxxxxxxxxxxxxxxx",  续期密钥
  "scope": null,
  "token_type": "Bearer",
  "user_id": xxxxxx  bgm用户uid
}
'''

## 以下为联动 Bangumi.online 的 API

# 查询/取消订阅 API
@app.route('/sub', methods=['get', 'post'])
def sub():
    type = request.values.get('type')
    subject_id = request.values.get('subject_id')
    user_id = request.values.get('user_id')
    if type and subject_id and user_id:
        if int(type) == 1:
            if sub_repeat(None, subject_id, user_id):
                logging.info(f"[I] sub: 查询 用户 {user_id} 已订阅 {subject_id}")
                return {'status': 1}, 200
            else:
                logging.info(f"[I] sub: 查询 用户 {user_id} 未订阅 {subject_id}")
                return {'status': 0}, 200
        elif int(type) == 2:
            if sub_repeat(None, subject_id, user_id):
                sub_unadd(None, subject_id, user_id)
                logging.info(f'[I] sub: 用户 {user_id} 取消订阅 {subject_id}')
                resu = {'code': 200, 'message': '已取消订阅'}
                return jsonify(resu), 200
            else:
                logging.error(f'[E] sub: 用户 {user_id} 未订阅过 {subject_id}')
                resu = {'code': 401, 'message': '该用户未订阅此条目'}
                return jsonify(resu), 401
    else:
        logging.error(f"[E] sub: 缺少参数 {type} {subject_id} {user_id}")
        resu = {'code': 400, 'message': '参数不能为空！'}
        return jsonify(resu), 400


# 推送 API
@app.route('/push', methods=['get', 'post'])
def push():
    import telebot
    logging.info(f'[I] push: 收到推送请求 {request.full_path}')
    video_id = request.values.get('video_id')
    subject_id = None
    if video_id:
        s = requests.Session()
        s.mount('https://', HTTPAdapter(max_retries=3))
        r = s.post('https://api.bangumi.online/bgm/subject', data={'vid': video_id}, timeout=10).json()
        if r['code'] == 10000:
            subject_id = r['data']['season']['bgm_id']
            subject_info = r['season']['title']
            volume = r['data']['episode']['volume']
    if subject_id and video_id:
        sub_users = sub_user_list(subject_id)
        if sub_users:
            text = (
                f'*🌸 #{subject_info["zh"] or subject_info["ja"]} [*[{volume}](https://cover.bangumi.online/episode/{video_id}.png)*] 更新咯～*\n\n'
                f'[>>🍿 前往观看](https://bangumi.online/watch/{video_id}?s=bgmbot)\n'
            )
            bot = telebot.TeleBot(config.BOT_TOKEN)
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(
                telebot.types.InlineKeyboardButton(text='取消订阅', callback_data=f'unaddsub|{subject_id}'),
                telebot.types.InlineKeyboardButton(text='查看详情', url=f"t.me/{BOT_USERNAME}?start={subject_id}")
            )
        else:
            logging.info(f'[I] push: {subject_id} 无订阅用户')
            resu = {'code': 200, 'message': f'{subject_id} 无订阅用户'}
            return jsonify(resu), 200
        lock.acquire() # 线程加锁
        s = 0 # 成功计数器
        us = 0 # 不成功计数器
        for users in chunked(sub_users, 30):
            for user in users:
                try:
                    bot.send_message(chat_id=user, text=text, parse_mode="Markdown", reply_markup=markup)
                    s += 1
                except: us += 1
            if len(sub_users) > 30:
                time.sleep(1)
        logging.info(f'[I] push: 推送成功 {s} 条，失败 {us} 条')
        resu = {'code': 200, 'message': f'推送:成功 {s} 失败 {us}'}
        lock.release() # 线程解锁
        return jsonify(resu), 200
    else:
        logging.error(f'[E] push: 缺少参数 {subject_id} {video_id}')
        resu = {'code': 400, 'message': '参数不能为空！'}
        return jsonify(resu), 400


@app.before_request
def before():
    """中间件拦截器"""
    url = request.path  # 读取到当前接口的地址
    if url == '/health':
        pass
    elif url == '/oauth_index':
        pass
    elif url == '/oauth_callback':
        pass
    elif re.findall(r'pma|db|mysql|phpMyAdmin|.env|php|admin|config|setup', url):
        logging.warning(f'[W] before: 拦截到非法请求 {request.remote_addr} -> {url}')
        fuck = {'code': 200, 'message': 'Fack you mather!'}
        return jsonify(fuck), 200
    elif request.headers.get('Content-Auth') != AUTH_KEY:
        logging.warning(f'[W] before: 拦截访问 {request.remote_addr} -> {url}')
        resu = {'code': 403, 'message': '你没有访问权限！'}
        return jsonify(resu), 200
    else:
        pass

if __name__ == '__main__':
    create_sql()
    serve(app, host="0.0.0.0", port=OAUTH_POST)
