![](https://github.com/IrinaRostovtseva/foodgram-project/workflows/Foodgram/badge.svg)

# **Foodgram**

Запущенный на сервере проект доступен по ссылке [130.193.45.150](http://130.193.45.150:/)

Дипломный проект в рамках профессии Яндекс.Практикума python-разработчик.
Foodgram - онлайн-сервис, где пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Требования

+  Docker
+  Docker Compose

## Разворачивание проекта на сервере

1.  Склонируйте проект

2.  В корневой директории проекта создайте файл .env со следующим содержимым:

        DB_ENGINE=django.db.backends.postgresql
        DB_NAME=<название-бд>
        DB_USER=<имя-пользователя-бд>
        DB_PASSWORD=<пароль-к-бд>
        DB_HOST=db
        DB_PORT=5432
        POSTGRES_USER=<имя-пользователя-бд-postgresql>
        POSTGRES_PASSWORD=<пароль-к-бд-postgresql>
        EMAIL_HOST=smtp.<email-домен>
        EMAIL_PORT=587
        EMAIL_HOST_USER=<yourusername@youremail.com>
        EMAIL_HOST_PASSWORD=<пароль>


3.  Создайте контейнеры для сервера базы данных и приложения Foodgram

        docker-compose up

4.  Зайдите в контейнер приложения

        docker exec -it <CONTAINER_ID> bash

5.  Выполните миграции

        ./manage.py migrate

6.  Создайте суперпользователя

        ./manage.py createsuperuser
