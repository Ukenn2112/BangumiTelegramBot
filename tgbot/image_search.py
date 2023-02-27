from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from utils.api.tracemoe import get_image_search
from utils.config_vars import BOT_USERNAME, bgm, config


async def send_image_search(message: Message, bot: AsyncTeleBot):
    smg = await bot.reply_to(message, "正在搜索中...")
    if message.photo:
        file_info = await bot.get_file(message.photo[-1].file_id)
    else:
        file_info = await bot.get_file(message.reply_to_message.photo[-1].file_id)
    back_data = get_image_search(
        f"https://api.telegram.org/file/bot{config['BOT_TOKEN']}/{file_info.file_path}"
    )
    if back_data:
        millis = back_data["from"]
        seconds = int(millis % 60)
        minutes = int((millis / 60) % 60)
        hours = int((millis / (60 * 60)) % 24)

        bgm_data = await bgm.search_subjects(keywords=back_data["anilist"]["title"]["native"], subject_type=2)
        if bgm_data and bgm_data.get("list"):
            name = bgm_data["list"][0]["name_cn"] or bgm_data["list"][0]["name"]
            subject_id = bgm_data["list"][0]["id"]
        else:
            name = back_data["anilist"]["title"]["native"]
            subject_id = None
        await bot.delete_message(message.chat.id, smg.message_id)
        text = (
            f"*{name}*\n\n"
            f"*➤ 来自：*`第{back_data['episode']}集 - {hours:02d}:{minutes:02d}:{seconds:02d}`\n"
            f"*➤ 文件：* `{back_data['filename']}`\n"
            f"*➤ 相似度：* `{round(back_data['similarity']*100, 2)} %`\n"
            )
        markup = InlineKeyboardMarkup()
        if subject_id:
            markup.add(InlineKeyboardButton(text="查看详情", url=f"t.me/{BOT_USERNAME}?start={subject_id}"))
        await bot.send_video(message.chat.id, back_data["video"], caption=text, reply_to_message_id=message.message_id, reply_markup=markup)
    else:
        await bot.edit_message_text("没有找到结果", message.chat.id, smg.message_id)