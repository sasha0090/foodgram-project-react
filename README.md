
# FoodGram - лучший продуктовый помощник ( ͡° ͜ʖ ͡°)
![foodgram workflow](https://github.com/sasha0090/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg) ![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Приложение «Продуктовый помощник»: сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других пользователей. Сервис «Список покупок» позволяет пользователям создавать список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

http://51.250.111.41/recipes


## Описание проекта  
Для бэкенда используется [Django](https://www.djangoproject.com), api написана помощью фреймворка [Django REST Framework](https://www.django-rest-framework.org).  Для основных действий по аутентификации используется библиотека [djoser](https://github.com/sunscrapers/djoser), таких как регистрация, вход/выход в систему, сброс пароля и др.

После пуша в main запускается Workflow: Проходят тесты >>>  Обновляются образы на Docker Hub >>> Деплой на сервер.

Фронтенд - одностраничное приложение на фреймворке  [React](https://ru.reactjs.org/), которое взаимодействует с API через удобный пользовательский интерфейс.

### Инфраструктура
-   Проект работает с СУБД PostgreSQL.
-   Проект запущен на сервере в Яндекс.Облаке в Docker контейнера Контейнеры с проектом обновляется через Docker Hub.
-   В nginx настроена раздача статики, остальные запросы переадресуются в Gunicorn.
-   Данные сохраняются в volumes.

&nbsp;

## Стек технологий
✅ Python
✅ Django
✅ Django REST framework
✅ Postgres
✅ Docker
✅ Github Workflow
✅ Nginx

&nbsp;

## Запуск проекта
Создайте в директории infra .env файл с параметрами:
```
    DB_ENGINE=django.db.backends.postgresql  # указываем, что работаем с postgresql 
    DB_NAME=postgres  # имя базы данных 
    POSTGRES_USER=postgres  # логин для подключения к базе данных 
    POSTGRES_PASSWORD=postgres  # пароль для подключения к БД (установите свой)
    DB_HOST=db  # название сервиса (контейнера) 
    DB_PORT=5432  # порт для подключения к БД
    
    ALLOWED_HOSTS=localhost #Ваши хосты
    SECRET_KEY=KEY # ваш ключ
```

### Через Doсker
Установите и настройте [Doсker](https://www.docker.com/products/docker-desktop/).
Собрать контейнеры можно автоматическом режиме для этого достаточно клонировать только папку infra и заменив в файле docker-compose.yaml:

◾ Запустите docker-compose:
```
docker-compose up -d --build
```
В соберите файлы статики, и запустите миграции командами:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --no-input 
```

◾ Создать суперпользователя можно командой:
```
docker-compose exec web python manage.py createsuperuser
```
◾ Остановить:
```
docker-compose down -v
```

&nbsp;

## Эндпоинты
Список доступных эндпоинтов в проекте.

Действия со значком  🔐  доступны только для авторизованных пользователей с помощью токена.

&nbsp;

### Пользователи

🔷 `api/users/`
> Поддерживаемые методы: GET | POST
 - Список пользователей
 - Регистрация пользователя

&nbsp;

🔷 `api/users/{id}/`
> Поддерживаемые методы: GET
 - Профиль пользователя 🔐

&nbsp;

🔷 `api/users/me/`
> Поддерживаемые методы: GET
 - Текущий пользователь

&nbsp;

🔷 `api/users/set_password/`
> Поддерживаемые методы: POST
 - Изменение пароля

&nbsp;

🔷 `api/auth/token/login/`
> Поддерживаемые методы: POST
 - Получить токен авторизации

&nbsp;

🔷 `api/auth/token/login/`
> Поддерживаемые методы: POST
 - Удаление токена

------------
### Теги

🔷 `api/tags/`
> Поддерживаемые методы: GET
 - Список тегов

&nbsp;

🔷 `api/tags/{id}/`
> Поддерживаемые методы: GET
 - Получение тега

------------
### Рецепты

🔷 `api/recipes/`
> Поддерживаемые методы: GET | POST
 - Список рецептов
 - Создание рецепта 🔐

&nbsp;

🔷 `api/recipes/{id}/`
> Поддерживаемые методы: GET | PATCH | DEL
 - Получение рецепта
 - Обновление рецепта 🔐
 - Удаление рецепта 🔐

------------
### Список покупок 

🔷 `api/recipes/download_shopping_cart/`
> Поддерживаемые методы: GET
 - Скачать список покупок 🔐

&nbsp;

🔷 `api/recipes/{id}/shopping_cart/`
> Поддерживаемые методы: POST | DEL
 - Добавить рецепт в список покупок 🔐
 - Удалить рецепт из списка покупок 🔐


------------
### Избранное

🔷 `api/recipes/{id}/favorite/`
> Поддерживаемые методы: POST | DEL
 - Добавить рецепт в избранное 🔐
 - Удалить рецепт из избранного 🔐

------------
### Подписки

🔷 `api/users/subscriptions/`
> Поддерживаемые методы: GET
 - Подписки текущий пользователя

&nbsp;

🔷 `api/recipes/{id}/favorite/`
> Поддерживаемые методы: POST | DEL
 - Подписаться на пользователя 🔐
 - Отписаться от пользователя 🔐

 ------------
### Ингредиенты

🔷 `api/recipes/{id}/favorite/`
> Поддерживаемые методы: GET
 - Список ингредиентов 🔐

&nbsp;

🔷 `api/recipes/{id}/favorite/`
> Поддерживаемые методы: GET
 - Подписаться на пользователя
 - Получение ингредиента

&nbsp;

## Авторы

Бэк - **[Александр Телепин](https://github.com/sasha0090)**

Фронт - ЯПрактикум
