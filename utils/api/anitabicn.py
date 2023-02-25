import aiohttp

from ..before_api import cache_data


class AnitabiAPI:
    """anitabi API"""

    def __init__(self):
        self.s = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            headers={
                "User-Agent": "Ukenn/BangumiBot (https://github.com/Ukenn2112/BangumiTelegramBot)"
            },
        )

    @cache_data
    async def get_anitabi_data(self):
        """获取 anitabi 数据"""
        async with self.s.get(
            "https://anitabi.cn/api/bangumi/points.geo",
        ) as resp:
            return await resp.json()
