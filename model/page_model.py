from typing import List, Dict, Literal, Optional

import telebot

NEXT_ACTION_MODE = Literal['返回', '入栈', '改变']


class BasePage:

    def __init__(self):
        self.next_action: NEXT_ACTION_MODE = '入栈'
        self.possible_request: Dict[str, BasePage] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None
        """所有页面的父类 抽象类 不应该被生成对象"""
        if type(self) == BasePage:
            raise RuntimeError("这是个抽象类,不能生成对象")


class WeekPage(BasePage):

    def __init__(self, week_day: int):
        """周放送页面

        :param week_day: 周几
        """
        super().__init__()
        self.week_day: int = week_day
        self.next_action: NEXT_ACTION_MODE = '改变'
        self.possible_request: Dict[str, BasePage] = {}
        self.page_text: Optional[str] = None
        self.page_image: Optional[str] = None
        self.page_markup: Optional[telebot.REPLY_MARKUP_TYPES] = None


class RequestStack:
    stack: List[BasePage]
    request_message: telebot.types.Message
    bot_message: telebot.types.Message

    def __init__(self, page: BasePage, uuid: str):
        """
        tg页面栈
        """
        self.stack = [page]
        self.uuid = uuid
