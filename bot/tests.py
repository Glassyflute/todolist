from django.test import TestCase


################################################
from bot.tg.client import TgClient

cl = TgClient("6248252954:AAE5J7RpbT3UaVbJLHC0euGlH9Hi2ysZeXE")
# my Tg token here

# Можно получить уведомления с помощью кода:
print(cl.get_updates(offset=0, timeout=60))

# >>> GetUpdatesResponse(ok=True,
# result=[UpdateObj(update_id=503972396,
# message=Message(message_id=332,
# from_=MessageFrom(id=85364161, first_name='Alexander', last_name='Opryshko', username='alexopryshko'),
# chat=Chat(id=85364161, type='private', first_name='Alexander', last_name='Opryshko', username='alexopryshko', title=None),
# text='123'))])

# C:\pythonProject\todolist\venv\Scripts\python.exe C:/pythonProject/todolist/bot/tests.py
# GetUpdatesResponse(ok=True,
# result=[{'update_id': 650945698,
# 'message': {'message_id': 5,
# 'from': {'id': 327134280, 'is_bot': False, 'first_name': 'Yuliya', 'username': 'yuliya_b7', 'language_code': 'ru'},
# 'chat': {'id': 327134280, 'first_name': 'Yuliya', 'username': 'yuliya_b7', 'type': 'private'},
# 'date': 1678539641,
# 'text': 'hi'}}])
#
# Process finished with exit code 0





# Можно отправить сообщение боту с помощью кода
# print(cl.send_message(327134280, "hello, friend"))
# my Tg chat id here
# MessageFrom(id=85364161,

# >>> SendMessageResponse(ok=True,
# result=Message(message_id=334,
# from_=MessageFrom(id=2065163148, first_name='Metaclass', last_name=None, username='metaclassbot'),
# chat=Chat(id=85364161, type='private', first_name='Alexander', last_name='Opryshko', username='alexopryshko', title=None),
# text='hello'))

# C:\pythonProject\todolist\venv\Scripts\python.exe C:/pythonProject/todolist/bot/tests.py
# SendMessageResponse(ok=True,
# result={'message_id': 6,
# 'from': {'id': 6248252954, 'is_bot': True, 'first_name': 'Todolist', 'username': 'goals_tracking_bot'},
# 'chat': {'id': 327134280, 'first_name': 'Yuliya', 'username': 'yuliya_b7', 'type': 'private'},
# 'date': 1678539837,
# 'text': 'hello, friend'})
#
# Process finished with exit code 0


tg_chat_id='327134280'
tg_username='yuliya_b7'

##################################################
# Состояние B = «Пользователь подтвержден »
# if TgUser.tg_user_id:
    # send secondary greeting msg
    # await other user commands == goals/ shows list of goals for user
        # unknown commands ==  ответить отбивкой «неизвестная команда»
        # /create  ==== allows creating a new goal =
            # юзер получает список категорий и выбирает одну
            # если категория корректная, бот сохраняет ее и просит выбрать заголовок цели
            # получив заголовок цели, бот создает задачу (с параметрами по умолчанию) и отправляет ссылку на нее юзеру
        # /cancel == отменяет все и возвращает юзера к начальному выбору категории для создания цели
        # если некорректная категория, то бот просит ввести еще раз категорию




