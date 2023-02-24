import datetime
from typing import Union

from .config_vars import bgm, sql
from tgbot.model.exception import TokenExpired

async def bgm_user_data(tg_id: int) -> Union[dict, None]:
    """获取用户的数据 过期则刷新 没有则返回 None
    :return: {"tgID": 用户 ID, "bgmId": 用户 ID, "accessToken": 授权密钥, "Cookie": Cookie, "userData": 用户数据}"""
    user_key = sql.inquiry_user_data(tg_id)
    if user_key:
        user_data = await bgm.get_user_info(user_key[1])
        if user_key[5] < datetime.datetime.now().timestamp() // 1000:
            back = await bgm.oauth_refresh_token(user_key[3])
            if not back.get("access_token"):
                if not user_key[4]:
                    sql.delete_user_data(tg_id)
                    raise TokenExpired("Token 已过期")
                code = bgm.web_authorization_oauth(user_key[4])
                if not code:
                    sql.delete_user_data(tg_id)
                    raise TokenExpired("Token 已过期")
                back = bgm.oauth_authorization_code(code)
            sql.update_user_data(tg_id, back["access_token"], back["refresh_token"], user_key[4])
            return {"tgID": user_key[0], "bgmId": user_key[1], "accessToken": back["access_token"], "Cookie": user_key[4], "userData": user_data}
        else:
            return {"tgID": user_key[0], "bgmId": user_key[1], "accessToken": user_key[2], "Cookie": user_key[4], "userData": user_data}
    else:
        return None