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


class SubjectRequest(BaseRequest):
    def __init__(self, subject_id: str):
        """条目详情

        :param subject_id: 条目ID
        """
        super().__init__()
        self.subject_id: str = subject_id
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
