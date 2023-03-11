import logging

from django.core.management.base import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message, GetUpdatesResponse, UpdateObj

logger = logging.getLogger(__name__)

################################################
# Написать manage.py команду runbot для получения уведомлений от бота и отправки в ответ пользователю
# текста, который был в уведомлении — то есть написать своего первого echo-бота.
# После того, как реализуете получения уведомлений из tg (команда запускается, и вы в консоли
# видите сообщения, которые пишете боту), нужно добавить отправку echo-сообщения обратно.
# При запуске команды Python manage.py runbot бот начинает отправлять echo-сообщения в ответ
# на пользовательские сообщения.


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()

    def handle(self, *args, **options):
        offset = 0
        # logger.info("Bot started operating")
        print("Bot started operating")

        while True:
            # res: GetUpdatesResponse = self.tg_client.get_updates(offset=offset)
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                print(f"Original offset: {offset}")
                # logger.info(item)
                offset = item["update_id"] + 1
                print(f"Updated offset: {offset}")
                # logger.info(item["message"])
                print(item["message"])

                # msg_chat_id = item["message"]["chat"]["id"]
                # msg_echo_text = item["message"]["text"]
                # self.tg_client.send_message(chat_id=msg_chat_id, text=msg_echo_text)

                self.handle_echo_message(item["message"])

    def handle_echo_message(self, message: Message):
        # msg_chat_id = message.chat.id
        msg_chat_id = message["chat"]["id"]
        # msg_echo_text = message.text
        msg_echo_text = message["text"]

        # tg_user, created = TgUser.objects.get_or_create(tg_chat_id=msg_chat_id)
        # print(f"Created: {created}")
        #
        # if tg_user.db_user:
        #     print("User is authorized.")
        # else:
        #     print("User is not authorized. Please, insert the verification code provided by "
        #           "the Telegram bot into the application while being logged in.")

        self.tg_client.send_message(chat_id=msg_chat_id, text=msg_echo_text)


# run polling
#
# verification_code_random = TgClient.objects.make_random_password(length=10,
#                                                           allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789")
# # or for User model
#
# while TgClient.objects.filter(verification_code=verification_code_random):
#     verification_code_random = TgClient.objects.make_random_password(length=10,
#                                                                      allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789")
# TgClient.verification_code = verification_code_random

# import telegram.ext
