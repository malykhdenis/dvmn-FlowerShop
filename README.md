# Продажа букетов через телеграм-бота

Телеграм-бот для интернет-магазина цветов, с помощью которого можно выбирать букеты, заказывать их и оплачивать онлайн.

## Возможности бота
* Фильтрация букетов по поводу и цене
* Просмотр всех подходящих под критерии поиска букетов
* Заказ конкретного букета с возможностью оплаты онлайн
* Заказ консультации флориста

## Пример взаимодействия с ботом

![FlowerBot-Example](https://github.com/malykhdenis/dvmn-FlowerShop/assets/157053921/c3b50067-f439-4c5c-9cb9-6a0b127e0761)

## Установка

1. Скачайте код с репозитория.
2. Установите Python [3.10.12](https://www.python.org/downloads/release/python-31012/)
3. Установите все необходимые зависимости с помощью `pip` (или `pip3`)

```bash
pip install -r requirements.txt
```

### Задайте переменные окружения в файле `.env`
О том, как получить токен и платёжный токен для телеграм бота, вы можете узнать в [документации к Telegram Bot API](https://core.telegram.org/bots/features#botfather).

```
SECRET_KEY='SECRET_KEY'
TELEGRAM_BOT_TOKEN='TELEGRAM_BOT_TOKEN'  # токен телеграм-бота
PAYMENT_TG_TOKEN='PAYMENT_TG_TOKEN'  # платёжный токен телеграм-бота
```

## Как запустить

1. Наполните базу данных, с которой должен будет работать бот (или используйте нашу [тестовую](https://github.com/malykhdenis/dvmn-FlowerShop/files/14638882/db.zip)), при этом:
    * В базе обязательно должен быть как минимум один курьер и один мастер с id равными 1.
2. Создайте суперпользователя для доступа в Django-админку:
    ```python
    python3 flowershop/manage.py createsuperuser
    ```
3. Создайте примените миграции
    ```python
    python3 flowershop/manage.py makemigrations
    ```
    ```python
    python3 flowershop/manage.py migrate
    ```
4. Запустите сайт Django
    ```python
    python3 manage.py runserver 0:8000
    ```
5. Запустите телеграм-бот:
    ```python
    python3 flowershop/bot/bot.py
    ```
***
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [Devman](dvmn.org).
