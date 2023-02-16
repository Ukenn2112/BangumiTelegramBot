import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from urllib import parse as url_parse

import requests.utils
from flask import Flask, jsonify, redirect, render_template, request, make_response
from waitress import serve

from utils.config_vars import CALLBACK_URL, bgm, config, redis, sql

# 异步线程池
executor = ThreadPoolExecutor()

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

# 错误访问
@app.route("/")
def index():
    return render_template("error.html")  # 发生错误


@app.route("/health")
def health():
    return "OK"  # 健康检查


@app.route("/web_index")
def web_index():
    try:
        state = request.args.get("state")
        if not state: return render_template("error.html")
        redis_data = redis.get("oauth:" + state)
        if not redis_data: return render_template("expired.html")
        params = json.loads(redis_data)
        check = sql.inquiry_user_data(params["tg_id"])
        if check: return render_template("verified.html")
        b64_captcha, cookie = bgm.web_authorization_captcha()
        cookie_dict: dict = requests.utils.dict_from_cookiejar(cookie)
        resp = make_response(render_template("webindex.html", b64_captcha=b64_captcha))
        resp.set_cookie("chii_sec_id", cookie_dict["chii_sec_id"])
        resp.set_cookie("chii_sid", cookie_dict["chii_sid"])
        return resp
    except Exception as e:
        logging.error(f"[E] web_index: {e}")
        return render_template("error.html")


@app.route("/web_login", methods=["POST"])
def web_login():
    try:
        cookie = request.headers.get("cookie")
        email, password = request.json.get("email"), request.json.get("password")
        captcha, state = request.json.get("captcha"), request.json.get("state")
        if not state or not cookie: return "缺少必要参数", 403
        redis_data = redis.get("oauth:" + state)
        if not redis_data: return "您的请求已过期，请重新私聊 Bot 并发送 /start", 403
        params = json.loads(redis_data)
        check = sql.inquiry_user_data(params["tg_id"])
        if check: return "你已验证成功，无需重复验证", 403
        back_check, back_data = bgm.web_authorization_login(cookie, email, password, captcha)
        if not back_check: return back_data, 400
        cookie_dict: dict = requests.utils.dict_from_cookiejar(back_data)
        cookie_str = cookie + "; " + "; ".join([f"{k}={v}" for k, v in cookie_dict.items()])
        code = bgm.web_authorization_oauth(cookie_str)
        if not code: return "Web 授权失败，请重试", 400
        back_oauth = bgm.oauth_authorization_code(code)
        sql.insert_user_data(params["tg_id"], back_oauth["user_id"], back_oauth["access_token"], back_oauth["refresh_token"], cookie_str)
        return jsonify({"BotUsername": config["BOT_USERNAME"], "Params": params["param"]}), 200
    except Exception as e:
        logging.error(f"[E] web_login: {e}")
        return "出错了，请重试", 403


@app.route("/oauth_index")
def oauth_index():
    try:
        state = request.args.get("state")
        if not state: return render_template("error.html")
        redis_data = redis.get("oauth:" + state)
        if not redis_data: return render_template("expired.html")
        params = json.loads(redis_data)
        check = sql.inquiry_user_data(params["tg_id"])
        if check: return render_template("verified.html")
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
        back_oauth = bgm.oauth_authorization_code(code)
        sql.insert_user_data(params["tg_id"], back_oauth["user_id"], back_oauth["access_token"], back_oauth["refresh_token"])
        redis.delete("oauth:" + state)
        return redirect(f"https://t.me/{config['BOT_USERNAME']}?start={params['param']}")
    except Exception as e:
        logging.error(f"[E] oauth_callback: {e}")
        return render_template("error.html")


@app.before_request
def before():
    """中间件拦截器"""
    url = request.path  # 读取到当前接口的地址
    if url in ["/health", "/oauth_index", "/oauth_callback", "/web_index", "/web_login"]:
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