FROM python:3.13

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Установка утилиты netcat (nc) для проверки доступности БД в entrypoint
RUN apt-get update \
  && apt-get install -y --no-install-recommends netcat-openbsd \
  && rm -rf /var/lib/apt/lists/*
# Копирование приложения
COPY . .

# Настройка миграций
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
