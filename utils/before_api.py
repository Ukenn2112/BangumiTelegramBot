import datetime
from typing import Union

from .config_vars import bgm, sql


async def get_user_token(tg_id: int) -> Union[str, None]:
    """获取用户的token 过期则刷新"""
    user_data = sql.inquiry_user_data(tg_id)
    if user_data:
        if user_data[5] < datetime.datetime.now().timestamp() // 1000:
            back = await bgm.oauth_refresh_token(user_data[3])
            if not back["access_token"]:
                sql.delete_user_data(tg_id)
                return None
            sql.update_user_data(tg_id, back["access_token"], back["refresh_token"], user_data[4])
            return back["access_token"]
        else:
            return user_data[2]
    else:
        return None
