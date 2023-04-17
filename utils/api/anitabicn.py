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
    async def get_anitabi_data(self, subject_id):
        """获取 anitabi 数据"""
        async with self.s.get(
            f"https://api.anitabi.cn/bangumi/{subject_id}/lite",
        ) as resp:
            if resp.status == 404:
                return None
            return await resp.json()
