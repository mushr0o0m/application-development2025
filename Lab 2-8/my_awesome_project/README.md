# my_awesome_project

Проект — асинхронный сервер API для простого магазина (пользователи, продукты, заказы, отчёты).
Сервис написан на Python с использованием Litestar (подобно FastAPI/Starlette) и SQLAlchemy (async). Миграции управляются через Alembic. В проекте есть скрипты для заполнения тестовых данных и набор тестов на pytest.

**Ключевые технологии**
- Python 3.10+ (рекомендуется 3.11)
- Litestar
- SQLAlchemy (async)
- Alembic
- asyncpg / psycopg2-binary (для PostgreSQL)
- uvicorn (ASGI-сервер)
- pytest для тестов
- Docker / docker-compose (опционально)

**Структура проекта** (корневые файлы и важные каталоги)
- `main.py`: точка входа — создаёт приложение Litestar и запускает uvicorn.
- `alembic.ini`, `alembic/`: конфигурация и миграции базы данных.
- `app/`: основная логика — модели, репозитории, сервисы, контроллеры.
- `seed.py`, `seed_all_data.py`: скрипты для заполнения БД тестовыми данными.
- `run_tests.sh`: удобный shell-скрипт для запуска тестов по файлам.
- `Dockerfile`, `docker-compose.yaml`: контейнеризация.

**Переменные окружения**
- `DATABASE_URL`: обязательна для запуска приложения. Примеры:
  - PostgreSQL: `postgresql+asyncpg://user:pass@localhost:5432/dbname`
  - SQLite (локально для быстрых тестов): `sqlite+aiosqlite:///./test.db`

Внимание: `main.py` требует, чтобы `DATABASE_URL` было задано — при его отсутствии приложение завершится с `RuntimeError`. Даже при использовании SQLite нужно экспортировать `DATABASE_URL` явно, например:

```zsh
export DATABASE_URL="sqlite+aiosqlite:///./test.db"
```

- `ALEMBIC_DATABASE_URL` (опционально): можно использовать для переопределения URL, который Alembic использует для миграций. Это полезно, если вы хотите отдельно указать синхронный URL для миграций (Alembic сам убирает `+asyncpg` при необходимости).

Пример (запустить миграции с явным URL для alembic):

```zsh
ALEMBIC_DATABASE_URL="postgresql://user:pass@localhost:5432/dbname" alembic upgrade head
```


**Установка и локальная разработка**
- Создайте виртуальное окружение и установите зависимости:

```zsh
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

- Экспортируйте `DATABASE_URL` в окружение перед запуском (пример для PostgreSQL):

```zsh
export DATABASE_URL="postgresql+asyncpg://myuser:mypassword@localhost:5432/mydb"
```

- Создайте базу данных (если используете Postgres) и выполните миграции.

Пример создания БД в Postgres (локально):

```zsh
createdb mydb
# или через psql
psql -c 'create database mydb'
```

Затем примените миграции:

```zsh
alembic upgrade head
```

- Для локальной быстрой проверки без Postgres можно использовать sqlite (файл `test.db` в проекте):

```zsh
export DATABASE_URL="sqlite+aiosqlite:///./test.db"
# В случае sqlite -- миграции с alembic остаются предпочтительными, но seed-скрипты автоматически создают таблицы через SQLAlchemy metadata
python seed.py
```

**Сидирование тестовых данных**
- Добавить минимальный набор пользователей и адресов:

```zsh
python seed.py
```

- Добавить пользователей, продукты и заказы (более полный набор):

```zsh
python seed_all_data.py
```

**Запуск приложения**
- Запустить напрямую (использует uvicorn из `main.py`):

```zsh
python main.py
```

- Или через uvicorn напрямую (полезно для autoreload в разработке):

```zsh
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

После запуска API будет доступно по `http://localhost:8000` (порт можно изменить).

**Тесты**
- Запустить все тесты через pytest:

```zsh
pytest -q
```

- Или воспользоваться удобным скриптом, который запускает тесты по каждому файлу в `tests/` последовательно:

```zsh
./run_tests.sh
```

Примечание: перед первым запуском убедитесь, что скрипт исполняемый:

```zsh
chmod +x run_tests.sh
```

**Миграции Alembic**
- Создать новую миграцию (автогенерация):

```zsh
alembic revision --autogenerate -m "описание"
```

- Применить миграции:

```zsh
alembic upgrade head
```

Примечание: Alembic читает конфигурацию из `alembic.ini`. Убедитесь, что `sqlalchemy.url` настроен либо в `alembic.ini`, либо используйте `DATABASE_URL` окружением. Для удобства можно задать `ALEMBIC_DATABASE_URL` (env var) — `alembic/env.py` поддерживает это и при необходимости корректно переводит `postgresql+asyncpg://` в синхронный URL.

**Docker / docker-compose**
- Запуск через Docker Compose (создаёт контейнеры, DB и сервисы согласно `docker-compose.yaml`):

```zsh
docker-compose up --build
```

- Остановить и удалить контейнеры:

```zsh
docker-compose down
```

(Если контейнеры требуют переменных окружения, задайте их через `.env` или в `docker-compose.yaml`.)

Файл `.env.example` добавлен в корень проекта — скопируйте его в `.env` и отредактируйте под своё окружение.

**RabbitMQ / Redis / очереди**
- В проекте присутствует код для работы с RabbitMQ и Redis (см. `scripts/check_rabbit.py`, зависимости `pika`, `redis`). Для использования очередей убедитесь, что соответствующие службы запущены и доступны по переменным окружения, которые вы используете в конфигурации.

**Отладка и распространённые проблемы**
- Ошибка: `RuntimeError: DATABASE_URL is not set.` — установите переменную `DATABASE_URL` как показано выше.
- Ошибки подключения к базе — проверьте, что сервер БД запущен, параметры доступа и firewall/порт.
- Миграции не применились — убедитесь, что alembic настроен на ту же БД, что и `DATABASE_URL`.
- Тесты зависят от базы — некоторые тесты могут требовать рабочую БД или корректный `DATABASE_URL`.

**Краткий обзор важных файлов**
- `main.py` — создание приложения, DI-провайдеры, запуск uvicorn.
- `app/models/` — ORM модели (User, Product, Order и т.д.).
- `app/controllers/` — HTTP-обработчики / маршруты.
- `app/services/` — бизнес-логика.
- `app/repositories/` — доступ к базе данных и операции CRUD.
- `alembic/versions/` — уже существующие миграции.

Если нужно, могу:
- Добавить пример `docker-compose.override.yml` для локальной разработки.
- Прописать точный .env-файл с рекомендуемыми переменными.
- Запустить тесты или миграции у вас в окружении (подскажу команды).

---
Файл `README.md` создан в корне проекта — при желании могу отредактировать или расширить конкретные разделы (например, пример `.env` или детали конфигурации Alembic).