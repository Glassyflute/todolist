# TODOLIST 

#### Приложение для постановки и работы с целями, отслеживания прогресса по целям.

***
#### Описание проекта

В проекте используется Python3.10, Django, PostgreSQL, Poetry, Nginx, frontend image: sermalenk/skypro-front:lesson-38.
Файлы poetry.lock, pyproject.toml показывают информацию по зависимостям и установленным пакетам. 

Информация по запуску базы данных PostgreSQL указана в docker-compose файле.
Информация по конфигурации приложения Todolist и значениям для переменных окружения указана в файле .env.
Данные в БД сохраняются с помощью volumes в docker-compose файле. 

Создана кастомная модель пользователя (наследник от AbstractUser) в приложении Core. Создать пользователя с 
доступом в Django admin можно с помощью команды `createsuperuser`. Управление пользователями 
осуществляется из Django admin. 

Миграции для создания моделей запускаются из корневой директории в терминале командой
`python manage.py makemigrations`. 

Миграции накатываются в модели командой `python manage.py migrate`. Проверка на необходимость накатывания миграций
осуществляется в файле `entrypoint.sh` в корневой директории проекта и запускается внутри Dockerfile при сборке в 
разделе ENTRYPOINT. 

Проект запускается через команду `runserver` (файл manage.py в корневой директории проекта). 
 
Папка Deploy в корне проекта включает docker-compose файл, файл .env, nginx.conf для автоматической сборки и деплоя
приложения на сервер с помощью GitHub Actions. Все чувствительные данные (логины/пароли и т.п.) указаны через 
переменные окружения, которые зашифрованы с помощью библиотеки `ansible-vault-win` в файле .env внутри папки Deploy; 
настоящие значения хранятся в secrets в GitHub.

Виртуальная машина работает по адресу домена: `ybobir.ga`, либо по публ IPv4: 158.160.60.182. 

Для написания API использовалась Django REST Framework (DRF). Реализована регистрация пользователя с последующей 
аутентификацией. Аутентификация пользователя и вход в приложение осуществляется по логину и паролю зарегистрированного 
пользователя, либо через социальную сеть VK с помощью протокола OAuth2 и библиотеки `social-auth-app-django`.

Библиотека `django.contrib.auth` позволяет проводить аутентификацию пользователя с помощью механизма
`django.contrib.auth.authenticate` и, в случае корректного username и password, запоминать пользователя с помощью
`django.contrib.auth.login`. Logout пользователя реализован с помощью HTTP метода DELETE, который удаляет
информацию о текущей сессии пользователя: таким образом, пользователь выходит из текущего аккаунта, но его данные 
остаются в БД. 

Реализована возможность сменить пароль путем ввода старого и нового значений пароля пользователем. Пароли 
пользователей в БД хранятся в зашифрованном виде.

Графический интерфейс работы с целями представляет собой набор из нескольких досок, при этом, каждая из досок может
включать список целей в назначенной категории и комментариев к каждой цели, созданных пользователями. 
Доска разделена на три колонки со статусами "К выполнению", "В работе", "Выполнено". 
В приложении goals реализованы функции сортировки, фильтрации и поиска с помощью `django-filter`. 

Достигнутые (удаленные) цели или категории получают статус "В архиве" и не показываются пользователю, однако не 
удаляются из БД. Комментарии пользователей удаляются полностью. При удалении доски находящиеся в ней цели и категории
переходят в статус "В архиве" и не показываются пользователю. 

Дополнительная информация по моделям, сериализаторам, вьюшкам и url-адресам указана в файлах внутри приложений 
`core` (информация по пользователю) и `goals` (информация по целям, категориям, комментариям, доскам). 
Для приложений core и goals реализована админка с возможностью работать со всеми созданными сущностями. 

Работа с доступами в DRF осуществляется с помощью системы permissions. Работа с досками, целями требует аутентификации
пользователя через `permissions.IsAuthenticated`, далее применяются дополнительные ограничения:
- Изменять/удалять доску имеет право только создатель доски. 
- Менять/удалять категорию или цель, принадлежащую конкретной доске, имеет право создатель доски или редактор. 
- Пользователь может создавать комментарии к целям, в досках которых он имеет роль "владелец" или "редактор".
- Пользователь не может редактировать или удалять чужие комментарии. 
- Пользователь не видит информацию из тех досок, в которых он не является участником. 

Чтобы обеспечить пользователю возможность просматривать и создавать цели без доступа к компьютеру, проект был
дополнен приложением Бот в мессенджере Телеграм, написанным вручную. Уведомления из Телеграм пользователь получает 
через процесс long polling и с помощью обращения к Telegram API через библиотеку `requests`. Ответы Telegram API 
описаны с помощью датаклассов. Кастомная django-admin команда на запуск бота `python manage.py runbot` (файл 
`bot/management/commands/runbot.py`) инициирует запуск Телеграм бота. 

Аккаунт Телеграм пользователя привязан к аккаунту приложения. 
После подтверждения аккаунта Телеграм в web-приложении, аутентифицированный пользователь имеет возможность через 
Телеграм бота просматривать список своих актуальных целей, а также создавать новую цель с присвоением категории из 
списка существующих в БД категорий (другие параметры создания цели используются по умолчанию). Созданная пользователем
цель записывается в БД и отображается в web-приложении. 

Для приложения `bot` реализована админка с возможностью работать с созданной сущностью. 

Код покрыт 30+ автотестами. Запустить все тесты и увидеть перечень тестов можно с помощью команды в терминале
`python manage.py test -v 2`. Тесты по классам User, Board, Goal, GoalComment, GoalCategory наследуются от
`APITestCase` и проверяют успешное создание, просмотр, редактирование и удаление в тестовой БД новых целей, 
категорий, досок, комментариев и пользователя и успех операций во вьюшках на основе статус-кодов. 
Также тесты по каждому классу можно запустить с помощью `pytest`, выбрав соответствующую конфигурацию
через опцию Edit Configurations в PyCharm и нажав на кнопку Run в файле слева от названия нужного класса. 
