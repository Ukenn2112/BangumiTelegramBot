"""
创建一个应用程序 https://bgm.tv/dev/app/create
Bangumi OAuth 用户授权机制文档 https://github.com/bangumi/api/blob/master/docs-raw/How-to-Auth.md

"""
import datetime
import json.decoder
import pathlib
import sqlite3
from os import path
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
from utils.api import create_sql

CALLBACK_URL = f'{WEBSITE_BASE}oauth_callback'

base_dir = pathlib.Path(path.dirname(__file__))

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

if __name__ == '__main__':
    create_sql()
    app.run('0.0.0.0', 6008)
