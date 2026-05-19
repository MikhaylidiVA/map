#!/bin/bash

# Скрипт быстрого развертывания QGIS Web Platform
# Использование: ./deploy.sh [dev|prod]

set -e

ENVIRONMENT=${1:-dev}

echo "🚀 Развертывание QGIS Web Platform (${ENVIRONMENT})"
echo "=================================================="

# Проверка наличия Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Пожалуйста, установите Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Пожалуйста, установите Docker Compose."
    exit 1
fi

echo "✅ Docker и Docker Compose найдены"

# Создание .env файла если не существует
if [ ! -f .env ]; then
    echo "📝 Создание файла .env из шаблона..."
    cp .env.example .env
    
    # Генерация случайного SECRET_KEY
    if command -v openssl &> /dev/null; then
        SECRET_KEY=$(openssl rand -hex 32)
        sed -i "s/generate_random_secret_key_here_use_openssl_rand_hex_32/${SECRET_KEY}/" .env
        echo "✅ SECRET_KEY сгенерирован"
    else
        echo "⚠️  OpenSSL не найден. SECRET_KEY нужно установить вручную в .env"
    fi
    
    echo "✅ Файл .env создан. Отредактируйте пароли перед запуском в production!"
else
    echo "✅ Файл .env уже существует"
fi

# Создание необходимых директорий
echo "📁 Создание необходимых директорий..."
mkdir -p nginx/ssl uploads static geoserver_plugins frontend/build

# Генерация self-signed сертификатов для dev окружения
if [ "$ENVIRONMENT" = "dev" ] && [ ! -f nginx/ssl/cert.pem ]; then
    echo "🔐 Генерация self-signed SSL сертификатов..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost" \
        2>/dev/null || echo "⚠️  Не удалось сгенерировать сертификаты"
fi

# Остановка старых контейнеров
echo "🛑 Остановка существующих контейнеров..."
docker-compose down 2>/dev/null || true

# Сборка и запуск сервисов
echo "🔨 Сборка образов..."
docker-compose build

echo "🚀 Запуск сервисов..."
docker-compose up -d

# Ожидание готовности сервисов
echo "⏳ Ожидание готовности сервисов..."
sleep 10

# Проверка статуса
echo ""
echo "📊 Статус сервисов:"
echo "==================="
docker-compose ps

echo ""
echo "✅ Развертывание завершено!"
echo ""
echo "📍 Сервисы доступны по адресам:"
echo "   - Фронтенд: http://localhost"
echo "   - Backend API: http://localhost/api"
echo "   - GeoServer: http://localhost/geoserver (admin / ваш пароль из .env)"
echo ""
echo "📋 Полезные команды:"
echo "   - Просмотр логов: docker-compose logs -f"
echo "   - Остановка: docker-compose down"
echo "   - Перезапуск: docker-compose restart"
echo ""
echo "⚠️  ВНИМАНИЕ: Для production обязательно измените все пароли в .env!"

if [ "$ENVIRONMENT" = "prod" ]; then
    echo ""
    echo "🔒 Production чеклист:"
    echo "   1. Измените все пароли в .env"
    echo "   2. Настройте SSL сертификаты (Let's Encrypt или свои)"
    echo "   3. Раскомментируйте SSL настройки в nginx/nginx.conf"
    echo "   4. Настройте firewall"
    echo "   5. Настройте резервное копирование"
    echo "   6. Включите мониторинг"
    echo ""
    echo "📖 Подробная инструкция: DEPLOYMENT.md"
fi
