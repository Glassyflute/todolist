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
                if "message" in item.keys():
                    message: Message = item["message"]
                else:
                    message: Message = item["edited_message"]

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
        msg_text = message["text"]

        msg_auth_greeting = f"{tg_username}, бот ожидает информацию."
        self.tg_client.get_send_message(chat_id=msg_chat_id, text=msg_auth_greeting)

        # self.tg_client.get_send_message(chat_id=msg_chat_id, text="Выберите действие")
        # prelim_dict = {"category": "", "goal": ""}
        # # tg_user.create_goal_via_tg()
        # allowed_commands = ["/goals", "/create", "/cancel"]

        goal_categories_data = self.handle_db_categories(tg_user=tg_user)

        if "/goals" in msg_text:
            self.handle_goals(tg_user=tg_user, message=message)
        elif "/cancel" in msg_text:
            self.tg_client.get_send_message(chat_id=msg_chat_id, text="Операция отменена")

        elif "/create" in msg_text:
            self.tg_client.get_send_message(chat_id=msg_chat_id, text="Список ваших категорий ниже.")
            goal_categories_data = self.handle_db_categories(tg_user=tg_user)
            # self.tg_client.get_send_message(chat_id=msg_chat_id, text="категории загружены 1")
            for category_item in goal_categories_data:
                self.tg_client.get_send_message(chat_id=msg_chat_id, text=category_item)
            self.tg_client.get_send_message(chat_id=msg_chat_id, text="Выберите категорию для новой цели.")

        else:
            self.tg_client.get_send_message(chat_id=msg_chat_id, text="Неизвестная команда")

        # Вариант 1: со словарем - не работает. И "Неизвестная команда" неясно, как обрабатывать.
        # elif msg_text not in allowed_commands:
        #
        #     for category in goal_categories_data:
        #         if prelim_dict["category"] is not None:
        #             prelim_dict["goal"] = msg_text
        #             print(f"Goal is {msg_text}")
        #             self.tg_client.get_send_message(chat_id=msg_chat_id, text="Название цели сохранено.")
        #
        #         if category in msg_text:
        #             # бот "сохраняет" категорию
        #             prelim_dict["category"] = category
        #             print(f"Category is {category}")
        #             self.tg_client.get_send_message(chat_id=msg_chat_id, text="Категория выбрана. Введите заголовок цели.")
        #             # return prelim_dict
        #         # else:
        #         #     self.tg_client.get_send_message(chat_id=msg_chat_id, text="Ошибка. Введите корректную категорию.")
        #
        #         if (prelim_dict["category"] is not None) and (prelim_dict["goal"] is not None):
        #             goal = Goal.objects.create(title=prelim_dict["goal"], user=tg_user.user,
        #                                        category=prelim_dict["category"])
        #             self.tg_client.get_send_message(chat_id=msg_chat_id,
        #                                             text="Цель создана в БД. Ссылка на приложение: http://127.0.0.1")


            # Вар. 2 - последовательные messages: новые message2 и далее. неясно, как их получать последовательно.
            # category = self.handle_save_category(tg_user=tg_user, message=message2)
            # self.tg_client.get_send_message(chat_id=msg_chat_id, text="Категория создана")
            # goal_title = self.handle_new_goal_name(tg_user=tg_user, message=message3)
            # self.tg_client.get_send_message(chat_id=msg_chat_id, text="Название цели есть.")
            # goal = Goal.objects.create(title=goal_title, user=tg_user.user, category=category)
            # self.tg_client.get_send_message(chat_id=msg_chat_id,
            #                                 text="Цель создана в БД. Ссылка на приложение: http://127.0.0.1")


    def handle_goals(self, tg_user: TgUser, message: Message):
        msg_text = message["text"]
        msg_chat_id = message["chat"]["id"]
        self.tg_client.get_send_message(chat_id=msg_chat_id, text="Список ваших целей ниже.")
        goals_data = self.handle_db_goals(tg_user=tg_user)
        for goal_item in goals_data:
            self.tg_client.get_send_message(chat_id=msg_chat_id, text=goal_item)

        self.tg_client.get_send_message(chat_id=msg_chat_id,
                                        text="Для создания новой цели, используйте команду /create")

    def handle_db_categories(self, tg_user: TgUser):
        user_categories = tg_user.show_user_goal_categories()

        categories_titles = []
        for category_item in user_categories:
            categories_titles.append(category_item.title)

        # len_categories = len(categories_titles)
        # print(f" Categories: {categories_titles}")
        # print(f"Number of categories: {len_categories}")
        return categories_titles

    def handle_db_goals(self, tg_user: TgUser):
        user_goals = tg_user.show_user_goals()

        goals_titles = []
        for goal_item in user_goals:
            goals_titles.append(goal_item.title)

        # len_goals = len(user_goals)
        # print(f" Goal titles: {goals_titles}")
        # print(f"Number of goals: {len_goals}")
        return goals_titles

    # def handle_save_category(self, tg_user: TgUser, message: Message):
    #     msg_text = message["text"]
    #     msg_chat_id = message["chat"]["id"]
    #
    #     if "/cancel" in msg_text:
    #         self.tg_client.get_send_message(chat_id=msg_chat_id, text="Операция отменена")
    #
    #     goal_categories_data = self.handle_db_categories(tg_user=tg_user)
    #     if msg_text in goal_categories_data:
    #         # бот "сохраняет" категорию
    #         category = msg_text
    #         self.tg_client.get_send_message(chat_id=msg_chat_id, text="Категория выбрана. Введите заголовок цели.")
    #         return category
    #     else:
    #         self.tg_client.get_send_message(chat_id=msg_chat_id, text="Ошибка. Введите корректную категорию.")

    # def handle_new_goal_name(self, tg_user: TgUser, message: Message):
    #     msg_text = message["text"]
    #     msg_chat_id = message["chat"]["id"]
    #
    #     if "/cancel" in msg_text:
    #         self.tg_client.get_send_message(chat_id=msg_chat_id, text="Операция отменена")
    #
    #     goal_title = msg_text
    #     self.tg_client.get_send_message(chat_id=msg_chat_id, text="Название цели сохранено.")
    #     return goal_title
