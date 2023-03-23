import logging

import requests
from django.conf import settings

from bot.tg.dc import GetUpdatesResponse, SendMessageResponse

logger = logging.getLogger(__name__)


class TgClient:
    """
    Хранит информацию по токену для Телеграм бота, использует long polling подход для обработки сообщений пользователя
    в чате, отправляет ответные сообщения в чате пользователю.
    """
    def __init__(self, token: str | None = None):
        self.token = token if token else settings.BOT_TELEGRAM_TOKEN
        # импортируем телеграм токен из django.conf settings

    def get_url(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self.token}/{method}"

    def get_updates(self, offset: int = 0, timeout: int = 60) -> GetUpdatesResponse:
        url = self.get_url("getUpdates")
        response = requests.get(url, params={"offset": offset, "timeout": timeout})
        if not response.ok:
            logger.info("Failed to obtain response data.")
            raise NotImplementedError

        data = response.json()
        return GetUpdatesResponse(**data)

    def get_send_message(self, chat_id: int, text: str) -> SendMessageResponse:
        url = self.get_url("sendMessage")
        response = requests.get(url, params={"chat_id": chat_id, "text": text})
        if not response.ok:
            logger.info("Failed to obtain response data.")
            raise NotImplementedError

        data = response.json()
        return SendMessageResponse(**data)
