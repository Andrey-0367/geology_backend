FROM nginx:alpine

# Удаляем дефолтный конфиг
RUN rm /etc/nginx/conf.d/default.conf

# Копируем наш конфиг
COPY nginx.conf /etc/nginx/conf.d/geology.conf

# Явно указываем команду запуска (хотя базовый образ уже имеет CMD)
CMD ["nginx", "-g", "daemon off;"]