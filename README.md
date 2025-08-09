# Finance API

## Описание:
API для управления финансами, пользователями и платежами.

## Требования:
Python 3.12+
UV
PostgreSQL 13
Docker (для локальной разработки)

## Установка
Клонировать репозиторий:

`git clone https://github.com/vadimkudesnik/pay.git`

Установить зависимости:

`uv sync --lock`

Запуск:

`./main.py`

## Или через Docker:
Инициализая:

`docker-compose up --build`

Запуск:

`docker-compose up`

## Эндпоинты
### Аутентификация

`POST /auth`

Параметры json:

`
{
"email": "email"
"password": "password"
}
`

Ответ:
`
{
  "token": "jwt_token"
}
`
Токен в качестве Authorization Bearer Token надо будет передавать 

### Текущий Пользователь

`GET /api/users/me`

Возвращает информацию о текущем пользователе
Требуется авторизация Authorization Bearer

### Счета текущего пользователя

`GET /users/me/accounts`

Возвращает информацию о счетах текущего пользователя
Требуется авторизация Authorization Bearer

### Платежи текущего пользователя

`GET /users/me/payments`

Возвращает информацию о платежах текущего пользователя
Требуется авторизация Authorization Bearer

## Административные функции
### Все пользователи

`GET /api/users`

Возвращает список всех пользователей
Требуется авторизация Authorization Bearer
Требуется роль администратора

### Полльзоаватель по id

`GET /users/<id:int>`

Возвращает пользователя по id
Требуется авторизация Authorization Bearer
Требуется роль администратора

### Платежи полльзоавтеля по id

`GET /users/<id:int>/payments`

Возвращает платежи пользователя по id
Требуется авторизация Authorization Bearer
Требуется роль администратора

### Счета полльзоавтеля по id

`GET /users/<id:int>/accounts`

Возвращает счета пользователя по id
Требуется авторизация Authorization Bearer
Требуется роль администратора

### Создание нового пользователя

`POST /users/add`

Требуется авторизация Authorization Bearer
Требуется роль администратора

Параметры json:

`
email
password
full_name
is_admin(опционально)
`

### Обновление пользователя

`POST /users/update`

Требуется авторизация Authorization Bearer
Требуется роль администратора

Параметры json:

`
email
password
full_name
is_admin(опционально)
`

### Удаление пользователя

`POST /users/delete`

Требуется авторизация Authorization Bearer
Требуется роль администратора

Параметры json:

`id`


## Тестовые данные
После первого запуска создаются тестовые пользователи:

Администратор:

Email: admin@test.com

Пароль: admin123

Обычный пользователь:

Email: user@test.com

Пароль: user123

Docker
Для локальной разработки рекомендуется использовать Docker:

docker-compose up --build
Доступ к API: http://localhost:8000/api

Доступ к Adminer (для управления БД): http://localhost:8080

Файл с API для Postman: payments.postman_collection.json 

Структура проекта
project/
│
├── app/
├── main.py
├── models.py
├── routes.py
├── config.py
├── utils.py
├── pyproject.toml
├── mypy.ini
├── seed.sql
├── docker/
│ ├── /web/Dockerfile
│ └── /db/Dockerfile
├── docker-compose.yml
├── payments.postman_collection.json
├── LICENSE.md
└── README.md