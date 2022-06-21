"""
创建一个应用程序 https://bgm.tv/dev/app/create
Bangumi OAuth 用户授权机制文档 https://github.com/bangumi/api/blob/master/docs-raw/How-to-Auth.md

"""
import datetime
import json.decoder
import pathlib
import sqlite3
from os import path
import threading
import time

from urllib import parse as url_parse

import redis
import requests
from flask import Flask, jsonify, redirect, request, render_template

from config import (
    APP_ID,
    APP_SECRET,
    WEBSITE_BASE,
    BOT_USERNAME,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_DATABASE,
)
from utils.api import create_sql, get_subject_info, sub_repeat, sub_unadd, sub_user_list

import config
if 'OAUTH_POST' in dir(config):
    OAUTH_POST = config.OAUTH_POST
else:
    OAUTH_POST = 6008

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
        redis_data = redis_cli.get("oauth:" + state)
        if not redis_data:
            return render_template('expired.html')
        params = json.loads(redis_data)
        if 'tg_id' not in params or not params['tg_id']:
            return render_template('error.html')  # 发生错误
        tg_id = params['tg_id']

        data = sql_con.execute(f"select * from user where tg_id={tg_id}").fetchone()
        if data is not None:
            return render_template('verified.html')  # 发生错误

        USER_AUTH_URL = 'https://bgm.tv/oauth/authorize?' + url_parse.urlencode(
            {
                'client_id': APP_ID,
                'response_type': 'code',
                'redirect_uri': CALLBACK_URL,
                'state': state,
            }
        )
    except Exception:
        return render_template('error.html')
    return redirect(USER_AUTH_URL)


# code 换取 Access Token
@app.route('/oauth_callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not code or not state:
        return render_template('error.html')  # 发生错误
    json_str = redis_cli.get("oauth:" + state)
    if not json_str:
        return render_template('expired.html')  # 发生错误
    try:
        params = json.loads(json_str)
    except Exception:
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

# 查询/取消订阅 API
@app.route('/sub', methods=['get', 'post'])
def sub():
    type = request.values.get('type')
    subject_id = request.values.get('subject_id')
    user_id = request.values.get('user_id')
    if type and subject_id and user_id:
        if int(type) == 1:
            if sub_repeat(None, subject_id, user_id):
                return {'status': 1}, 200
            else:
                return {'status': 0}, 200
        elif int(type) == 2:
            if sub_repeat(None, subject_id, user_id):
                sub_unadd(None, subject_id, user_id)
                resu = {'code': 200, 'message': '已取消订阅'}
                return json.dumps(resu, ensure_ascii=False), 200
            else:
                resu = {'code': 401, 'message': '该用户未订阅此条目'}
                return json.dumps(resu, ensure_ascii=False), 401
    else:
        resu = {'code': 400, 'message': '参数不能为空！'}
        return json.dumps(resu, ensure_ascii=False), 400


# 推送 API
@app.route('/push', methods=['get', 'post'])
def push():
    subject_id = request.values.get('subject_id')
    video_id = request.values.get('video_id')
    ep = request.values.get('ep')
    image = request.values.get('image')
    if subject_id and video_id:
        userss = sub_user_list(subject_id)
        if userss:
            subject_info = get_subject_info(subject_id)
            text = (
                f'*🌸 #{subject_info["name_cn"] or subject_info["name"]} [*[{ep}]({image})*] 更新咯～*\n\n'
                f'[>>🍿 前往观看](https://bangumi.online/watch/{video_id}?s=bgmbot)\n'
            )
            from bot import bot, telebot
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(
                telebot.types.InlineKeyboardButton(text='取消订阅', callback_data=f'unaddsub|{subject_id}'),
                telebot.types.InlineKeyboardButton(text='查看详情', url=f"t.me/{BOT_USERNAME}?start={subject_id}")
            )
        lock.acquire() # 线程加锁
        s = 0 # 成功计数器
        us = 0 # 不成功计数器
        for users in userss:
            for user in users:
                try:
                    bot.send_message(chat_id=user, text=text, parse_mode="Markdown", reply_markup=markup)
                    s += 1
                except:
                    us += 1
            if len(userss) > 1:
                time.sleep(1)
        resu = {'code': 200, 'message': f'推送:成功 {s} 失败 {us}'}
        lock.release() # 线程解锁
        return json.dumps(resu, ensure_ascii=False), 200
    else:
        resu = {'code': 400, 'message': '参数不能为空！'}
        return json.dumps(resu, ensure_ascii=False), 400


if __name__ == '__main__':
    create_sql()
    app.run('0.0.0.0', OAUTH_POST)
