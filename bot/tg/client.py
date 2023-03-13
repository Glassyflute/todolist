import logging
from enum import Enum

import requests
from django.conf import settings

from bot.tg.dc import GetUpdatesResponse, SendMessageResponse


# class Command(str, Enum):
#     GET_UPDATES = "getUpdates"
#     SEND_MESSAGE = "sendMessage"


class TgClient:
    def __init__(self, token: str | None = None):
        self.token = token if token else settings.BOT_TELEGRAM_TOKEN
        # импортируем телеграм токен из django.conf settings
        # self.logger = logging.getLogger(__name__)

    def get_url(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        url = self.get_url("getUpdates")
        response = requests.get(url, params={"offset": offset, "timeout": timeout})
        if not response.ok:
            # self.logger.info("failed...")     # ValueError
            raise NotImplementedError

        data = response.json()
        return GetUpdatesResponse(**data)

        # data = self._get(Command.GET_UPDATES, offset=offset, timeout=timeout)
        # return GetUpdatesResponse(**data)

    def get_send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        url = self.get_url("sendMessage")
        response = requests.get(url, params={"chat_id": chat_id, "text": text})
        # response = requests.post(url, params={"chat_id": chat_id, "text": text})
        if not response.ok:
            # self.logger.info("failed...")     # ValueError
            raise NotImplementedError

        data = response.json()
        return SendMessageResponse(**data)

        # data = self._get(Command.SEND_MESSAGE, chat_id=chat_id, text=text)
        # return SendMessageResponse(**data)

    # def _get(self, command: Command, **params) -> dict:
    #     url = self.get_url(command.value)
    #     response = requests.get(url, params=params)
    #     return response.json()

