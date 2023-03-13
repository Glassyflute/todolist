import logging

from django.core.management.base import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message
from goals.models import Goal

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tg_client = TgClient()

    def handle(self, *args, **options):
        offset = 0
        logger.info("Bot started operating")

        while True:
            res = self.tg_client.get_updates(offset=offset)
            for item in res.result:
                logger.info(f"UpdateObj is {item}")
                offset = item["update_id"] + 1
                message: Message = item["message"]
                logger.info(f"Message is {message}")

                self.handle_message(message=message)
                logger.info("Bot replied with message")

    def handle_message(self, message: Message):
        msg_chat_id: int = message["chat"]["id"]

        msg_echo_text: str = message["text"]
        tg_username = message["chat"]["username"]

        tg_user, created = TgUser.objects.get_or_create(tg_chat_id=msg_chat_id)
        logger.info(f"Created: {created} for tg_chat_id <{msg_chat_id}>")

        if tg_user.user:
            self.handle_authorized_user(tg_user=tg_user, message=message)
            # # /goals here
            # self.tg_client.get_send_message(chat_id=msg_chat_id, text="goals 0")
            # self.handle_goals(tg_user=tg_user, message=message)
        else:
            self.handle_unauthorized_user(tg_user=tg_user, message=message)

        # self.tg_client.get_send_message(chat_id=msg_chat_id, text=msg_echo_text)

    def handle_unauthorized_user(self, tg_user: TgUser, message: Message):
        logger.info("User is not authorized. Need to generate Verification code and link "
                    "the Telegram user with DB user via the Todolist web application.")
        msg_chat_id = message["chat"]["id"]
        greetings_text = f"Greetings, User. Please, verify your account. For proper authorization " \
                         "insert the verification code provided by the Telegram bot into the application " \
                         "while being logged in."
        self.tg_client.get_send_message(chat_id=msg_chat_id, text=greetings_text)

        tg_username = message["chat"]["username"]
        updated_username = tg_user.assign_tg_username(username=tg_username)

        verification_code = tg_user.assign_verification_code()
        verification_msg = f"Verification code: {verification_code}"
        tg_user.save()

        self.tg_client.get_send_message(chat_id=msg_chat_id, text=verification_msg)

    def handle_authorized_user(self, tg_user: TgUser, message: Message):
        logger.info("User is authorized.")
        tg_username = message["chat"]["username"]
        msg_chat_id = message["chat"]["id"]

        msg_auth_greeting = f"Welcome to chat, {tg_username}"
        self.tg_client.get_send_message(chat_id=msg_chat_id, text=msg_auth_greeting)

        self.tg_client.get_send_message(chat_id=msg_chat_id, text="Выберите действие")

        self.handle_goals(tg_user=tg_user, message=message)

    # for /start, /help === show original greeting message or list of functions

    def handle_goals(self, tg_user: TgUser, message: Message):
        msg_text = message["text"]
        msg_chat_id = message["chat"]["id"]
        self.tg_client.get_send_message(chat_id=msg_chat_id, text="goals p1")

        if "/goals" in msg_text:
            self.tg_client.get_send_message(chat_id=msg_chat_id, text="goals 2 - asked")
            goals_data = self.handle_db_goals(tg_user=tg_user)
            self.tg_client.get_send_message(chat_id=msg_chat_id, text="goals 3 - данные загружены")

            for goal_item in goals_data:
                self.tg_client.get_send_message(chat_id=msg_chat_id, text=goal_item)

            self.tg_client.get_send_message(chat_id=msg_chat_id, text="goals 4 - показ данных завершен")
        else:
            self.tg_client.get_send_message(chat_id=msg_chat_id, text="Неизвестная команда")

    def handle_db_goals(self, tg_user: TgUser):
        user_goals = tg_user.show_user_goals()

        goals_titles = []
        for goal_item in user_goals:
            goals_titles.append(goal_item.title)

        len_goals = len(user_goals)

        print(f" Goal titles: {goals_titles}")
        print(f"Number of goals: {len_goals}")

        return goals_titles


