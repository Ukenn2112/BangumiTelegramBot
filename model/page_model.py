from typing import List, Dict, Optional, Literal

import telebot

COLLECTION_TYPE_STR = Literal['wish', 'collect', 'do', 'on_hold', 'dropped']


class BaseRequest:

    def __init__(self):
        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class WeekRequest(BaseRequest):

    def __init__(self, week_day: int):
        """周放送

        :param week_day: 周几
        """
        super().__init__()
        self.week_day: int = week_day

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class CollectionsRequest(BaseRequest):

    def __init__(self, user_data, subject_type, offset=0, collection_type=3, limit=10):
        """用户收藏
        :param user_data: 用户数据
        :param subject_type: 条目类型 1书籍 2动画 3音乐 4游戏 6三次元
        :param offset: 分页页数
        :param collection_type: 收藏类型 1想看 2看过 3在看 4搁置 5抛弃
        :param limit:每页数量

        """
        super().__init__()
        self.user_data = user_data
        self.subject_type: int = subject_type
        self.offset: int = offset
        self.collection_type: int = collection_type
        self.limit: int = limit

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class SubjectRequest(BaseRequest):
    def __init__(self, subject_id: str, is_root: bool = False, user_data=None):
        """条目详情

        :param subject_id: 条目ID
        :param is_root: 是否为根节点 如为真则不可返回
        :param user_data: 用户信息 用于获取条目收藏
        """
        super().__init__()
        self.subject_id: str = subject_id
        self.is_root: bool = is_root
        self.user_data = user_data

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class SummaryRequest(BaseRequest):
    def __init__(self, subject_id: str):
        """条目介绍

        :param subject_id: 条目ID
        """
        super().__init__()
        self.subject_id: str = subject_id

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class EditCollectionTypePageRequest(BaseRequest):
    def __init__(self, subject_id: str):
        """修改收藏类型页

        :param subject_id: 条目ID
        """
        super().__init__()
        self.subject_id: str = subject_id

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class DoEditCollectionTypeRequest(BaseRequest):
    def __init__(self, subject_id: str, collection_type: COLLECTION_TYPE_STR):
        """修改收藏类型

        :param subject_id: 条目ID
        """
        super().__init__()
        self.subject_id: str = subject_id
        self.collection_type: COLLECTION_TYPE_STR = collection_type

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class EditRatingPageRequest(BaseRequest):
    def __init__(self, subject_id: str):
        """修改评分页

        :param subject_id: 条目ID
        """
        super().__init__()
        self.subject_id: str = subject_id
        self.user_collection = None

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class DoEditRatingRequest(BaseRequest):
    def __init__(self, subject_id: str, rating_num: int):
        """修改评分

        :param subject_id: 条目ID
        """
        super().__init__()
        self.subject_id: str = subject_id
        self.rating_num: int = rating_num
        self.user_collection = None

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None
        self.callback_text: Optional[str] = None


class BackRequest(BaseRequest):
    def __init__(self, needs_refresh: bool = False):
        """返回请求
        """
        super().__init__()
        self.needs_refresh = needs_refresh

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None


class RefreshRequest(BaseRequest):
    def __init__(self):
        """刷新请求
        """
        super().__init__()
        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None


class RequestStack:
    request_message: telebot.types.Message
    bot_message: telebot.types.Message

    def __init__(self, page: BaseRequest, uuid: str):
        """
        tg页面栈
        """
        self.stack: List[BaseRequest] = [page]
        self.uuid: str = uuid
        self.call: Optional[telebot.types.CallbackQuery] = None
