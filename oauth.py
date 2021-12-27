"""
创建一个应用程序 https://bgm.tv/dev/app/create
Bangumi OAuth 用户授权机制文档 https://github.com/bangumi/api/blob/master/docs-raw/How-to-Auth.md

"""
import json.decoder
import pathlib
import datetime
from os import path
from urllib import parse as url_parse

import requests
from flask import Flask, jsonify, redirect, request, render_template

from config import APP_ID, APP_SECRET, WEBSITE_BASE


CALLBACK_URL = f'{WEBSITE_BASE}oauth_callback'

base_dir = pathlib.Path(path.dirname(__file__))

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# 错误访问
@app.route('/')
def index():
    return render_template('error.html') # 发生错误

# 获取code
@app.route('/oauth_index')
def oauth_index():
    tg_user_id = request.args.get('tg_id')
    if not tg_user_id:
        return render_template('error.html') # 发生错误
    with open('bgm_data.json') as f:
        data_seek = json.loads(f.read())
    data_li = [i['tg_user_id'] for i in data_seek]
    if int(tg_user_id) in data_li:
        return render_template('verified.html') # 发生错误
    USER_AUTH_URL = 'https://bgm.tv/oauth/authorize?' + url_parse.urlencode({
    'client_id': APP_ID,
    'response_type': 'code',
    'redirect_uri': CALLBACK_URL,
    'state': tg_user_id,
    })
    return redirect(USER_AUTH_URL)

# code 换取 Access Token
@app.route('/oauth_callback')
def oauth_callback():
    code = request.args.get('code')
    state = request.args.get('state')
    if not code and state:
        return render_template('error.html') # 发生错误
    resp = requests.post(
        'https://bgm.tv/oauth/access_token',
        data={
            'grant_type': 'authorization_code',
            'client_id': APP_ID,
            'client_secret': APP_SECRET,
            'code': code,
            'redirect_uri': CALLBACK_URL,
        },
        headers = {
        "User-Agent": "",
        }
    )
    try:
        r = resp.json()
        if 'error' in r:
            return jsonify(r)
    except json.decoder.JSONDecodeError:
        return render_template('error.html') # 发生错误
    # 写入json
    with open("bgm_data.json", 'r+', encoding='utf-8') as f:    # 打开文件
        try:
            data = json.load(f)                                 # 读取
        except:
            data = []                                           # 空文件
        expiry_time = (datetime.datetime.now()+datetime.timedelta(days=7)).strftime("%Y%m%d") # 加7天得到过期时间
        data.append({'tg_user_id': int(state), 'data': r, 'expiry_time': expiry_time})
        f.seek(0, 0)
        json.dump(data, f, ensure_ascii=False, indent=4)

    return redirect('https://t.me/BangumiBot?start=none')

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
    app.run('0.0.0.0', 6008)
