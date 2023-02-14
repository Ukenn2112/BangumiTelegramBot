import asyncio
import logging

import telebot

from apiserver import start_api, stop_api
from tgbot import start_bot
from utils.config_vars import LOG_LEVEL, sql

telebot.logger.setLevel(LOG_LEVEL.upper())
logging.getLogger().setLevel(LOG_LEVEL.upper())
logging.basicConfig(
    format="[%(levelname)s]%(asctime)s: %(message)s",
    handlers=[
        logging.FileHandler("data/run.log", encoding="UTF-8"),
        logging.StreamHandler(),
    ],
)

if __name__ == '__main__':
    sql.create_users_db()
    sql.create_subscribe_db()
    try:
        start_api()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        stop_api()
        loop.close()
        sql.close()