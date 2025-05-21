#!/bin/bash

echo "Ожидание запуска PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  echo "PostgreSQL еще не доступен - ожидание..."
  sleep 1
done
echo "PostgreSQL запущен"

echo "Создание миграций..."
python manage.py makemigrations

echo "Применение миграций..."
python manage.py migrate

echo "Сбор статических файлов..."
python manage.py collectstatic --noinput

echo "Запуск сервера разработки Django..."
exec python manage.py runserver 0.0.0.0:8000