FROM nginx:1.25-alpine

# Удаляем все дефолтные конфиги
RUN rm -rf /etc/nginx/conf.d/*

# Копируем наш конфиг
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Проверяем конфигурацию при сборке
RUN nginx -t