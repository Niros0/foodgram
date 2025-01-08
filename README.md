# Проект Foodgram

Foodgram — это проект, цель которого предоставить пользователям возможность создавать и хранить рецепты на онлайн-платформе. На этом сайте пользователи могут делиться своими рецептами со всем миром, а также просматривать чужие рецепты. При желании пользователи могут добавлять рецепты в корзину и перед походом в магазин им будет достаточно скачать свою корзину, чтобы получить список покупок в удобном формате. Если пользователь находит интересный рецепт, но не планирует его использовать в ближайшее время, он может добавить его в избранное. Пользователи также могут подписываться на других пользователей и следить за их действиями.

## Технологии
Python
Django
Django REST
PostgreSQL
Docker
Nginx
Gunicorn
GitHub Actions

## Структура проекта
backend - Папка, содержащая код приложения Backend (Django)
docs - Папка, содержащая спецификации API
frontend - Папка, содержащая код приложения Frontend
infra - Папка, содержащая конфигурации приложений и файлы развертывания инфраструктуры для локальной отладки, а также конфигурации nginx
postman_collection - Папка, содержащая коллекцию postman
docker-compose.production.yml - Настройки для развертывания приложения локально
docker-compose.production.yml - Настройки для развертывания приложения через DockerHub

## Чтобы запустить проект на удаленном сервере, выполните следующие шаги:

Клонируйте репозиторий.

```
git clone git@github.com:Niros0/foodgram.git
```

Проверьте, установлен ли у вас Docker.

```
sudo systemctl status docker.
``` 

Создайте новую папку и файл на сервере с помощью команд.

```
mkdir foodgram && cd foodgram && touch .env.
```

Заполните файл .env на основе файла .env.example и скопируйте на сервер файл docker-compose.production.yml.

Запустите проект, выполнив команду:

```
sudo docker compose -f docker-compose.production.yml up -d.
```

Выполните миграции и импортируйте теги и ингредиенты, выполнив команды:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py makemigrations shortener
sudo docker compose -f docker-compose.production.yml exec backend python manage.py makemigrations users
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py makemigrations
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/
```

Также возможно автоматизировать весь процесс развертывания проекта на удаленном сервере с помощью GitHub Actions.