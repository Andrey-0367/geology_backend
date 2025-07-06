FROM python:3.10-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копирование и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . .
COPY .env /app/.env
# Сборка статики
RUN python manage.py collectstatic --noinput

# Запуск приложения
CMD ["sh", "-c", "python manage.py migrate && gunicorn geology.wsgi:application --bind 0.0.0.0:8000"]
