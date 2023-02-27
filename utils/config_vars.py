import yaml
from redis import Redis

from .api import BangumiAPI
from .sqlite_orm import SQLite

# 配置
with open('data/config.yaml', 'r') as f:
    config: dict = yaml.safe_load(f)

# API 服务器地址
API_SETVER_URL = f"{config['API_SERVER']['WEBSITE_BASE']}"
CALLBACK_URL = f"{API_SETVER_URL}/oauth_callback"

BOT_USERNAME = config["BOT_USERNAME"]

LOG_LEVEL = config["LOG_LEVEL"]

# bgm.tv API
bgm = BangumiAPI(
    config["BGM"]["APP_ID"],
    config["BGM"]["APP_SECRET"],
    CALLBACK_URL,
    config["BGM"]["ACCESS_TOKEN"])

# 数据库
sql = SQLite()

redis = Redis(
    host=config['REDIS']['HOST'],
    port=config['REDIS']['PORT'],
    db=config['REDIS']['REDIS_DATABASE'])