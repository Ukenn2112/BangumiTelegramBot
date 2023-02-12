import json
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from urllib import parse as url_parse

from flask import Flask, jsonify, redirect, render_template, request
from waitress import serve

from utils.config_vars import CALLBACK_URL, config, redis, sql, bgm, BOT_USERNAME

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
        if "tg_id" not in params: return render_template("error.html")
        elif not params["tg_id"]: return render_template("error.html")
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
        if "tg_id" not in params: return render_template("error.html")
        elif not params["tg_id"]: return render_template("error.html")
        back_oauth = asyncio.run(bgm.oauth_authorization_code(code))
        sql.insert_user_data(params["tg_id"], back_oauth["user_id"], back_oauth["access_token"], back_oauth["refresh_token"])
        param = params["param"] if "param" in params else "None"
        return redirect(f"https://t.me/{BOT_USERNAME}?start={param}")
    except Exception as e:
        logging.error(f"[E] oauth_callback: {e}")
        return render_template("error.html")


def start_flask():
    serve(app, port=config["API_SERVER"]["POST"])


def start_api():
    executor.submit(start_flask)


def stop_api():
    executor.shutdown(wait=False)