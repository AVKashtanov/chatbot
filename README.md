# chatbot

Чат бот для бронирования в телеграме.

# Запуск
Первое, что нужно сделать, это клонировать репозиторий:

```sh
$ git clone https://github.com/AVKashtanov/chatbot.git
```

Создайте виртуальную среду, чтобы установить зависимости и активировать ее:

```sh
$ python -m venv venv
$ source venv/bin/activate
```

Затем установите зависимости:

```sh
(venv)$ pip install -r requirements.txt
```
Теперь необходимо добавить файл .env в корневой каталог скопировать в него файл env.example и вписать токен бота.
```python
TELEGRAM_TOKEN=''
```
Как только `pip` завершит загрузку зависимостей:
```sh
(venv)$ python manage.py migrate
(venv)$ python manage.py runserver
```
Далее запуск самого бота:
```sh
(venv)$ python manage.py startbot
```

# Запуск c помощью docker-compose

Аналогично нужно добавить файл .env в корневой каталог скопировать в него уже файл env.prod и вписать токен бота.
```python
TELEGRAM_TOKEN=''
```
Запустить команду:
```sh
$ docker-compose up -d --build
```
