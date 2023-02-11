import yaml
from telebot.async_telebot import AsyncTeleBot

from .api import BangumiAPI
from .sqlite_orm import SQLite

# 配置
with open('data/config.yaml', 'r') as f:
    config: dict = yaml.safe_load(f)

# 创建 TeleBot 实例
bot = AsyncTeleBot(config["BOT_TOKEN"], parse_mode='Markdown')

# bgm.tv API
bgm = BangumiAPI(
    config["BGM"]["APP_ID"],
    config["BGM"]["APP_SECRET"],
    f"{config['API_SERVER']['WEBSITE_BASE']}:{config['API_SERVER']['POST']}")

# 数据库
sql = SQLite()