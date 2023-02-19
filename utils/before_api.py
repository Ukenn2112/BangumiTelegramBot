import json
import random

import yaml
from redis import Redis

with open("data/config.yaml", "r") as f:
    redis_config: dict = yaml.safe_load(f)["REDIS"]

redis = Redis(
    host=redis_config['HOST'],
    port=redis_config['PORT'],
    db=redis_config['REDIS_DATABASE'])

def cache_data(func):
    """api 中间件 如有缓存则返回缓存"""
    async def wrapper(*args, **kwargs):
        # 函数名:不定量参数:定量参数（不包含 access_token）
        key = f"{func.__name__}:{json.dumps(args[1:])}:{json.dumps({k: v for k, v in kwargs.items() if k != 'access_token'})}"
        result = redis.get(key)
        if result:
            if result == b"None__":
                raise FileNotFoundError(f"API 请求错误-缓存 {key}")
            else:
                return json.loads(result)
        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            redis.set(key, "None__", ex=60 * 10)  # 不存在时 防止缓存穿透
            raise FileNotFoundError(f"API 请求错误 {key}:{e}")
        redis.set(key, json.dumps(result), ex=60 * 60 * 24 + random.randint(-3600, 3600))
        return result
    return wrapper
