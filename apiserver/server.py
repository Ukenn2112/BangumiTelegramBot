from concurrent.futures import ThreadPoolExecutor

from flask import Flask, jsonify, render_template, request
from waitress import serve

from utils.config_vars import config

# 异步线程池
executor = ThreadPoolExecutor()

app = Flask(__name__)
app.config ['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# 错误访问
@app.route('/')
def index():
    return render_template("error.html")  # 发生错误

@app.route('/health')
def health():
    return 'OK'  # 健康检查

def start_flask():
    serve(app, port=config["API_SERVER"]["POST"])


def start_api():
    executor.submit(start_flask)


def stop_api():
    executor.shutdown(wait=False)