import json
import uuid

from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from utils.user_token import bgm_user_data
from utils.config_vars import API_SETVER_URL, BOT_USERNAME, bgm, redis, sql

from .help import send_help
from .model import RequestSession, SubjectRequest, consumption_request


async def send_start(message: Message, bot: AsyncTeleBot):
    msg_data = message.text.split(" ")
    if len(msg_data) > 1 and msg_data[1].startswith("addsub"):
        sub_data = msg_data[1].lstrip("addsub").split('user')
        if len(sub_data) < 2: return
        subject_id, bgm_id = sub_data[0], sub_data[1]
        if not subject_id.isdigit() or not bgm_id.isdigit(): return
        if sql.check_subscribe(int(subject_id), message.from_user.id):
            return await bot.reply_to(message, "你已经订阅过这个番剧了哦～")
        else:
            sql.insert_subscribe_data(message.from_user.id, int(bgm_id), int(subject_id))
            subject_info = await bgm.get_subject(subject_id)
            text = (f"\\[*#订阅成功*]\n\n"
                    f"*{subject_info['name_cn'] or subject_info['name']}*\n\n"
                    f"*➤ 放送星期：*`{subject_info['_air_weekday']}`\n")
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton(text="取消订阅", callback_data=f"unaddsub|{subject_id}"),
                InlineKeyboardButton(text="查看详情", url=f"t.me/{BOT_USERNAME}?start={subject_id}")
            )
            return await bot.reply_to(message, text, reply_markup=markup)
    elif len(msg_data) > 1 and msg_data[1] == "help":
        return await send_help(message, bot)
    user_data = await bgm_user_data(message.from_user.id)
    if user_data and len(msg_data) > 1 and msg_data[1].isdecimal():
        msg = await bot.reply_to(message, "正在获取番剧信息...")
        session = RequestSession(uuid.uuid4().hex, message, user_data)
        subject_request = SubjectRequest(session, msg_data[1], is_root=True)
        session.stack = [subject_request]
        session.bot_message = msg
        return await consumption_request(bot, session)
    elif user_data:
        return await bot.reply_to(message, "您已绑定，快开始使用吧～")
    else:
        state = uuid.uuid4().hex
        params = {
            "tg_id": message.from_user.id,
            "param": msg_data[1] if len(msg_data) > 1 else "None"
            }
        redis.set("oauth:" + state, json.dumps(params), ex=3600)
        markup = InlineKeyboardMarkup()
        if "https://" in API_SETVER_URL:
            markup.add(InlineKeyboardButton(text="登录绑定 Bangumi", web_app=WebAppInfo(url=f"{API_SETVER_URL}/web_index?state={state}")))
        markup.add(InlineKeyboardButton(text="授权绑定 Bangumi", url=f"{API_SETVER_URL}/oauth_index?state={state}"))
        return await bot.reply_to(message, "*欢迎使用 BangumiTelegrBot，现在开始绑定您的 Bangumi 账号吧～*", reply_markup=markup)