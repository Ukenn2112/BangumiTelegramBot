from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message

from utils.config_vars import BOT_USERNAME


async def send_help(message: Message, bot: AsyncTeleBot):
    text = (
        f"*{BOT_USERNAME} 使用帮助*\n\n"
        "/start _绑定Bangumi账号_\n"
        "/book _Bangumi用户在读书籍_\n"
        "/anime _Bangumi用户在看动画_\n"
        "/game _Bangumi用户在玩游戏_\n"
        "/real _Bangumi用户在看剧集_\n"
        "/week _查询当日/空格加数字查询每日放送_\n"
        "/search _搜索条目引导_\n\n"
        "*Telegram inline(输入框内使用) 使用方法\n\n*"
        "*➤ 常用方法：*\n"
        f"`@{BOT_USERNAME} [关键字]`\n_进行 Bangumi 搜索_\n\n"
        f"`@{BOT_USERNAME} @[关键字]`\n_在Bot已加入的群组进行搜索_\n\n"
        f"`@{BOT_USERNAME} mybgm/mybgm [BGM username/Uid] `\n_查询Bangumi收藏统计/空格加username或uid不绑定查询_\n"
        "\n*➤ 更多方法：*_见图_"
    )
    await bot.send_photo(
        message.chat.id,
        photo="https://article.biliimg.com/bfs/article/81e655fd1dafd9fbb7dc060eba248cf857a83cc0.png",
        caption=text,
    )