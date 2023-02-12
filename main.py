import asyncio
import logging

import telebot

from apiserver import start_api, stop_api
from tgbot import bot_register
from utils.config_vars import bot, config, sql

telebot.logger.setLevel(config["LOG_LEVEL"].upper())
logging.getLogger().setLevel(config["LOG_LEVEL"].upper())
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
    bot_register(bot)
    try:
        logging.info("Bot started.")
        start_api()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(bot.polling(non_stop=True))
    except KeyboardInterrupt:
        logging.info("Bot stopped.")
        stop_api()
        loop.close()
        sql.close()