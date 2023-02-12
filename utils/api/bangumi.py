import aiohttp


class BangumiAPI:
    """Bangumi API
    :param app_id: Bangumi App ID
    :param app_secret: Bangumi App Secret"""

    api_url = "https://api.bgm.tv/v0"

    def __init__(self, app_id: str, app_secret: str, redirect_uri: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri

    async def __aenter__(self):
        self.s = aiohttp.ClientSession(
            headers={
                "User-Agent":"Ukenn/BangumiBot (https://github.com/Ukenn2112/BangumiTelegramBot)"
            },
            timeout=aiohttp.ClientTimeout(total=10),
        )
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        await self.s.close()

    # OAuth
    async def oauth_authorization_code(self, code: str) -> dict:
        """授权获取 access_token
        :return {
            "access_token": "xxxxxxxxxxxxxxxx", api请求密钥
            "expires_in": 604800, 有效期7天
            "refresh_token": "xxxxxxxxxxxxxxxxxxx",  续期密钥
            "scope": null,
            "token_type": "Bearer",
            "user_id": xxxxxx  bgm用户uid
        }"""
        async with self.s.post(
            "https://bgm.tv/oauth/access_token",
            data={
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri
            }
        ) as resp:
            return await resp.json()

    async def oauth_refresh_token(self, refresh_token) -> dict:
        """刷新 access_token"""
        async with self.s.post(
            "https://bgm.tv/oauth/access_token",
            data={
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "redirect_uri": self.redirect_uri
            }
        ) as resp:
            return await resp.json()
    # 用户
    async def get_me_info(self, access_token) -> dict:
        """
        获取当前 Access Token 对应的用户信息
        
        Docs: https://bangumi.github.io/api/#/%E7%94%A8%E6%88%B7/getMyself
        
        access_token: Access Token"""
        async with self.s.get(
            f"{self.api_url}/me",
            headers = {"Authorization": f"Bearer {access_token}"}
        ) as resp:
            return await resp.json()
    
    async def get_user_info(self, username) -> dict:
        """
        获取用户信息

        Docs: https://bangumi.github.io/api/#/%E7%94%A8%E6%88%B7/getUserByName

        username: 用户名 设置了用户名之后无法使用 UID。"""
        async with self.s.get(
            f"{self.api_url}/users/{username}",
        ) as resp:
            return await resp.json()
    # 收藏
    async def get_user_subject_collections(self, username, access_token = None, subject_type = 2, collection_type = 3, limit = 30, offset = 0) -> dict:
        """
        获取对应用户的条目收藏

        Docs: https://bangumi.github.io/api/#/%E6%94%B6%E8%97%8F/getUserCollectionsByUsername

        username: 用户名 设置了用户名之后无法使用 UID。

        access_token: Access Token (可选) 查看私有收藏则需要

        subject_type: 收藏类型, 可选值: 1: 书籍, 2: 动画 (默认), 3: 音乐, 4: 游戏, 6: 三次元

        collection_type: 收藏状态, 可选值: 1: 想看, 2: 看过, 3: 在看 (默认), 4: 搁置, 5: 抛弃

        limit: 返回条目数量, 默认 30, 最大 100

        offset: 返回条目偏移, 默认 0"""
        async with self.s.get(
            f"{self.api_url}/users/{username}/collections",
            headers = {"Authorization": f"Bearer {access_token}"} if access_token else None,
            params={
                "subject_type": subject_type,
                "collection_type": collection_type,
                "limit": limit,
                "offset": offset
            }
        ) as resp:
            return await resp.json()

    async def get_user_subject_collection(self, username, subject_id, access_token = None) -> dict:
        """
        获取对应条目用户的收藏

        Docs: https://bangumi.github.io/api/#/%E6%94%B6%E8%97%8F/getUserCollection

        username: 用户名 设置了用户名之后无法使用 UID。

        subject_id: 条目 ID

        access_token: Access Token (可选) 查看私有收藏则需要"""
        async with self.s.get(
            f"{self.api_url}/users/{username}/collection/{subject_id}",
            headers = {"Authorization": f"Bearer {access_token}"} if access_token else None,
        ) as resp:
            return await resp.json()
    
    async def send_user_subject_collection(self, access_token, subject_id, status: str = "do", comment: str = None, tags: str = None, rating: int = None, privacy: int = 0) -> None:
        """
        发送条目收藏

        Docs: https://bangumi.github.io/api/#/%E6%94%B6%E8%97%8F/postUserCollection

        access_token: Access Token

        subject_id: 条目 ID

        status: 收藏状态, 可选值: wish: 想看, collect: 看过, do: 在看 (默认), on_hold: 搁置, drop: 抛弃

        comment: 吐槽 (简评，最多200字) (可选)

        tags: 标签, 多个以以半角空格分割 (可选)

        rating: 评分, 0-10 (可选) 不填默认重置为未评分

        privacy: 隐私设置, 0: 公开, 1: 私有"""
        params = {
            "status": status
            }
        if comment:
            params["comment"] = comment
        if tags:
            params["tags"] = tags
        if rating:
            params["rating"] = rating
        if privacy:
            params["privacy"] = privacy
        return await self.s.post(
            f"https://api.bgm.tv/collection/{subject_id}/update",
            headers = {"Authorization": f"Bearer {access_token}"},
            data = params
        )

    async def get_user_episode_collections(self, access_token, subject_id, offset = 0, limit = 100, episode_type = 0) -> dict:
        """
        获取条目章节收藏

        Docs: https://bangumi.github.io/api/#/%E6%94%B6%E8%97%8F/getUserSubjectEpisodeCollection

        access_token: Access Token

        subject_id: 条目 ID

        offset: 返回条目偏移, 默认 0

        limit: 返回条目数量, 默认 100, 最大 100

        episode_type: 集数类型, 0: 本篇 (默认), 1: 特别篇, 2: OP, 3: ED, 4, 预告/宣传/广告, 5: MAD, 6: 其他"""
        async with self.s.get(
            f"{self.api_url}/users/-/collections/{subject_id}/episodes",
            headers = {"Authorization": f"Bearer {access_token}"},
            params={
                "offset": offset,
                "limit": limit,
                "episode_type": episode_type
            }
        ) as resp:
            return await resp.json()
    
    async def get_user_episode_collection(self, access_token, episode_id) -> dict:
        """
        获取章节收藏

        Docs: https://bangumi.github.io/api/#/%E6%94%B6%E8%97%8F/getUserEpisodeCollection

        access_token: Access Token

        episode_id: 章节 ID"""
        async with self.s.get(
            f"{self.api_url}/users/-/collections/episodes/{episode_id}",
            headers = {"Authorization": f"Bearer {access_token}"},
        ) as resp:
            return await resp.json()
    
    async def update_user_episode_collection(self, access_token, episode_id, status = 2) -> None:
        """
        更新章节收藏

        Docs: https://bangumi.github.io/api/#/%E6%94%B6%E8%97%8F/putUserEpisodeCollection

        access_token: Access Token

        episode_id: 章节 ID

        status: 收藏状态, 可选值: 0: 未收藏, 1: 想看, 2: 看过, 3: 抛弃"""
        return await self.s.put(
            f"{self.api_url}/users/-/collections/episodes/{episode_id}",
            headers = {"Authorization": f"Bearer {access_token}"},
            data = {
                "type": status
            }
        )