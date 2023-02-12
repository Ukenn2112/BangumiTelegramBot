import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
import re
from urllib import parse as url_parse

from flask import Flask, jsonify, redirect, render_template, request
from waitress import serve

from utils.config_vars import (BOT_USERNAME, CALLBACK_URL, bgm, config, redis,
                               sql)

# 异步线程池
executor = ThreadPoolExecutor()

app = Flask(__name__)
app.config ["JSON_SORT_KEYS"] = False
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

# 错误访问
@app.route("/")
def index():
    return render_template("error.html")  # 发生错误


@app.route("/health")
def health():
    return "OK"  # 健康检查


@app.route("/oauth_index")
def oauth_index():
    try:
        state = request.args.get("state")
        if not state: return render_template("error.html")
        redis_data = redis.get("oauth:" + state)
        if not redis_data: return render_template("error.html")
        params = json.loads(redis_data)
        check = sql.inquiry_user_data(params["tg_id"])
        if not check: return render_template("verified.html")
        USER_AUTH_URL = "https://bgm.tv/oauth/authorize?" + url_parse.urlencode(
                {
                    "client_id": config["BGM"]["APP_ID"],
                    "response_type": "code",
                    "redirect_uri": CALLBACK_URL,
                    "state": state,
                }
            )
        return redirect(USER_AUTH_URL)
    except Exception as e:
        logging.error(f"[E] oauth_index: {e}")
        return render_template("error.html")


@app.route("/oauth_callback")
def oauth_callback():
    try:
        code, state = request.args.get("code"), request.args.get("state")
        if not code or not state: return render_template("error.html")
        redis_data = redis.get("oauth:" + state)
        if not redis_data: return render_template("expired.html")
        params = json.loads(redis_data)
        back_oauth = asyncio.run(bgm.oauth_authorization_code(code))
        sql.insert_user_data(params["tg_id"], back_oauth["user_id"], back_oauth["access_token"], back_oauth["refresh_token"])
        return redirect(f"https://t.me/{BOT_USERNAME}?start={params['param']}")
    except Exception as e:
        logging.error(f"[E] oauth_callback: {e}")
        return render_template("error.html")


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
        logging.debug(f'[W] before: 拦截到非法请求 {request.remote_addr} -> {url}')
        fuck = {'code': 200, 'message': 'Fack you mather!'}
        return jsonify(fuck), 200
    elif request.headers.get('Content-Auth') != config['API_SERVER']['AUTH_KEY']:
        logging.debug(f'[W] before: 拦截访问 {request.remote_addr} -> {url}')
        resu = {'code': 403, 'message': '你没有访问权限！'}
        return jsonify(resu), 200
    else:
        pass


def start_flask():
    serve(app, port=config["API_SERVER"]["POST"])


def start_api():
    executor.submit(start_flask)


def stop_api():
    executor.shutdown(wait=False)