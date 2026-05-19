# Инструкция по развертыванию QGIS Web Platform

## Быстрый старт

### 1. Подготовка окружения

```bash
# Скопируйте файл переменных окружения
cp .env.example .env

# Отредактируйте .env файл с вашими параметрами
nano .env
```

**Важно:** Обязательно измените все пароли и секретные ключи в production!

### 2. Генерация секретного ключа

```bash
# Сгенерируйте случайный SECRET_KEY
openssl rand -hex 32
```

Вставьте полученное значение в `.env` файл.

### 3. Запуск через Docker Compose

```bash
# Сборка и запуск всех сервисов
docker-compose up -d --build

# Проверка статуса контейнеров
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

### 4. Доступ к сервисам

После запуска сервисы будут доступны по адресам:

- **Фронтенд**: http://localhost
- **Backend API**: http://localhost/api
- **GeoServer**: http://localhost/geoserver (логин: admin, пароль из .env)
- **База данных**: localhost:5432 (не рекомендуется открывать в production)

### 5. Первоначальная настройка GeoServer

1. Войдите в GeoServer: http://localhost/geoserver/web
2. Создайте новое рабочее пространство
3. Добавьте хранилище данных PostgreSQL/PostGIS
4. Опубликуйте слои

## Production развертывание

### Настройка SSL/TLS

#### Вариант 1: Self-signed сертификаты (для тестирования)

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

#### Вариант 2: Let's Encrypt (для production)

```bash
# Установите certbot
apt-get install certbot python3-certbot-nginx

# Получите сертификаты
certbot certonly --standalone -d your-domain.com

# Скопируйте сертификаты в папку nginx/ssl
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

Не забудьте раскомментировать строки SSL в `nginx/nginx.conf`.

### Обновление конфигурации Nginx для production

Отредактируйте `nginx/nginx.conf`:

1. Раскомментируйте строки SSL (443 порт)
2. Укажите пути к вашим SSL сертификатам
3. Измените `server_name` на ваш домен

### Firewall настройки

```bash
# Разрешите только необходимые порты
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw deny 5432/tcp   # PostgreSQL (доступ только изнутри)
ufw deny 6379/tcp   # Redis (доступ только изнутри)
ufw deny 8080/tcp   # GeoServer (доступ через nginx)
ufw enable
```

## Мониторинг и обслуживание

### Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f nginx
```

### Резервное копирование базы данных

```bash
# Создать дамп
docker-compose exec db pg_dump -U qgis_admin gis_platform > backup_$(date +%Y%m%d).sql

# Восстановить из дампа
cat backup_20240101.sql | docker-compose exec -T db psql -U qgis_admin gis_platform
```

### Обновление приложения

```bash
# Остановка сервисов
docker-compose down

# Сборка новых образов
docker-compose build --no-cache

# Запуск обновленных сервисов
docker-compose up -d

# Очистка старых образов
docker image prune -f
```

## Масштабирование

### Увеличение количества workers backend

В `docker-compose.yml` измените команду backend:

```yaml
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 8
```

### Добавление реплик

Для production рассмотрите использование Docker Swarm или Kubernetes для автоматического масштабирования.

## Безопасность

### Обязательные действия для production:

1. ✅ Изменить все пароли по умолчанию
2. ✅ Настроить HTTPS (SSL/TLS)
3. ✅ Ограничить доступ к базе данных (только из внутренней сети)
4. ✅ Настроить firewall
5. ✅ Включить rate limiting (уже настроено в nginx)
6. ✅ Регулярно обновлять образы Docker
7. ✅ Настроить мониторинг и алерты
8. ✅ Регулярное резервное копирование

### Рекомендуемые дополнительные меры:

- Настроить Fail2Ban
- Использовать secrets management (HashiCorp Vault, AWS Secrets Manager)
- Включить audit logging
- Настроить WAF (Web Application Firewall)

## Устранение неполадок

### Контейнер не запускается

```bash
# Проверить логи
docker-compose logs <service_name>

# Проверить использование ресурсов
docker stats
```

### Проблемы с подключением к базе данных

```bash
# Проверить статус БД
docker-compose exec db pg_isready -U qgis_admin

# Перезапустить БД
docker-compose restart db
```

### GeoServer недоступен

```bash
# Проверить выделение памяти
docker stats geoserver

# Увеличить память в docker-compose.yml при необходимости
```

## Поддержка

При возникновении проблем:

1. Проверьте логи всех сервисов
2. Убедитесь, что все переменные окружения настроены правильно
3. Проверьте доступность портов
4. Убедитесь, что достаточно ресурсов (CPU, RAM, диск)

Документация:
- [Docker Compose](https://docs.docker.com/compose/)
- [PostGIS](https://postgis.net/documentation/)
- [GeoServer](https://docs.geoserver.org/)
- [Nginx](https://nginx.org/en/docs/)
