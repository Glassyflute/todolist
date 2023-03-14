import logging

from django.core.management.base import BaseCommand

from bot.models import TgUser
from bot.tg.client import TgClient
from bot.tg.dc import Message
from goals.models import Goal, GoalCategory

logger = logging.getLogger(__name__)


USER_NOT_IN_DB = "User is not authorized. Bot needs to generate Verification code and send to user."
# logger.info("User is not authorized. Bot needs to generate Verification code and send to user. %s", "user_not_in_db")

USER_IN_DB_NOT_AUTHORIZED = "User is in database but is not authorized. Bot provided verification code to user and " \
                            "expects the user to link the Telegram user with DB user data via the Todolist" \
                            " web application."
GREETING_UNAUTH_USER = f"Greetings, User. Please, verify your account. For proper authorization " \
                         "insert the verification code provided by the Telegram bot into the application " \
                         "while being logged in."
USER_IS_AUTHORIZED = "User is authorized."

BOT_SENDS_ALL_GOAL_TITLES = "Bot successfully sent the list of goal titles to the User."
USER_CANCELLED_OPERATION = "User cancelled the operation by sending /cancel command to bot."
BOT_SENDS_ALL_CATEGORIES_TITLES = "Bot successfully sent all titles for goal categories to user and asked User " \
                                  "to proceed with selecting a category."
BOT_RECEIVED_UNKNOWN_COMMAND = "Bot received an unknown command from User. No actions performed."
USER_INITIATED_GOAL_CREATION = "Bot received /create command from User to proceed with creation of a new goal."
BOT_AWAITING_CATEGORY = "Bot expects category name from User from the list of available categories."
USER_SELECTED_CATEGORY = "User successfully selected a category for the goal from the list of available categories."
BOT_SAVED_CATEGORY = "Bot saved the selected category as first step in goal creation process."

BOT_AWAITING_GOAL_TITLE = "Bot expects goal title from User."
USER_SELECTED_GOAL_TITLE = "User provided goal title to bot."
BOT_SAVED_GOAL_TITLE = "Bot saved the goal title as part of goal creation process."

BOT_CREATED_NEW_GOAL = "Bot created the goal and saved goal data in the database. Bot provided link to Web " \
                       "app to User."

user_states: dict[str, dict] = {"327134280": {}}


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
                logger.info("UpdateObj is %s", item)
                offset = item["update_id"] + 1
                if "message" in item.keys():
                    message: Message = item["message"]
                else:
                    message: Message = item["edited_message"]
                logger.info("Message is %s", message)

                self.handle_message(message=message)
                logger.info("Bot replied with message")

    def handle_message(self, message: Message):
        msg_chat_id: int = message["chat"]["id"]

        msg_echo_text: str = message["text"]
        tg_username = message["chat"]["username"]

        tg_user, created = TgUser.objects.get_or_create(tg_chat_id=msg_chat_id)
        logger.info(f"Created: {created} for tg_chat_id <{msg_chat_id}>")
        # logger.info("Created: %s" "for tg_chat_id %s", created, msg_chat_id)

        if tg_user.user:
            self.handle_authorized_user(tg_user=tg_user, message=message)

        else:
            self.handle_unauthorized_user(tg_user=tg_user, message=message)

        # self.tg_client.get_send_message(chat_id=msg_chat_id, text=msg_echo_text)

    def handle_unauthorized_user(self, tg_user: TgUser, message: Message):
        logger.info(USER_NOT_IN_DB)
        msg_chat_id = message["chat"]["id"]

        self.tg_client.get_send_message(chat_id=msg_chat_id, text=GREETING_UNAUTH_USER)

        tg_username = message["chat"]["username"]
        updated_username = tg_user.assign_tg_username(username=tg_username)

        verification_code = tg_user.assign_verification_code()
        verification_msg = f"Verification code: {verification_code}"
        tg_user.save()

        self.tg_client.get_send_message(chat_id=msg_chat_id, text=verification_msg)
        logger.info(USER_IN_DB_NOT_AUTHORIZED)

    def handle_authorized_user(self, tg_user: TgUser, message: Message):
        logger.info(USER_IS_AUTHORIZED)
        tg_username = message["chat"]["username"]
        msg_chat_id = message["chat"]["id"]
        msg_text = message["text"]

        msg_auth_greeting = f"{tg_username}, бот ожидает информацию."
        self.tg_client.get_send_message(chat_id=msg_chat_id, text=msg_auth_greeting)

        allowed_commands = ["/goals", "/create", "/cancel"]

        logger.info("user_states is %s", user_states)

        if "/goals" in msg_text:
            self.handle_goals(tg_user=tg_user, message=message)
            logger.info(BOT_SENDS_ALL_GOAL_TITLES)

        elif "/cancel" in msg_text:
            if "user" in user_states["327134280"]:
                del user_states["327134280"]["user"]
            self.tg_client.get_send_message(chat_id=msg_chat_id, text="Операция отменена")
            logger.info(USER_CANCELLED_OPERATION)

        elif ("user" not in user_states["327134280"]) and (msg_text not in allowed_commands):
            self.tg_client.get_send_message(chat_id=msg_chat_id, text="Неизвестная команда")
            logger.info(BOT_RECEIVED_UNKNOWN_COMMAND)

        elif "/create" in msg_text:
            logger.info(USER_INITIATED_GOAL_CREATION)
            self.tg_client.get_send_message(chat_id=msg_chat_id, text="Список ваших категорий ниже.")

            goal_categories_data = self.handle_db_categories(tg_user=tg_user)
            for category_item in goal_categories_data:
                self.tg_client.get_send_message(chat_id=msg_chat_id, text=category_item)
            self.tg_client.get_send_message(chat_id=msg_chat_id, text="Выберите категорию для новой цели.")
            logger.info(BOT_SENDS_ALL_CATEGORIES_TITLES)

            if "user" not in user_states["327134280"]:
                user_states["327134280"]["user"] = tg_user.user
                logger.info("user_states is %s", user_states)
                logger.info("User assigned to dict")
                logger.info(BOT_AWAITING_CATEGORY)

        elif (msg_text not in allowed_commands) and (user_states["327134280"]["user"]) and \
                ("category" not in user_states["327134280"]):
            category = self.handle_save_category(tg_user=tg_user, message=message)
            if category:
                user_states["327134280"]["category"] = category
                logger.info("user_states is %s", user_states)
                logger.info(BOT_SAVED_CATEGORY)
                logger.info(BOT_AWAITING_GOAL_TITLE)
                self.tg_client.get_send_message(chat_id=msg_chat_id, text="Категория выбрана. Введите заголовок цели.")

        elif (msg_text not in allowed_commands) and (user_states["327134280"]["user"]) and \
                (user_states["327134280"]["category"]) and ("goal_title" not in user_states["327134280"]):
            user_states["327134280"]["goal_title"] = msg_text
            logger.info("user_states is %s", user_states)
            logger.info(BOT_SAVED_GOAL_TITLE)

            goal = Goal.objects.create(title=user_states["327134280"]["goal_title"],
                                       user=user_states["327134280"]["user"],
                                       category=user_states["327134280"]["category"])
            self.tg_client.get_send_message(chat_id=msg_chat_id,
                                            text="Цель создана в БД. Ссылка на приложение: http://127.0.0.1")
            logger.info(BOT_CREATED_NEW_GOAL)

    def handle_save_category(self, tg_user: TgUser, message: Message):
        msg_text = message["text"]
        msg_chat_id = message["chat"]["id"]

        goal_categories_data = self.handle_db_categories(tg_user=tg_user)
        if msg_text in goal_categories_data:
            category_name = msg_text
            user_categories = tg_user.show_user_goal_categories()
            category_data = user_categories.get(title=category_name)
            return category_data

        self.tg_client.get_send_message(chat_id=msg_chat_id, text="Ошибка. Введите корректную категорию.")

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

        return categories_titles

    def handle_db_goals(self, tg_user: TgUser):
        user_goals = tg_user.show_user_goals()

        goals_titles = []
        for goal_item in user_goals:
            goals_titles.append(goal_item.title)

        return goals_titles
