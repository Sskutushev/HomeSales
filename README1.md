# HomeSale Project Stack and Deployment Guide

Этот документ описывает текущий стек проекта HomeSale, его структуру и шаги для развертывания бэкенда с использованием бесплатных опций.

## 1. Обзор стека проекта

Проект HomeSale состоит из двух основных частей: фронтенда (веб-сайта) и бэкенда (серверной части с API и ботом).

### 1.1. Фронтенд (miniapp)
*   **Технологии:** React, Vite (сборщик), TypeScript, Tailwind CSS (стили), React Router v6 (маршрутизация).
*   **Назначение:** Отображает объявления недвижимости, позволяет просматривать детали.
*   **Развертывание:** Размещен на GitHub Pages.

### 1.2. Бэкенд (backend)
*   **Технологии:** FastAPI (Python-фреймворк для API), Uvicorn (ASGI-сервер), SQLAlchemy (ORM для работы с БД), PostgreSQL (база данных), Redis (брокер сообщений для Celery).
*   **Назначение:**
    *   Предоставляет API для фронтенда (получение списка объявлений, деталей).
    *   Содержит логику бота для парсинга и публикации в Telegram.
*   **Контейнеризация:** Использует Docker и Docker Compose для изоляции и упрощения развертывания.

### 1.3. Логика бота
*   **Парсер (simulated):** В текущей реализации парсер `SetlGroupParser` является симуляцией. Он возвращает жестко закодированные тестовые объявления. В реальной версии здесь должна быть логика для сбора данных с сайта застройщика.
*   **Генерация постов:** Использует Gemini API (модель `gemini-2.5-pro`) для создания маркетинговых текстов объявлений.
*   **Публикация в Telegram:** Использует библиотеку `python-telegram-bot` для отправки постов (текст + кнопка) в указанный Telegram-канал.
*   **Очередь задач:** Celery с Redis используется для выполнения фоновых задач (парсинг, публикация) по расписанию.

## 2. Рабочий процесс (Data Flow)

1.  **Парсинг (Simulated):** Задача `parse_sources` (Celery) запускается по расписанию (или вручную). Она вызывает `SetlGroupParser`, который возвращает список объявлений.
2.  **Обновление базы данных:** Задача `parse_sources` очищает таблицу `listings` в PostgreSQL и добавляет в нее полученные (симулированные) объявления.
3.  **Отображение на фронтенде:** Фронтенд (веб-сайт) обращается к API бэкенда (`/api/listings`), получает список объявлений из базы данных и отображает их.
4.  **Генерация и публикация постов:** Задача `publish_posts` (Celery) запускается по расписанию (или вручную).
    *   Она получает объявления из базы данных.
    *   Для каждого объявления `PostGenerator` использует Gemini API для создания маркетингового текста.
    *   `TelegramChannelPublisher` отправляет этот текст в Telegram-канал.
    *   К каждому посту прикрепляется кнопка "Открыть объявление", которая ведет на страницу этого объявления в вашем Mini App (фронтенде).

## 3. Развертывание бэкенда (бесплатные опции)

Развертывание бэкенда требует размещения вашего приложения и базы данных на публичном сервере. Использование только бесплатных опций накладывает серьезные ограничения и часто требует более сложной настройки.

**Важно:** Я не могу выполнить эти шаги за вас, так как это требует доступа к вашим аккаунтам на внешних сервисах.

### 3.1. Необходимые компоненты для развертывания

Для работы бэкенда вам понадобятся:
*   **База данных PostgreSQL:** Удаленная база данных.
*   **Брокер сообщений Redis:** Удаленный Redis-сервер для Celery.
*   **Сервер для FastAPI и Celery:** Место, где будет работать ваш Python-код.

### 3.2. Бесплатные варианты хостинга (с ограничениями)

**База данных PostgreSQL:**
*   **ElephantSQL:** Предоставляет бесплатный тариф "Tiny Turtle" (до 20 МБ данных, 5 одновременных подключений). Идеально для небольших проектов.
*   **Supabase:** Бесплатный тариф включает PostgreSQL, но может потребовать больше усилий для интеграции с вашим Docker-Compose.
*   **Railway:** Бесплатный тариф с лимитами по использованию.

**Брокер сообщений Redis:**
*   **Upstash:** Предоставляет бесплатный тариф для Redis (до 10 000 команд в день, 256 МБ данных).
*   **RedisLabs (Redis Cloud):** Бесплатный тариф с лимитами.

**Сервер для FastAPI и Celery (Docker-совместимые):**
*   **Render:** Один из немногих сервисов, который поддерживает развертывание Docker Compose. Предоставляет бесплатный тариф (до 750 часов работы в месяц, приложение "засыпает" после 15 минут бездействия). Это наиболее подходящий вариант для вашего проекта с Docker Compose.
*   **Google Cloud Run:** Щедро предоставляет бесплатный тариф, но требует адаптации вашего приложения под бессерверные функции и не поддерживает прямой запуск Docker Compose.

### 3.3. Подготовка `docker-compose.yml` для Celery

Я сейчас изменю ваш файл `docker-compose.yml`, чтобы он включал сервисы для Celery worker и Celery Beat. Это позволит задачам парсинга и публикации запускаться автоматически по расписанию, когда вы развернете проект с Docker Compose.

```yaml
# Текущий docker-compose.yml (пример)
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8001:8001" # Измененный порт
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SQLALCHEMY_DATABASE_URL=${SQLALCHEMY_DATABASE_URL}
      - ASYNC_DATABASE_URL=${ASYNC_DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHANNEL_ID=${TELEGRAM_CHANNEL_ID}
      - CIAN_API_KEY=${CIAN_API_KEY}
      - YANDEX_API_KEY=${YANDEX_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload # Измененный порт

  celery_worker:
    build: ./backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SQLALCHEMY_DATABASE_URL=${SQLALCHEMY_DATABASE_URL}
      - ASYNC_DATABASE_URL=${ASYNC_DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHANNEL_ID=${TELEGRAM_CHANNEL_ID}
      - CIAN_API_KEY=${CIAN_API_KEY}
      - YANDEX_API_KEY=${YANDEX_API_KEY}
    depends_on:
      - db
      - redis
    command: celery -A tasks.parse_sources worker --loglevel=info

  celery_beat:
    build: ./backend
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SQLALCHEMY_DATABASE_URL=${SQLALCHEMY_DATABASE_URL}
      - ASYNC_DATABASE_URL=${ASYNC_DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHANNEL_ID=${TELEGRAM_CHANNEL_ID}
      - CIAN_API_KEY=${CIAN_API_KEY}
      - YANDEX_API_KEY=${YANDEX_API_KEY}
    depends_on:
      - db
      - redis
    command: celery -A tasks.parse_sources beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler # Пример, может потребоваться установка django-celery-beat

  frontend:
    build:
      context: ./miniapp
      dockerfile: Dockerfile
    ports:
      - "3000:3000" # Измененный порт
    volumes:
      - ./miniapp:/app
      - /app/node_modules
    environment:
      - VITE_API_BASE_URL=http://backend:8001/api # Измененный порт
    command: npm run dev
  
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: spb_realty
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### 3.4. Настройка фронтенда для публичного бэкенда

Я изменю файл `miniapp/src/api/client.ts`, чтобы он использовал переменную окружения `VITE_API_BASE_URL`. Когда вы будете развертывать фронтенд, вы сможете указать публичный адрес вашего бэкенда через эту переменную.

```typescript
// miniapp/src/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api', // 'http://localhost:8001/api' для локальной разработки
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;
```

---

**Давайте начнем с обновления `docker-compose.yml` для включения Celery worker и Celery Beat.**

Согласны?
