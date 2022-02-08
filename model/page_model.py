from typing import List, Dict, Optional

import telebot


class BaseRequest:

    def __init__(self):
        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None
        """所有页面的父类 抽象类 不应该被生成对象"""
        if type(self) == BaseRequest:
            raise RuntimeError("这是个抽象类,不能生成对象")


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


class SubjectRequest(BaseRequest):
    def __init__(self, subject_id: str):
        """条目详情

        :param subject_id: 条目ID
        """
        super().__init__()
        self.subject_id: str = subject_id
        self.is_root: bool = False

        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None


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


class BackRequest(BaseRequest):
    def __init__(self):
        """返回请求
        """
        super().__init__()
        self.possible_request: Dict[str, BaseRequest] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None


class RequestStack:
    stack: List[BaseRequest]
    request_message: telebot.types.Message
    bot_message: telebot.types.Message

    def __init__(self, page: BaseRequest, uuid: str):
        """
        tg页面栈
        """
        self.stack = [page]
        self.uuid = uuid
