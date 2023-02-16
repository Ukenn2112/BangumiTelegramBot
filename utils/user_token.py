import datetime
from typing import Union

from .config_vars import bgm, sql


async def bgm_user_data(tg_id: int) -> Union[dict, None]:
    """获取用户的数据 过期则刷新 没有则返回 None
    :return: {"bgmId": 用户 ID, "accessToken": 授权密钥, "Cookie": Cookie}"""
    user_data = sql.inquiry_user_data(tg_id)
    if user_data:
        if user_data[5] < datetime.datetime.now().timestamp() // 1000:
            back = await bgm.oauth_refresh_token(user_data[3])
            if not back["access_token"]:
                sql.delete_user_data(tg_id)
                return None
            sql.update_user_data(tg_id, back["access_token"], back["refresh_token"], user_data[4])
            return {"bgmId": user_data[1], "accessToken": back["access_token"], "Cookie": user_data[4]}
        else:
            return {"bgmId": user_data[1], "accessToken": user_data[2], "Cookie": user_data[4]}
    else:
        return None