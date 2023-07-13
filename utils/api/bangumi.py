import base64
import builtins
import datetime
from typing import Literal, Union

import aiohttp
import requests
from lxml.etree import HTML

from ..before_api import cache_data, redis
from ..subject_img import subject_image
from .onair import get_onair_data


class BangumiAPI:
    """Bangumi API
    :param app_id: Bangumi App ID
    :param app_secret: Bangumi App Secret
    :param redirect_uri: OAuth 回调地址
    :param nsfw_token: NSFW Token"""

    api_url = "https://api.bgm.tv"

    def __init__(self, app_id: str, app_secret: str, redirect_uri: str, nsfw_token: str = None):
        self.app_id = app_id
        self.app_secret = app_secret
        self.redirect_uri = redirect_uri
        self.nsfw_token = nsfw_token # 携带登陆密钥才能获取 NSFW 数据
        self.headers = {
                "User-Agent":"Ukenn/BangumiBot (https://github.com/Ukenn2112/BangumiTelegramBot)"
            },
        self.s = aiohttp.ClientSession(
            headers = self.headers[0],
            timeout = aiohttp.ClientTimeout(total=10),
        )

    def web_authorization_captcha(self):
        """获取验证码图片
        :return (图片 Base64, RequestsCookieJar)"""
        set_cookie = requests.get("https://bgm.tv/login", headers = self.headers[0], timeout=10).cookies
        now = datetime.datetime.now()
        with requests.get(
            f"https://bgm.tv/signup/captcha?{int(now.timestamp() * 1000)}1",
            headers = self.headers[0],
            cookies=set_cookie,
        ) as resp:
            return (base64.b64encode(resp.content).decode('utf-8'), set_cookie)

    def web_authorization_login(self, cookies: str, email: str, password: str, captcha_challenge_field: str):
        """Web 登录
        :return (是否成功 bool, 错误信息/RequestsCookieJar)"""
        with requests.post(
            "https://bgm.tv/FollowTheRabbit",
            headers = {
                **self.headers[0],
                "Cookie": cookies,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data = {
                "email": email,
                "password": password,
                "captcha_challenge_field": captcha_challenge_field,
                "loginsubmit": "登录",
                "referer": "https://bgm.tv/FollowTheRabbit",
                "dreferer": "https://bgm.tv/FollowTheRabbit",
            },
            allow_redirects=False,
            timeout = 10,
        ) as resp:
            if resp.status_code == 200:
                resp.encoding = "utf-8"
                html_data = HTML(resp.text)
                error = html_data.xpath("//*[@id='colunmNotice']/div/p[1]")
                if error:
                    return (False, error[0].text)
            return (True, resp.cookies)

    def web_authorization_oauth(self, cookies: str):
        """Web OAuth 授权
        :return code"""
        params = {
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
        }
        get_data = requests.get(
            "https://bgm.tv/oauth/authorize",
            headers = {
                **self.headers[0],
                "Cookie": cookies,
            },
            params = params,
            timeout = 10,
        )
        html_data = HTML(get_data.text)
        formhash = html_data.xpath("//input[@name='formhash']/@value")
        if not formhash: return None
        return requests.post(
            "https://bgm.tv/oauth/authorize",
            headers = {
                **self.headers[0],
                "Cookie": cookies,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data = {
                "client_id": self.app_id,
                "formhash": formhash[0],
                "redirect_uri": None,
                "submit": "授权",
            },
            params = params,
            timeout = 10,
            allow_redirects=False
        ).headers.get('Location').split("code=")[-1]

    # OAuth https://github.com/bangumi/api/blob/master/docs-raw/How-to-Auth.md
    def oauth_authorization_code(self, code: str) -> dict:
        """授权获取 access_token
        :return {
            "access_token": "xxxxxxxxxxxxxxxx", api请求密钥
            "expires_in": 604800, 有效期7天
            "refresh_token": "xxxxxxxxxxxxxxxxxxx",  续期密钥
            "scope": null,
            "token_type": "Bearer",
            "user_id": xxxxxx  bgm用户uid
        }"""
        with requests.post(
            "https://bgm.tv/oauth/access_token",
            headers = self.headers[0],
            data = {
                "client_id": self.app_id,
                "client_secret": self.app_secret,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": self.redirect_uri
            },
            timeout=10
        ) as resp:
            return resp.json()

    async def oauth_refresh_token(self, refresh_token) -> dict:
        """刷新 access_token"""
        async with self.s.post(
            "https://bgm.tv/oauth/access_token",
            data = {
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
            f"{self.api_url}/v0/me",
            headers = {"Authorization": f"Bearer {access_token}"}
        ) as resp:
            return await resp.json()
    
    @cache_data
    async def get_user_info(self, bgm_id) -> dict:
        """
        获取用户信息 (Old API) 新 API 还没老的好用 (:3 」∠)_

        Docs: https://bangumi.github.io/api/#/%E7%94%A8%E6%88%B7/getUserByName

        :param bgm_id: BGM ID 或 用户名 可反查"""
        async with self.s.get(
            f"{self.api_url}/user/{bgm_id}",
        ) as resp:
            return await resp.json()
    # 收藏
    async def get_user_collections_status(self, username) -> Union[list, None]:
        """
        获取用户的收藏状态 (旧 API)

        Docs: https://bangumi.github.io/api/#/%E6%94%B6%E8%97%8F/getUserCollectionsStatusByUsername

        :param username: 用户名 可 UID"""
        async with self.s.get(
            f"{self.api_url}/user/{username}/collections/status",
            params = {
                "app_id": self.app_id,
            }
        ) as resp:
            if resp.status == 404:
                return None
            return await resp.json()

    async def get_user_subject_collections(self, username, access_token = None, subject_type = 2, collection_type = 3, limit = 30, offset = 0) -> Union[dict, None]:
        """
        获取用户的条目收藏

        Docs: https://bangumi.github.io/api/#/%E6%94%B6%E8%97%8F/getUserCollectionsByUsername

        :param username: 用户名 设置了用户名之后无法使用 UID。
        :param access_token: Access Token (可选) 查看私有收藏则需要
        :param subject_type: 收藏类型, 可选值: 1: 书籍, 2: 动画 (默认), 3: 音乐, 4: 游戏, 6: 三次元
        :param collection_type: 收藏状态, 可选值: 1: 想看, 2: 看过, 3: 在看 (默认), 4: 搁置, 5: 抛弃
        :param imit: 返回条目数量, 默认 30, 最大 100
        :param offset: 返回条目偏移, 默认 0"""
        async with self.s.get(
            f"{self.api_url}/v0/users/{username}/collections",
            headers = {"Authorization": f"Bearer {access_token}"} if access_token else None,
            params = {
                "subject_type": subject_type,
                "type": collection_type,
                "limit": limit,
                "offset": offset
            }
        ) as resp:
            if resp.status == 404:
                return None
            return await resp.json()

    async def get_user_subject_collection(self, username, subject_id, access_token = None) -> Union[dict, None]:
        """
        获取用户对应条目收藏 没有收藏则返回 None

        Docs: https://bangumi.github.io/api/#/%E6%94%B6%E8%97%8F/getUserCollection

        :param username: 用户名 设置了用户名之后无法使用 UID。
        :param subject_id: 条目 ID
        :param access_token: Access Token (可选) 查看私有收藏则需要"""
        async with self.s.get(
            f"{self.api_url}/v0/users/{username}/collections/{subject_id}",
            headers = {"Authorization": f"Bearer {access_token}"} if access_token else None,
        ) as resp:
            if resp.status == 404:
                return None
            return await resp.json()
        
    async def post_user_subject_collection(self, access_token, subject_id, collection_type: int = 3, rate: int = None, comment: str = None, private: bool = None, tags: str = None) -> None:
        """
        添加用户条目收藏 (旧 API)

        Docs: https://bangumi.github.io/api/#/%E6%94%B6%E8%97%8F/postUserCollection

        :param access_token: Access Token
        :param subject_id: 条目 ID
        :param collection_type: 收藏状态, 可选值: 1: 想看, 2: 看过, 3: 在看 (默认), 4: 搁置, 5: 抛弃
        :param rate: 评分, 0-10, 不填默认重置为未评分
        :param comment: 吐槽, 最多 200 字符
        :param private: 是否私有收藏, 默认 False
        :param tags: 标签, 多个以以半角空格分割"""

        _type = {1: "wish", 2: "collect", 3: "do", 4: "on_hold", 5: "dropped"}

        send_data = {"status": _type.get(collection_type, "do")}
        if rate is not None:
            send_data["rating"] = rate
        if comment is not None:
            send_data["comment"] = comment
        if private is not None:
            send_data["private"] = 0 if private else 1
        if tags is not None:
            send_data["tags"] = tags
        return await self.s.post(
            f"{self.api_url}/collection/{subject_id}/update",
            headers = {"Authorization": f"Bearer {access_token}"},
            data = send_data
        )
    
    async def patch_user_subject_collection(self, access_token, subject_id, collection_type: int = None, rate: int = None, ep_status: int = None, vol_status: int = None, comment: str = None, private: bool = None, tags: list[str] = None) -> None:
        """
        修改用户条目收藏

        Docs: https://bangumi.github.io/api/#/%E6%94%B6%E8%97%8F/patchUserCollection

        :param access_token: Access Token
        :param subject_id: 条目 ID
        :param collection_type: 收藏状态, 可选值: 1: 想看, 2: 看过, 3: 在看 (默认), 4: 搁置, 5: 抛弃
        :param rate: 评分, 0-10, 0 为删除评分
        :param ep_status: 章节状态, 0: 未看, 1: 看过, 2: 抛弃, 3: 搁置 (只能用于修改书籍条目进度)
        :param vol_status: 卷状态, 0: 未看, 1: 看过, 2: 抛弃, 3: 搁置 (只能用于修改书籍条目进度)
        :param comment: 吐槽, 最多 200 字符
        :param private: 是否私有收藏, 默认 False
        :param tags: 标签, None 为不修改, [] 为清空 不能包含空格"""
        send_data = {}
        if collection_type is not None:
            send_data["type"] = collection_type
        if rate is not None:
            send_data["rate"] = rate
        if ep_status is not None:
            send_data["ep_status"] = ep_status
        if vol_status is not None:
            send_data["vol_status"] = vol_status
        if comment is not None:
            send_data["comment"] = comment
        if private is not None:
            send_data["private"] = private
        if tags is not None:
            send_data["tags"] = tags
        return await self.s.patch(
            f"{self.api_url}/v0/users/-/collections/{subject_id}",
            headers = {"Authorization": f"Bearer {access_token}"},
            json = send_data
        )

    async def get_user_episode_collections(self, access_token, subject_id, offset = 0, limit = 100, episode_type = 0) -> Union[dict, None]:
        """
        获取用户条目章节收藏

        Docs: https://bangumi.github.io/api/#/%E6%94%B6%E8%97%8F/getUserSubjectEpisodeCollection

        :param access_token: Access Token
        :param subject_id: 条目 ID
        :param offset: 返回条目偏移, 默认 0
        :param limit: 返回条目数量, 默认 100, 最大 100
        :param episode_type: 集数类型, 0: 本篇 (默认), 1: 特别篇, 2: OP, 3: ED, 4, 预告/宣传/广告, 5: MAD, 6: 其他"""
        async with self.s.get(
            f"{self.api_url}/v0/users/-/collections/{subject_id}/episodes",
            headers = {"Authorization": f"Bearer {access_token}"},
            params = {
                "offset": offset,
                "limit": limit,
                "episode_type": episode_type
            }
        ) as resp:
            if resp.status == 404:
                return None
            return await resp.json()
    
    async def get_user_episode_collection(self, access_token, episode_id) -> Union[dict, None]:
        """
        获取用户单个章节收藏

        Docs: https://bangumi.github.io/api/#/%E6%94%B6%E8%97%8F/getUserEpisodeCollection

        :param access_token: Access Token
        :param episode_id: 章节 ID"""
        async with self.s.get(
            f"{self.api_url}/v0/users/-/collections/-/episodes/{episode_id}",
            headers = {"Authorization": f"Bearer {access_token}"},
        ) as resp:
            if resp.status == 404:
                return None
            return await resp.json()
    
    async def patch_uesr_episode_collection(self, access_token, subject_id, episodes_id: list[int], status: int = 2) -> None:
        """
        修改用户条目章节收藏

        Docs: https://bangumi.github.io/api/#/%E6%94%B6%E8%97%8F/patchUserSubjectEpisodeCollection

        :param access_token: Access Token
        :param subject_id: 条目 ID
        :param episodes_id: 章节 ID 列表
        :param status: 收藏状态, 可选值: 0: 未收藏, 1: 想看, 2: 看过, 3: 抛弃"""
        return await self.s.patch(
            f"{self.api_url}/v0/users/-/collections/{subject_id}/episodes",
            headers = {"Authorization": f"Bearer {access_token}"},
            json = {
                "episode_id": episodes_id,
                "type": status
            }
        )

    async def put_user_episode_collection(self, access_token, episode_id, status = 2) -> None:
        """
        修改用户章节收藏 (单集修改)

        Docs: https://bangumi.github.io/api/#/%E6%94%B6%E8%97%8F/putUserEpisodeCollection

        :param access_token: Access Token
        :param episode_id: 章节 ID
        :param status: 收藏状态, 可选值: 0: 未收藏, 1: 想看, 2: 看过, 3: 抛弃"""
        return await self.s.put(
            f"{self.api_url}/v0/users/-/collections/-/episodes/{episode_id}",
            headers = {"Authorization": f"Bearer {access_token}"},
            json = {
                "type": status
            }
        )
    
    def post_episode_reply(self, cookie: str, episode_id: int, reply_text: str) -> None:
        """
        吐槽章节

        :param cookie: 用户 Cookie
        :param episode_id: 章节 ID
        :param reply_text: 吐槽内容"""
        get_data = requests.get(
            f"https://bgm.tv/ep/{episode_id}",
            headers = {
                **self.headers[0],
                "Cookie": cookie,
            },
            timeout = 10
        )
        html_data = HTML(get_data.text)
        formhash = html_data.xpath('//input[@name="formhash"]/@value')[0]
        lastview = html_data.xpath('//input[@name="lastview"]/@value')[0]
        reply_text += "\n[color=grey][size=10][来自Bangumi for TelegramBot] [url=https://bgm.tv/group/topic/366880][color=grey]获取[/color][/url][/size][/color]"
        return requests.post(
            f"https://bgm.tv/subject/ep/{episode_id}/new_reply",
            headers = {
                **self.headers[0],
                "Cookie": cookie,
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data = {
                "content": reply_text,
                "related_photo": 0,
                "formhash": formhash,
                "lastview": lastview,
                "submit": "submit",
            },
            timeout = 10
        )

    # 条目
    @cache_data
    async def get_calendar(self) -> list:
        """
        每日放送

        Docs: https://bangumi.github.io/api/#/%E6%9D%A1%E7%9B%AE/getCalendar"""
        async with self.s.get(
            f"{self.api_url}/calendar"
        ) as resp:
            week_data = await resp.json()
            onair_data = get_onair_data()
            if onair_data is None:
                return week_data
            output = [
                {"weekday": {'en': 'Mon', 'cn': '星期一', 'ja': '月耀日', 'id': 1}, "items": []},
                {"weekday": {'en': 'Tue', 'cn': '星期二', 'ja': '火耀日', 'id': 2}, "items": []},
                {"weekday": {'en': 'Wed', 'cn': '星期三', 'ja': '水耀日', 'id': 3}, "items": []},
                {"weekday": {'en': 'Thu', 'cn': '星期四', 'ja': '木耀日', 'id': 4}, "items": []},
                {"weekday": {'en': 'Fri', 'cn': '星期五', 'ja': '金耀日', 'id': 5}, "items": []},
                {"weekday": {'en': 'Sat', 'cn': '星期六', 'ja': '土耀日', 'id': 6}, "items": []},
                {"weekday": {'en': 'Sun', 'cn': '星期日', 'ja': '日耀日', 'id': 7}, "items": []},
            ]
            for week in week_data:
                for subject in week["items"]:
                    check = False
                    for odata in onair_data:
                        if subject["id"] == int(odata["id"]):
                            check = True
                            if ontime := odata["timeCN"]:
                                subject["_air_time"] = ontime
                                subject["air_weekday"] = odata["weekDayCN"] if odata["weekDayCN"] != 0 else 7
                                output[subject["air_weekday"] - 1]["items"].append(subject)
                            elif sites := odata.get("sites"):
                                if begin := sites[0].get("begin"):
                                    begin = datetime.datetime.fromisoformat(begin.replace("Z", "+00:00")) + datetime.timedelta(hours=8)
                                    subject["_air_time"] = begin.strftime("%H%M")
                                    weekday = int(begin.strftime("%w"))
                                    subject["air_weekday"] = weekday if weekday != 0 else 7
                                    output[subject["air_weekday"] - 1]["items"].append(subject)
                                elif ontime := odata["timeJP"]:
                                    subject["_air_time"] = ontime
                                    subject["air_weekday"] = odata["weekDayJP"] if odata["weekDayJP"] != 0 else 7
                                    output[subject["air_weekday"] - 1]["items"].append(subject)
                            elif ontime := odata["timeJP"]:
                                subject["_air_time"] = ontime
                                subject["air_weekday"] = odata["weekDayJP"] if odata["weekDayJP"] != 0 else 7
                                output[subject["air_weekday"] - 1]["items"].append(subject)
                            break
                    if not check: output[subject["air_weekday"] - 1]["items"].append(subject)
            return output


    @cache_data
    async def get_subject(self, subject_id, access_token: str = None, re=0) -> dict:
        """
        获取条目信息

        Docs: https://bangumi.github.io/api/#/%E6%9D%A1%E7%9B%AE/getSubjectById

        :param subject_id: 条目 ID
        :param access_token: Access Token"""
        if not access_token and re == 0:
            access_token = self.nsfw_token
        async with self.s.get(
            f"{self.api_url}/v0/subjects/{subject_id}",
            headers = {"Authorization": f"Bearer {access_token}"} if access_token else None,
        ) as resp:
            loads = await resp.json()
            if resp.status != 200 and re == 0:
                print(f"Error: {loads}")
                return await self.get_subject(subject_id, None, 1)
            loads["_air_weekday"] = None
            for info in loads["infobox"]:
                if info["key"] == "放送星期":
                    loads["_air_weekday"] = info["value"]  # 加一个下划线 用于区别
                    break
            if loads["images"]["large"]:
                redis.set(f"_subject_image:{subject_id}", subject_image(loads), ex = 60 * 60 * 24)
            return loads
    
    @cache_data
    async def get_subject_persons(self, subject_id, access_token: str = None) -> list:
        """
        获取条目人物

        Docs: https://bangumi.github.io/api/#/%E6%9D%A1%E7%9B%AE/getRelatedPersonsBySubjectId

        :param subject_id: 条目 ID
        :param access_token: Access Token"""
        if not access_token:
            access_token = self.nsfw_token
        async with self.s.get(
            f"{self.api_url}/v0/subjects/{subject_id}/persons",
            headers = {"Authorization": f"Bearer {access_token}"} if access_token else None,
        ) as resp:
            return await resp.json()
    
    @cache_data
    async def get_subject_characters(self, subject_id, access_token: str = None) -> list:
        """
        获取条目角色

        Docs: https://bangumi.github.io/api/#/%E6%9D%A1%E7%9B%AE/getRelatedCharactersBySubjectId

        :param subject_id: 条目 ID
        :param access_token: Access Token"""
        if not access_token:
            access_token = self.nsfw_token
        async with self.s.get(
            f"{self.api_url}/v0/subjects/{subject_id}/characters",
            headers = {"Authorization": f"Bearer {access_token}"} if access_token else None,
        ) as resp:
            return await resp.json()
    
    @cache_data
    async def get_subject_related(self, subject_id, access_token: str = None) -> list:
        """
        获取条目相关条目

        Docs: https://bangumi.github.io/api/#/%E6%9D%A1%E7%9B%AE/getRelatedSubjectsBySubjectId

        :param subject_id: 条目 ID
        :param access_token: Access Token"""
        if not access_token:
            access_token = self.nsfw_token
        async with self.s.get(
            f"{self.api_url}/v0/subjects/{subject_id}/subjects",
            headers = {"Authorization": f"Bearer {access_token}"} if access_token else None,
        ) as resp:
            return await resp.json()
    # 章节
    @cache_data
    async def get_episodes(self, subject_id, episode_type = 0, limit = 100, offset = 100, access_token: str = None) -> dict:
        """
        获取条目章节信息

        Docs: https://bangumi.github.io/api/#/%E7%AB%A0%E8%8A%82/getEpisodes

        :param subject_id: 条目 ID
        :param episode_type: 集数类型, 0: 本篇 (默认), 1: 特别篇, 2: OP, 3: ED, 4, 预告/宣传/广告, 5: MAD, 6: 其他
        :param limit: 返回数量, 默认 100
        :param offset: 偏移量, 默认 0
        :param access_token: Access Token"""
        if not access_token:
            access_token = self.nsfw_token
        async with self.s.get(
            f"{self.api_url}/v0/episodes",
            headers = {"Authorization": f"Bearer {access_token}"} if access_token else None,
            params = {
                "subject_id": subject_id,
                "type": episode_type,
                "limit": limit,
                "offset": offset,
            }
        ) as resp:
            return await resp.json()
    
    @cache_data
    async def get_episode(self, episode_id, access_token: str = None) -> dict:
        """
        获取章节信息

        Docs: https://bangumi.github.io/api/#/%E7%AB%A0%E8%8A%82/getEpisodeById

        :param episode_id: 章节 ID
        :param access_token: Access Token"""
        if not access_token:
            access_token = self.nsfw_token
        async with self.s.get(
            f"{self.api_url}/v0/episodes/{episode_id}",
            headers = {"Authorization": f"Bearer {access_token}"} if access_token else None,
        ) as resp:
            return await resp.json()

    # 人物
    @cache_data
    async def get_person(self, person_id) -> dict:
        """
        获取人物信息

        Docs: https://bangumi.github.io/api/#/%E4%BA%BA%E7%89%A9/getPersonById

        :param person_id: 人物 ID"""
        async with self.s.get(
            f"{self.api_url}/v0/persons/{person_id}",
        ) as resp:
            return await resp.json()

    @cache_data
    async def get_person_subjects(self, person_id) -> list:
        """
        获取人物相关条目

        Docs: https://bangumi.github.io/api/#/%E4%BA%BA%E7%89%A9/getRelatedSubjectsByPersonId

        :param person_id: 人物 ID"""
        async with self.s.get(
            f"{self.api_url}/v0/persons/{person_id}/subjects",
        ) as resp:
            return await resp.json()
    
    @cache_data
    async def get_person_characters(self, person_id) -> list:
        """
        获取人物相关角色

        Docs: https://bangumi.github.io/api/#/%E4%BA%BA%E7%89%A9/getRelatedCharactersByPersonId

        :param person_id: 人物 ID"""
        async with self.s.get(
            f"{self.api_url}/v0/persons/{person_id}/characters",
        ) as resp:
            return await resp.json()
    # 角色
    @cache_data
    async def get_character(self, character_id) -> dict:
        """
        获取角色信息

        Docs: https://bangumi.github.io/api/#/%E8%A7%92%E8%89%B2/getCharacterById

        :param character_id: 角色 ID"""
        async with self.s.get(
            f"{self.api_url}/v0/characters/{character_id}",
        ) as resp:
            return await resp.json()
    
    @cache_data
    async def get_character_subjects(self, character_id) -> list:
        """
        获取角色相关条目

        Docs: https://bangumi.github.io/api/#/%E8%A7%92%E8%89%B2/getRelatedSubjectsByCharacterId

        :param character_id: 角色 ID"""
        async with self.s.get(
            f"{self.api_url}/v0/characters/{character_id}/subjects",
        ) as resp:
            return await resp.json()
    
    @cache_data
    async def get_character_persons(self, character_id) -> list:
        """
        获取角色相关人物

        Docs: https://bangumi.github.io/api/#/%E8%A7%92%E8%89%B2/getRelatedPersonsByCharacterId

        :param character_id: 角色 ID"""
        async with self.s.get(
            f"{self.api_url}/v0/characters/{character_id}/persons",
        ) as resp:
            return await resp.json()
    # 搜索
    @cache_data
    async def search_subjects(self, keywords, subject_type: int = None, response_group: Literal["small", "medium", "large"] = "small", start = 0, max_results = 10) -> list:
        """
        条目搜索 (Old API) 由于新 API 暂时为试验性可能变动较大, 故暂时使用旧 API

        Docs: https://bangumi.github.io/api/#/%E6%90%9C%E7%B4%A2/searchSubjectByKeywords

        :param keywords: 关键词
        :param subject_type: 条目类型, 1: 小说, 2: 动画, 3: 音乐, 4: 音乐, 6: 三次元
        :param response_group: 返回数据组, small: 小, medium: 中 large: 大, 默认 small
        :param start: 返回起始位置, 默认 0
        :param max_results: 返回数量, 默认 25 (最大 25)"""
        params = {
            "responseGroup": response_group,
            "start": start,
            "max_results": max_results,
        }
        if subject_type:
            params["type"] = subject_type
        async with self.s.get(
            f"{self.api_url}/search/subject/{keywords}",
            params = params
        ) as resp:
            try:
                return await resp.json()
            except:
                return {"results": 0, "list": []}

    @cache_data
    async def search_mono(self, keywords, page = 1, cat: Literal["all", "crt", "prsn"] = "all"):
        """
        人物搜索 (Web API)

        :param keyword: 关键词
        :param page: 页码, 默认 1
        :param cat: 搜索类型, all: 全部, crt: 角色, prsn: 人物, 默认 all"""
        async with self.s.get(
            f"http://bgm.tv/mono_search/{keywords}",
            params = {
                "cat": cat,
                "page": page,
            }
        ) as resp:
            html_data = HTML(await resp.text())
            error = html_data.xpath("//*[@id='colunmNotice']/div/p[1]")
            if error:
                return {"error": error[0].text, "list": []}
            else:
                rows = html_data.xpath("//*[@id='columnSearchB']/div[@class='light_odd clearit']")
                list_data = list()
                for row in rows:
                    _name = row.xpath("div/h2/a")
                    name = builtins.str.removesuffix(_name[0].text, " / ") if _name else None
                    _name_cn = row.xpath("div/h2/a/span")
                    name_cn = _name_cn[0].text if _name_cn else None
                    _img_url = row.xpath("a/img")
                    img_url = (
                        "https:" + _img_url[0].get("src")
                        if _img_url and _img_url[0].get("src") != "/img/info_only.png"
                        else None
                    )
                    _info = row.xpath('div[2]/div/span')
                    info = _info[0].text.strip() if _info else None
                    _mono_data = row.xpath("a")
                    mono_id, mono_type = None, None
                    if _mono_data:
                        mono_data: str = _mono_data[0].get("href")
                        if mono_data.startswith("/character/"):
                            mono_id = int(mono_data[11:])
                            mono_type = "character"
                        elif mono_data.startswith("/person/"):
                            mono_id = int(mono_data[8:])
                            mono_type = "person" # 人物
                    list_data.append({
                        "id": mono_id,
                        "type": mono_type,
                        "name": name,
                        "name_cn": name_cn,
                        "img_url": img_url,
                        "info": info,
                    })
                return {"error": None, "list": list_data}