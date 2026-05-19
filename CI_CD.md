# CI/CD конфигурация для QGIS Web Platform

## GitHub Actions

### Файл: `.github/workflows/deploy.yml`

```yaml
name: Deploy QGIS Web Platform

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgis/postgis:15-3.3
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: gis_platform_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install backend dependencies
      working-directory: ./backend
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run backend tests
      working-directory: ./backend
      env:
        POSTGRES_HOST: localhost
        POSTGRES_PORT: 5432
        REDIS_HOST: localhost
        REDIS_PORT: 6379
      run: |
        pytest --cov=app tests/
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install frontend dependencies
      working-directory: ./frontend
      run: npm ci
    
    - name: Run frontend tests
      working-directory: ./frontend
      run: npm test -- --coverage
  
  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master')
    
    permissions:
      contents: read
      packages: write
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=sha,prefix=
          type=semver,pattern={{version}}
    
    - name: Build and push Docker image
      uses: docker/build-push-action@v4
      with:
        context: .
        file: ./docker-compose.yml
        push: true
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
  
  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && (github.ref == 'refs/heads/main' || github.ref == 'refs/heads/master')
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.DEPLOY_HOST }}
        username: ${{ secrets.DEPLOY_USER }}
        key: ${{ secrets.DEPLOY_KEY }}
        script: |
          cd /path/to/qgis-web
          git pull origin main
          docker-compose pull
          docker-compose up -d
          docker image prune -f
```

## GitLab CI/CD

### Файл: `.gitlab-ci.yml`

```yaml
stages:
  - test
  - build
  - deploy

variables:
  POSTGRES_DB: gis_platform_test
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
  DOCKER_REGISTRY: registry.gitlab.com/your-project

test-backend:
  stage: test
  image: python:3.10
  services:
    - postgis/postgis:15-3.3
    - redis:7-alpine
  variables:
    POSTGRES_HOST: postgis
    REDIS_HOST: redis
  before_script:
    - cd backend
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
  script:
    - pytest --cov=app tests/
  coverage: '/TOTAL.*\s+(\d+%)/'

test-frontend:
  stage: test
  image: node:18
  before_script:
    - cd frontend
    - npm ci
  script:
    - npm test -- --coverage

build-images:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker-compose build
    - docker-compose push
  only:
    - main
    - master

deploy-production:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$DEPLOY_KEY" | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - ssh-keyscan $DEPLOY_HOST >> ~/.ssh/known_hosts
    - chmod 644 ~/.ssh/known_hosts
  script:
    - ssh $DEPLOY_USER@$DEPLOY_HOST "cd /path/to/qgis-web && git pull && docker-compose pull && docker-compose up -d && docker image prune -f"
  only:
    - main
```

## Docker Compose для production

### Файл: `docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  db:
    image: postgis/postgis:15-3.3
    container_name: qgis_web_db
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - qgis_internal
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G

  redis:
    image: redis:7-alpine
    container_name: qgis_web_redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    networks:
      - qgis_internal
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: qgis_web_backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    environment:
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=${DB_NAME}
      - POSTGRES_HOST=db
      - POSTGRES_PORT=5432
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./uploads:/app/uploads
      - ./static:/app/static
    networks:
      - qgis_internal
      - qgis_web
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 1G

  geoserver:
    image: kartoza/geoserver:2.23.0
    container_name: qgis_web_geoserver
    environment:
      - BASIC_AUTH=true
      - GEOSERVER_ADMIN_PASSWORD=${GEOSERVER_PASSWORD}
      - GEOSERVER_ADMIN_USER=admin
    volumes:
      - geoserver_data:/opt/geoserver/data_dir
    depends_on:
      - db
    networks:
      - qgis_internal
      - qgis_web
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G

  nginx:
    image: nginx:alpine
    container_name: qgis_web_nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./frontend/build:/usr/share/nginx/html:ro
      - ./uploads:/var/www/uploads:ro
    depends_on:
      - backend
    networks:
      - qgis_web
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M

volumes:
  postgres_data:
  geoserver_data:

networks:
  qgis_internal:
    driver: bridge
    internal: true
  qgis_web:
    driver: bridge
```

## Переменные окружения для CI/CD

### GitHub Secrets:
- `DEPLOY_HOST` - IP или домен сервера
- `DEPLOY_USER` - пользователь для SSH
- `DEPLOY_KEY` - приватный SSH ключ для деплоя

### GitLab CI Variables:
- `DEPLOY_HOST` - IP или домен сервера
- `DEPLOY_USER` - пользователь для SSH
- `DEPLOY_KEY` - приватный SSH ключ для деплоя
- `DOCKER_REGISTRY` - URL реестра Docker

## Мониторинг

### Prometheus + Grafana стек

Добавьте в `docker-compose.yml`:

```yaml
  prometheus:
    image: prom/prometheus:latest
    container_name: qgis_prometheus
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - qgis_network
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: qgis_grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD:-admin}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    networks:
      - qgis_network
    restart: unless-stopped
```

## Автоматическое резервное копирование

### Скрипт backup.sh:

```bash
#!/bin/bash

BACKUP_DIR="/backups/qgis_web"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker-compose exec -T db pg_dump -U ${DB_USER} ${DB_NAME} | gzip > $BACKUP_DIR/db_${DATE}.sql.gz

# Backup GeoServer data
tar -czf $BACKUP_DIR/geoserver_${DATE}.tar.gz -C /var/lib/docker/volumes/qgis_web_geoserver_data/_data .

# Backup uploads
tar -czf $BACKUP_DIR/uploads_${DATE}.tar.gz ./uploads

# Delete backups older than 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### Cron job для ежедневного бэкапа:

```bash
# Добавить в crontab
0 2 * * * /path/to/backup.sh >> /var/log/qgis_backup.log 2>&1
```
