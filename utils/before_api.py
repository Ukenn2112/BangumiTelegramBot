import datetime
import json
import random
from typing import Union

from .config_vars import bgm, redis, sql


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

def cache_data(func):
    """请求 api 数据并存入 redis"""
    async def wrapper(*args, **kwargs):
        # 函数名:不定量参数:定量参数（不包含 access_token）
        key = f"{func.__name__}:{json.dumps(args)}:{json.dumps({k: v for k, v in kwargs.items() if k != 'access_token'})}"
        result = redis.get(key)
        if result:
            return json.loads(result)
        try:
            result = await func(*args, **kwargs)
        except:
            redis.set(key, "None__", ex=60 * 10)  # 不存在时 防止缓存穿透
            raise FileNotFoundError(f"API 请求错误: {key}")
        redis.set(key, json.dumps(result), ex=60 * 60 * 24 + random.randint(-3600, 3600))
        return result
    return wrapper