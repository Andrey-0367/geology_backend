#!/bin/bash
set -e  # Остановить скрипт при любой ошибке

echo "Ожидание запуска PostgreSQL..."
until PGPASSWORD=$DB_PASSWORD psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -c '\q' > /dev/null 2>&1; do
  echo "PostgreSQL недоступен, повторная проверка через 1 секунду..."
  sleep 1
done
echo "PostgreSQL запущен!"

echo "Создание миграций..."
python manage.py makemigrations --noinput  # --noinput для автоматизации

echo "Применение миграций..."
python manage.py migrate --noinput

echo "Сбор статических файлов..."
python manage.py collectstatic --noinput --clear

# Запуск Gunicorn вместо сервера разработки
echo "Запуск Gunicorn..."
exec gunicorn \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  your_project.wsgi:application