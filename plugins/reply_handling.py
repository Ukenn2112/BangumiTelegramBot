import re
import telebot

from utils.api import get_subject_info, post_collection, post_eps_reply, user_collection_get
from utils.converts import convert_telegram_message_to_bbcode, subject_type_to_emoji


def send(message, bot):
    if re.search(r'(EP ID： )([0-9]+)', str(message.reply_to_message.text), re.I | re.M):
        for i in re.findall(r'(EP ID： )([0-9]+)', message.reply_to_message.text, re.I | re.M):
            try:
                text = message.text
                text = convert_telegram_message_to_bbcode(text, message.entities)
                post_eps_reply(message.from_user.id, i[1], text)
            except:
                bot.send_message(message.chat.id,
                                "*发送评论失败\n(可能未添加 Cookie 或者 Cookie 已过期)* \n请使用 `/start <Cookie>` 来添加或更新 Cookie",
                                parse_mode='Markdown', reply_to_message_id=message.message_id)
                raise
            bot.send_message(message.chat.id, "发送评论成功",
                             reply_to_message_id=message.message_id)
    if re.search(r'回复此消息即可对此条目进行吐槽', str(message.reply_to_message.caption), re.I | re.M):
        for i in re.findall(r'(bgm\.tv)/subject/([0-9]+)', str(message.reply_to_message.html_caption), re.I | re.M):
            user_collection = user_collection_get(message.from_user.id, i[1])
            try:
                post_collection(message.from_user.id, i[1],
                                status=user_collection['status']['type'] if user_collection['status']['type'] else 'collect',
                                comment=message.text,
                                rating=user_collection['rating'] if user_collection['rating'] else None)
            except:
                bot.send_message(message.chat.id, "*发送简评失败*", parse_mode='Markdown', reply_to_message_id=message.message_id)
                raise
            bot.send_message(message.chat.id, "发送简评成功",
                             reply_to_message_id=message.message_id)
    if re.search(r'回复此消息即可修改标签', str(message.reply_to_message.caption), re.I | re.M):
        for i in re.findall(r'(bgm\.tv)/subject/([0-9]+)', str(message.reply_to_message.html_caption), re.I | re.M):
            subject_id = i[1]
            user_collection = user_collection_get(message.from_user.id, subject_id)
            try:
                post_collection(message.from_user.id, subject_id,
                                status=user_collection['status']['type'] if user_collection['status']['type'] else 'collect',
                                tags=message.text,
                                rating=user_collection['rating'] if user_collection['rating'] else None)
            except:
                bot.send_message(message.chat.id, "*修改标签失败*", parse_mode='Markdown', reply_to_message_id=message.message_id)
                raise
            bot.send_message(message.chat.id, "修改标签成功", reply_to_message_id=message.message_id)
            subject_info = get_subject_info(subject_id)
            user_collection = user_collection_get(message.from_user.id, subject_id)
            if (user_collection and 'tag' in user_collection and user_collection['tag'] and len(user_collection['tag']) == 1 and user_collection['tag'][0] == ""):
                user_collection['tag'] = []  # 鬼知道为什么没标签会返回个空字符串
            text = f"*{subject_type_to_emoji(subject_info['type'])}" \
                   f"『 {subject_info['name_cn'] or subject_info['name']} 』标签管理*\n\n"
            text += "➤ *常用标签：*"
            if subject_info['tags']:
                for tag in subject_info['tags']:
                    text += f"`{tag['name']}` "
            else:
                text += "此条目暂无标签"
            text += "\n\n➤ *我的标签：*"
            if user_collection['tag']:
                for tag in user_collection['tag']:
                    text += f"`{tag}` "
            else:
                text += "未设置条目标签"
            text += f"\n\n📖 [详情](https://bgm.tv/subject/{subject_id})\n*回复此消息即可修改标签 (此操作直接对现有设置标签进行覆盖，多标签请用空格隔开)*"
            markup = telebot.types.InlineKeyboardMarkup()
            markup.add(telebot.types.InlineKeyboardButton(text='返回', callback_data=f'{message.reply_to_message.reply_markup.keyboard[0][0].callback_data}|back'))
            bot.edit_message_caption(chat_id=message.chat.id ,message_id=message.reply_to_message.message_id, caption=text, parse_mode='Markdown', reply_markup=markup)