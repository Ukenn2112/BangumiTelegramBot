"""查询 Bangumi 用户收藏列表"""
import asyncio
import math

from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils.config_vars import bgm
from utils.converts import (collection_type_subject_type_str,
                            subject_type_to_str)

from ..model.page_model import (BackRequest, CloseRequest, CollectionsRequest,
                                SubjectRequest)


async def generate_page(request: CollectionsRequest) -> CollectionsRequest:
    session_uuid = request.session.uuid
    subject_type = request.subject_type
    limit = request.limit
    offset = request.offset
    # 获取用户收藏列表
    user_collections = await bgm.get_user_subject_collections(
        request.user_bgm_data["userData"]["username"],
        request.user_bgm_data["accessToken"],
        request.subject_type,
        request.collection_type,
        request.limit,
        request.offset,
        )
    count = user_collections["total"]  # 总在看数 int
    subject_list = user_collections["data"] # 收藏列表 list
    if not subject_list:
        request.page_text = (
            f"出错啦，您貌似没有{collection_type_subject_type_str(subject_type, request.collection_type)}"
            f"的{subject_type_to_str(subject_type)}"
        )
        return request
    # 提前异步获取subject信息
    loop = asyncio.get_running_loop()
    tasks = []
    for info in subject_list:
        task = loop.create_task(bgm.get_subject(info["subject"]["id"], request.user_bgm_data["accessToken"]))
        tasks.append(task)
    asyncio.gather(*tasks)
    # 开始处理Telegram消息
    # 拼接字符串
    markup = InlineKeyboardMarkup()
    text_data = ""
    nums = range(1, len(subject_list) + 1)
    nums_unicode = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩"]
    button_list = []
    for info, num, nums_unicode in zip(subject_list, nums, nums_unicode):
        text_data += (
            f"*{nums_unicode}* {info['subject']['name_cn'] or info['subject']['name']}"
            f" `[{info['ep_status']}/{'??' if info['subject']['eps'] == 0 else info['subject']['eps']}]`\n\n"
        )
        button_list.append(InlineKeyboardButton(text=num, callback_data=f"{session_uuid}|{nums_unicode}"))
        request.possible_request[nums_unicode] = SubjectRequest(request.session, info["subject"]["id"])
    text = (
        f"*{request.user_bgm_data['userData']['nickname']} {collection_type_subject_type_str(subject_type, request.collection_type)}"
        f"的{subject_type_to_str(subject_type)}*\n\n{text_data}"
        f"共{count}部"
    )
    markup.add(*button_list, row_width=5)
    # 只有数量大于分页时 开启分页
    if count > limit:
        button_list2 = []
        if offset - limit >= 0:
            button_list2.append(InlineKeyboardButton(text="上一页", callback_data=f'{session_uuid}|back'))
            request.possible_request["back"] = BackRequest(request.session)
        else:
            button_list2.append(InlineKeyboardButton(text="这是首页", callback_data="None"))
        button_list2.append(InlineKeyboardButton(text=f'{int(offset / limit) + 1}/{math.ceil(count / limit)}', callback_data="None"))
        if offset + limit < count:
            button_list2.append(InlineKeyboardButton(text="下一页", callback_data=f'{session_uuid}|{offset + limit}'))
            next_request = CollectionsRequest(
                request.session,
                subject_type,
                offset=offset + limit,
                collection_type=request.collection_type,
                limit=limit,
                user_bgm_data=request.user_bgm_data,
            )
            request.possible_request[str(offset + limit)] = next_request
        else:
            button_list2.append(InlineKeyboardButton(text='这是末页', callback_data="None"))
        markup.add(*button_list2)
    if request.session.bot_message.chat.type != "private":
        markup.add(InlineKeyboardButton(text="关闭此对话", callback_data=f'{session_uuid}|close'))
        request.possible_request["close"] = CloseRequest(request.session, request.session.user_bgm_data['tgID'])
    request.page_text = text
    request.page_markup = markup
    return request
