from typing import Dict, List, Literal, Optional

from telebot.types import Message, CallbackQuery
from telebot import REPLY_MARKUP_TYPES

COLLECTION_TYPE_STR = Literal["wish", "collect", "do", "on_hold", "dropped"]
EpStatusType = Literal["watched", "queue", "drop", "remove", "watched_batch"]


class BaseRequest:
    def __init__(self, session):
        self.possible_request: Dict[str, BaseRequest] = {} # 可能的请求
        self.page_text: Optional[str] = None # 页面文本
        self.page_image: Optional[str] = None # 页面图片
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None # 页面回调
        self.callback_text: Optional[str] = None # 回调文本
        self.retain_image: Optional[bool] = True  # 是否保留页面图片
        self.session: RequestSession = session # 会话


class RequestSession:
    request_message: Message # 用户请求消息
    bot_message: Message # 机器人消息

    def __init__(self, uuid: str, request_message: Message, user_bgm_data: dict):
        """Telegram 页面会话
        :param uuid: 会话 uuid
        :param request_message: 用户请求消息
        :param user_bgm_data: 用户 Bangumi 数据
        """
        self.stack: List[BaseRequest] = [] # 请求栈
        self.uuid: str = uuid # 会话 uuid
        self.call: Optional[CallbackQuery] = None # 回调
        self.request_message: Message = request_message # 用户请求消息
        self.user_bgm_data = user_bgm_data # 用户 Bangumi 数据


class WeekRequest(BaseRequest):
    def __init__(self, session: RequestSession, week_day: int):
        """周放送

        :param week_day: 周几
        """
        super().__init__(session)
        self.week_day: int = week_day

        self.retain_image = False

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class CollectionsRequest(BaseRequest):
    def __init__(
        self,
        session: RequestSession,
        subject_type: Literal[1, 2, 3, 4, 6],
        offset=0,
        collection_type: Literal[1, 2, 3, 4, 5, None] = 3,
        limit=10,
        user_bgm_data: dict = None,
    ):
        """用户收藏
        :param subject_type: 条目类型 1书籍 2动画 3音乐 4游戏 6三次元
        :param offset: 分页页数
        :param collection_type: 收藏类型 1想看 2看过 3在看 4搁置 5抛弃
        :param limit:每页数量
        :param user_bgm_data: 用户 Bangumi 数据
        """
        super().__init__(session)
        self.subject_type: Literal[1, 2, 3, 4, 6] = subject_type
        self.offset: int = offset
        self.collection_type: Literal[1, 2, 3, 4, 5, None] = collection_type
        self.limit: int = limit

        self.user_bgm_data = user_bgm_data
        self.retain_image = False

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class SubjectRequest(BaseRequest):
    def __init__(self, session: RequestSession, subject_id: int, subject_info: dict = None, is_root: bool = False):
        """条目详情

        :param subject_id: 条目ID
        :param subject_info: 条目信息
        :param is_root: 是否为根节点 如为真则不可返回
        """
        super().__init__(session)
        self.subject_id: int = subject_id
        self.subject_info: dict = subject_info
        self.is_root: bool = is_root
        self.retain_image = False

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class SummaryRequest(BaseRequest):
    def __init__(self, session: RequestSession, subject_info: dict):
        """条目介绍

        :param subject_info: 条目信息
        """
        super().__init__(session)
        self.subject_info: dict = subject_info

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class EditCollectionTypePageRequest(BaseRequest):
    def __init__(self, session: RequestSession, subject_id: int):
        """修改收藏类型页

        :param subject_id: 条目ID
        """
        super().__init__(session)
        self.subject_id: int = subject_id
        self.user_collection = None

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class DoEditCollectionTypeRequest(BaseRequest):
    def __init__(
        self, session: RequestSession, subject_id: int, collection_type: COLLECTION_TYPE_STR
    ):
        """修改收藏类型

        :param subject_id: 条目ID
        """
        super().__init__(session)
        self.subject_id: int = subject_id
        self.collection_type: COLLECTION_TYPE_STR = collection_type

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class EditRatingPageRequest(BaseRequest):
    def __init__(self, session: RequestSession, user_collection: dict):
        """修改评分页

        :param user_collection: 用户收藏信息
        """
        super().__init__(session)
        self.user_collection = user_collection

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class DoEditRatingRequest(BaseRequest):
    def __init__(self, session: RequestSession, subject_id: int, rating_num: int):
        """修改评分

        :param subject_id: 条目ID
        """
        super().__init__(session)
        self.subject_id: int = subject_id
        self.rating_num: int = rating_num
        self.user_collection = None

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class SubjectEpsPageRequest(BaseRequest):
    def __init__(
        self,
        session: RequestSession,
        subject_info: dict,
        episode_type: Literal[0, 1, 2, 3, 4, 5, 6] = 0,
        limit=100,
        offset=0,
    ):
        """展示条目章节页

        :param subject_info: 条目信息
        :param episode_type: 章节类型 0: 本篇 (默认), 1: 特别篇, 2: OP, 3: ED, 4, 预告/宣传/广告, 5: MAD, 6: 其他
        """

        super().__init__(session)
        self.subject_info: dict = subject_info
        self.limit = limit
        self.offset = offset
        self.episode_type: Literal[0, 1, 2, 3, 4, 5, 6] = episode_type

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class SubjectRelationsPageRequest(BaseRequest):
    def __init__(self, session: RequestSession, subject_info: dict):
        """展示条目关联条目

        :param subject_info: 条目信息
        """

        super().__init__(session)
        self.subject_info: dict = subject_info

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class EditEpsPageRequest(BaseRequest):
    def __init__(
        self,
        session: RequestSession,
        episode_id: int,
        episode_info: dict = None,
        before_status=None,
    ):
        """修改评分页"""
        super().__init__(session)
        self.episode_id = episode_id
        self.episode_info = episode_info
        self.before_status: int = before_status

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class DoEditEpisodeRequest(BaseRequest):
    def __init__(self, session: RequestSession, episode_id: int, status: EpStatusType):
        """修改评分

        :param episode_id: 章节ID
        :param status: 要修改的状态
        """
        super().__init__(session)
        self.episode_id: int = episode_id
        self.status: EpStatusType = status

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class EditCollectionTagsPageRequest(BaseRequest):
    def __init__(self, session: RequestSession, subject_id: int):
        """修改收藏标签页

        :param subject_id: 条目ID
        """
        super().__init__(session)
        self.subject_id: int = subject_id

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class BackRequest(BaseRequest):
    def __init__(self, session: RequestSession, needs_refresh: bool = False):
        """返回请求"""
        super().__init__(session)
        self.needs_refresh = needs_refresh

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None


class RefreshRequest(BaseRequest):
    def __init__(self, session: RequestSession):
        """刷新请求"""
        super().__init__(session)

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[REPLY_MARKUP_TYPES] = None
