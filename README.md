# Промпт для Gemini: Агрегатор недвижимости СПб (легальная версия)

## ⚠️ КРИТИЧЕСКИ ВАЖНО: Легальность превыше всего

Этот проект использует ТОЛЬКО официальные источники данных:
1. RSS-ленты застройщиков (публичные)
2. API агрегаторов (ЦИАН, Яндекс.Недвижимость)
3. Партнерские программы
4. Пресс-релизы и новости

**ЗАПРЕЩЕНО:**
- Парсинг сайтов без разрешения
- Использование чужих фото без атрибуции
- Копирование текстов 1-в-1

---

## Контекст проекта

Создаём Telegram-канал + Mini App для агрегации предложений по недвижимости Санкт-Петербурга.

**Архитектура:**
```
RSS/API источники → Python парсер → База данных → 
→ Gemini обработка → Telegram Bot публикация + Mini App
```

**Компоненты:**
1. **Parser Service** - сбор данных из легальных источников
2. **Gemini Processor** - структурирование и создание постов
3. **Telegram Bot** - публикация в канал
4. **Mini App** - детальные объявления

---

## Технический стек

```yaml
Backend:
  Language: Python 3.11+
  Framework: FastAPI
  Database: PostgreSQL (Supabase free tier)
  Cache: Redis (Upstash free tier)
  Task Queue: Celery + Redis

AI:
  Provider: Google Gemini 2.5 Flash
  API Key: AIzaSyBlo8Nt5_eS_Ya7kllINI9NdaLpu611xbo
  
Telegram:
  Bot Token: 8311969135:AAGyyTOqwpYcOzpIIwKHauA6u6ZJBj1YgcY
  Channel: @HomeSalesSPB
  
Mini App:
  Frontend: React + Vite + TypeScript
  Hosting: GitHub Pages или Vercel
  UI: Telegram Mini App guidelines
```

---

## Структура проекта

```
spb-realty-aggregator/
├── backend/
│   ├── src/
│   │   ├── parsers/          # Сбор данных
│   │   │   ├── rss_parser.py
│   │   │   ├── cian_api.py
│   │   │   ├── yandex_api.py
│   │   │   └── base_parser.py
│   │   ├── processors/       # AI обработка
│   │   │   ├── gemini_client.py
│   │   │   ├── post_generator.py
│   │   │   └── image_handler.py
│   │   ├── telegram/         # Публикация
│   │   │   ├── bot.py
│   │   │   └── channel_publisher.py
│   │   ├── models/           # База данных
│   │   │   ├── listing.py
│   │   │   ├── developer.py
│   │   │   └── post.py
│   │   ├── api/              # REST API для Mini App
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   ├── config.py
│   │   └── main.py
│   ├── tasks/                # Celery задачи
│   │   ├── parse_sources.py
│   │   └── publish_posts.py
│   └── requirements.txt
├── miniapp/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ListingCard.tsx
│   │   │   ├── FilterPanel.tsx
│   │   │   ├── DetailView.tsx
│   │   │   └── ImageGallery.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Listing.tsx
│   │   │   └── Favorites.tsx
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
└── README.md
```

---

## База данных (PostgreSQL)

```sql
-- Разработчики/Застройщики
CREATE TABLE developers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    logo_url TEXT,
    website VARCHAR(255),
    description TEXT,
    rating DECIMAL(3,2),
    projects_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Жилые комплексы
CREATE TABLE complexes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    developer_id UUID REFERENCES developers(id),
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    district VARCHAR(100),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    completion_date DATE,
    min_price DECIMAL(15,2),
    max_price DECIMAL(15,2),
    images JSONB,
    amenities JSONB,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Объявления
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    complex_id UUID REFERENCES complexes(id),
    external_id VARCHAR(100),
    source VARCHAR(50) NOT NULL, -- 'rss', 'cian', 'yandex'
    source_url TEXT,
    
    -- Основные данные
    rooms INT NOT NULL, -- 0 = студия
    area DECIMAL(6,2) NOT NULL,
    floor INT,
    total_floors INT,
    price DECIMAL(15,2) NOT NULL,
    price_per_sqm DECIMAL(10,2),
    
    -- Детали
    finishing VARCHAR(50), -- 'none', 'rough', 'turnkey'
    balcony BOOLEAN,
    windows_view VARCHAR(100),
    layout_type VARCHAR(50),
    
    -- Медиа
    images JSONB, -- [{url, caption}]
    layout_image TEXT,
    
    -- Статусы
    is_published BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    published_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Посты в канале
CREATE TABLE channel_posts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    listing_id UUID REFERENCES listings(id),
    message_id BIGINT, -- ID сообщения в Telegram
    post_text TEXT NOT NULL,
    images JSONB,
    views INT DEFAULT 0,
    clicks INT DEFAULT 0,
    published_at TIMESTAMP DEFAULT NOW()
);

-- Избранное пользователей (для Mini App)
CREATE TABLE favorites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_user_id BIGINT NOT NULL,
    listing_id UUID REFERENCES listings(id),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(telegram_user_id, listing_id)
);
```

---

## Легальные источники данных

### 1. RSS-ленты застройщиков (публичные)

```python
# backend/src/parsers/rss_sources.py

RSS_SOURCES = {
    "setl_group": {
        "url": "https://www.setlgroup.ru/rss/",
        "parser": "rss_parser"
    },
    "lsr": {
        "url": "https://www.lsr.ru/spb/news/rss/",
        "parser": "rss_parser"
    },
    "glorax": {
        "url": "https://glorax.ru/rss/",
        "parser": "rss_parser"
    },
    "cds": {
        "url": "https://cds.spb.ru/rss/",
        "parser": "rss_parser"
    }
}
```

### 2. ЦИАН API (партнерская программа)

```python
# backend/src/parsers/cian_api.py

import requests

class CianAPI:
    """
    Для использования нужно зарегистрироваться:
    https://www.cian.ru/help/about/api/
    Бесплатный тариф: 1000 запросов/день
    """
    
    BASE_URL = "https://api.cian.ru/v1/"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    def get_new_buildings(self, city_id: int = 2):  # 2 = СПб
        """Получить новостройки"""
        endpoint = f"{self.BASE_URL}new-buildings/"
        params = {
            "city_id": city_id,
            "limit": 50
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = requests.get(endpoint, params=params, headers=headers)
        return response.json()
```

### 3. Яндекс.Недвижимость API

```python
# backend/src/parsers/yandex_api.py

class YandexRealtyAPI:
    """
    Партнерская программа:
    https://partner.realty.yandex.ru/
    """
    
    BASE_URL = "https://realty.yandex.ru/export/rss/"
    
    def get_newbuildings_feed(self):
        url = f"{self.BASE_URL}sale/newbuilding/sankt-peterburg/"
        response = requests.get(url)
        return self.parse_rss(response.content)
```

---

## AI обработка с Gemini

### Промпты для генерации постов

```python
# backend/src/processors/post_generator.py

import google.generativeai as genai

genai.configure(api_key="AIzaSyBlo8Nt5_eS_Ya7kllINI9NdaLpu611xbo")

CHANNEL_POST_PROMPT = """
Ты - маркетолог недвижимости. Создай пост для Telegram-канала о недвижимости СПб.

ДАННЫЕ ОБЪЯВЛЕНИЯ:
- ЖК: {complex_name}
- Район: {district}
- Комнат: {rooms}
- Площадь: {area} м²
- Цена: {price} руб ({price_per_sqm} руб/м²)
- Срок сдачи: {completion_date}
- Отделка: {finishing}
- Особенности: {amenities}

ТРЕБОВАНИЯ К ПОСТУ:
1. Длина: 500-700 символов
2. Структура:
   - Цепляющий заголовок с эмоцией
   - Ключевые факты (район, цена, площадь)
   - Уникальное преимущество
   - Призыв к действию
3. Использовать техники копирайтинга:
   - Конкретные цифры
   - Социальное доказательство
   - Ограниченность предложения (если есть)
   - Выгода для покупателя
4. БЕЗ излишней рекламности и восклицаний
5. Хештеги в конце: #{district_slug} #{developer_slug} #{room_count}комнатная

СТИЛЬ: экспертный, доверительный, с акцентом на факты и выгоду.

Создай пост:
"""

DETAIL_DESCRIPTION_PROMPT = """
Создай детальное описание квартиры для страницы объявления в Mini App.

ДАННЫЕ: {listing_data}

СТРУКТУРА:
1. Краткий обзор (2-3 предложения)
2. Планировка и площадь
3. Локация и инфраструктура
4. Особенности ЖК
5. Инвестиционная привлекательность

Длина: 1500-2000 символов.
Стиль: информативный, структурированный.
"""

class GeminiPostGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_channel_post(self, listing_data: dict) -> str:
        """Генерация поста для канала"""
        prompt = CHANNEL_POST_PROMPT.format(**listing_data)
        response = self.model.generate_content(prompt)
        return response.text
    
    def generate_detail_description(self, listing_data: dict) -> str:
        """Генерация детального описания"""
        prompt = DETAIL_DESCRIPTION_PROMPT.format(
            listing_data=json.dumps(listing_data, ensure_ascii=False)
        )
        response = self.model.generate_content(prompt)
        return response.text
```

---

## Telegram Bot (публикация в канал)

```python
# backend/src/telegram/channel_publisher.py

from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

class ChannelPublisher:
    def __init__(self, bot_token: str, channel_id: str):
        self.bot = Bot(token=bot_token)
        self.channel_id = channel_id  # @HomeSalesSPB
    
    async def publish_listing(
        self, 
        post_text: str, 
        images: list[str], 
        listing_id: str
    ) -> int:
        """
        Публикует объявление в канал
        Возвращает message_id
        """
        
        # Кнопка "Подробнее" → открывает Mini App на конкретном объявлении
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "📋 Подробнее",
                url=f"https://t.me/YOUR_BOT_USERNAME/app?startapp=listing_{listing_id}"
            )
        ]])
        
        # Если есть фото - отправляем как медиа-группу
        if images:
            media_group = [
                InputMediaPhoto(media=img, caption=post_text if i == 0 else "")
                for i, img in enumerate(images[:3])  # макс 3 фото
            ]
            
            messages = await self.bot.send_media_group(
                chat_id=self.channel_id,
                media=media_group
            )
            
            # Добавляем кнопку отдельным сообщением
            await self.bot.send_message(
                chat_id=self.channel_id,
                text="👇 Полная информация в приложении:",
                reply_markup=keyboard
            )
            
            return messages[0].message_id
        else:
            # Без фото - простое сообщение
            message = await self.bot.send_message(
                chat_id=self.channel_id,
                text=post_text,
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard
            )
            return message.message_id
```

---

## Mini App (Frontend)

### Главная страница (список объявлений)

```typescript
// miniapp/src/pages/Home.tsx

import { useEffect, useState } from 'react';
import { ListingCard } from '../components/ListingCard';
import { FilterPanel } from '../components/FilterPanel';
import { api } from '../api/client';

interface Listing {
  id: string;
  complex_name: string;
  district: string;
  rooms: number;
  area: number;
  price: number;
  price_per_sqm: number;
  images: string[];
  preview_image: string;
}

export function Home() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [filters, setFilters] = useState({
    district: '',
    rooms: '',
    min_price: '',
    max_price: ''
  });
  
  useEffect(() => {
    // Получаем startapp параметр из URL
    const urlParams = new URLSearchParams(window.location.search);
    const startParam = urlParams.get('startapp');
    
    if (startParam?.startsWith('listing_')) {
      // Открыли с конкретным объявлением
      const listingId = startParam.replace('listing_', '');
      window.location.href = `/listing/${listingId}`;
    } else {
      // Загружаем список
      loadListings();
    }
  }, [filters]);
  
  const loadListings = async () => {
    const data = await api.getListings(filters);
    setListings(data);
  };
  
  return (
    <div className="container">
      <header>
        <h1>🏠 Новостройки СПб</h1>
        <p>Актуальные предложения от застройщиков</p>
      </header>
      
      <FilterPanel filters={filters} onChange={setFilters} />
      
      <div className="listings-grid">
        {listings.map(listing => (
          <ListingCard key={listing.id} listing={listing} />
        ))}
      </div>
    </div>
  );
}
```

### Карточка объявления

```typescript
// miniapp/src/components/ListingCard.tsx

interface Props {
  listing: Listing;
}

export function ListingCard({ listing }: Props) {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('ru-RU').format(price);
  };
  
  return (
    <a href={`/listing/${listing.id}`} className="listing-card">
      <div className="image">
        <img src={listing.preview_image} alt={listing.complex_name} />
        <div className="badge">{listing.rooms === 0 ? 'Студия' : `${listing.rooms}-комн`}</div>
      </div>
      
      <div className="content">
        <h3>{listing.complex_name}</h3>
        <p className="district">📍 {listing.district}</p>
        
        <div className="specs">
          <span>{listing.area} м²</span>
          <span>•</span>
          <span>{formatPrice(listing.price_per_sqm)} ₽/м²</span>
        </div>
        
        <div className="price">
          <strong>{formatPrice(listing.price)} ₽</strong>
        </div>
      </div>
    </a>
  );
}
```

---

## Celery задачи (автоматизация)

```python
# backend/tasks/parse_sources.py

from celery import Celery
from src.parsers import RSSParser, CianAPI, YandexAPI
from src.processors import GeminiPostGenerator
from src.telegram import ChannelPublisher
from src.models import Listing, ChannelPost

app = Celery('spb_realty')

@app.task
def parse_all_sources():
    """Запускается каждые 30 минут"""
    
    # 1. Собираем данные из всех источников
    parsers = [
        RSSParser(RSS_SOURCES),
        CianAPI(api_key=config.CIAN_API_KEY),
        YandexAPI()
    ]
    
    new_listings = []
    for parser in parsers:
        try:
            data = parser.fetch()
            new_listings.extend(parser.parse(data))
        except Exception as e:
            logger.error(f"Parser {parser.__class__} failed: {e}")
    
    # 2. Сохраняем в БД (дедупликация по external_id)
    saved_count = 0
    for listing_data in new_listings:
        listing = Listing.create_or_update(listing_data)
        if listing.is_new:
            saved_count += 1
    
    logger.info(f"Saved {saved_count} new listings")
    
    # 3. Триггерим публикацию лучших предложений
    publish_best_listings.delay()

@app.task
def publish_best_listings():
    """Публикация 3-5 лучших объявлений в день"""
    
    # Выбираем непубликованные объявления с лучшим соотношением цена/качество
    candidates = Listing.query.filter(
        Listing.is_published == False,
        Listing.is_active == True
    ).order_by(Listing.created_at.desc()).limit(20).all()
    
    # AI-оценка каждого
    generator = GeminiPostGenerator()
    scored = []
    
    for listing in candidates:
        score = generator.score_listing_attractiveness(listing.to_dict())
        scored.append((listing, score))
    
    # Публикуем топ-3
    publisher = ChannelPublisher(
        bot_token=config.TELEGRAM_BOT_TOKEN,
        channel_id=config.TELEGRAM_CHANNEL_ID
    )
    
    top_listings = sorted(scored, key=lambda x: x[1], reverse=True)[:3]
    
    for listing, score in top_listings:
        try:
            # Генерируем пост
            post_text = generator.generate_channel_post(listing.to_dict())
            
            # Публикуем
            message_id = await publisher.publish_listing(
                post_text=post_text,
                images=listing.images[:3],
                listing_id=str(listing.id)
            )
            
            # Сохраняем факт публикации
            ChannelPost.create(
                listing_id=listing.id,
                message_id=message_id,
                post_text=post_text,
                images=listing.images
            )
            
            listing.is_published = True
            listing.published_at = datetime.now()
            listing.save()
            
            logger.info(f"Published listing {listing.id} with score {score}")
            
            # Пауза между постами (2-3 часа)
            await asyncio.sleep(random.randint(7200, 10800))
            
        except Exception as e:
            logger.error(f"Failed to publish {listing.id}: {e}")

# Расписание задач
app.conf.beat_schedule = {
    'parse-sources-every-30-min': {
        'task': 'tasks.parse_sources.parse_all_sources',
        'schedule': 1800.0,  # 30 минут
    },
    'publish-daily-at-10am': {
        'task': 'tasks.parse_sources.publish_best_listings',
        'schedule': crontab(hour=10, minute=0),
    },
}
```

---

## API для Mini App

```python
# backend/src/api/routes.py

from fastapi import FastAPI, Query
from typing import Optional
from src.models import Listing, Complex, Developer

app = FastAPI()

@app.get("/api/listings")
async def get_listings(
    district: Optional[str] = None,
    rooms: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = Query(20, le=100)
):
    """Получить список объявлений с фильтрами"""
    
    query = Listing.query.filter(Listing.is_active == True)
    
    if district:
        query = query.join(Complex).filter(Complex.district == district)
    if rooms is not None:
        query = query.filter(Listing.rooms == rooms)
    if min_price:
        query = query.filter(Listing.price >= min_price)
    if max_price:
        query = query.filter(Listing.price <= max_price)
    
    listings = query.order_by(Listing.created_at.desc()).limit(limit).all()
    
    return [listing.to_dict() for listing in listings]

@app.get("/api/listings/{listing_id}")
async def get_listing_detail(listing_id: str):
    """Получить детальную информацию об объявлении"""
    
    listing = Listing.get_by_id(listing_id)
    if not listing:
        raise HTTPException(status_code=404)
    
    return listing.to_dict(include_full_description=True)

@app.get("/api/districts")
async def get_districts():
    """Получить список районов с количеством объявлений"""
    
    districts = db.session.query(
        Complex.district,
        db.func.count(Listing.id).label('count')
    ).join(Listing).group_by(Complex.district).all()
    
    return [{"name": d[0], "count": d[1]} for d in districts]
```

---

## Конфигурация и деплой

```python
# backend/src/config.py

import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")  # Supabase PostgreSQL
    REDIS_URL: str = os.getenv("REDIS_URL")  # Upstash
    
    # Gemini AI
    GEMINI_API_KEY: str = "AIzaSyBlo8Nt5_eS_Ya7kllINI9NdaLpu611xbo"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = "8311969135:AAGyyTOqwpYcOzpIIwKHauA6u6ZJBj1YgcY"
    TELEGRAM_CHANNEL_ID: str = "@HomeSalesSPB"
    
    # External APIs (нужно получить ключи)
    CIAN_API_KEY: str = os.getenv("CIAN_API_KEY", "")
    YANDEX_API_KEY: str = os.getenv("YANDEX_API_KEY", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Docker Compose для локальной разработки

```yaml
# docker-compose.yml

version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/spb_realty
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./backend:/app
    command: uvicorn src.main:app --host 0.0.0.0 --reload
  
  celery_worker:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/spb_realty
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    command: celery -A tasks.parse_sources worker --loglevel=info
  
  celery_beat:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/spb_realty
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    command: celery -A tasks.parse_sources beat --loglevel=info
  
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

---

## Пошаговый план разработки

### Неделя 1: Backend Foundation

**День 1-2: Настройка проекта**
- [ ] Создать структуру папок
- [ ] Настроить PostgreSQL (Supabase)
- [ ] Создать таблицы БД
- [ ] Настроить FastAPI + Celery

**День 3-4: Парсеры**
- [ ] Реализовать RSS парсер
- [ ] Интегрировать ЦИАН API (если есть ключ)
- [ ] Тестовая загрузка 50+ объявлений

**День 5-7: Gemini интеграция**
- [ ] Настроить Gemini API
- [ ] Создать промпты для постов
- [ ] Тесты генерации контента
- [ ] Сохранение в БД

### Неделя 2: Telegram Bot

**День 8-10: Bot Setup**
- [ ] Создать бота через BotFather
- [ ] Добавить в канал как админа
- [ ] Реализовать публикацию постов
- [ ] Тесты с кнопками

**День 11-14: Автоматизация**
- [ ] Celery задачи парсинга
- [ ] Celery задачи публикации
- [ ] Настроить расписание
- [ ] Мониторинг ошибок

### Неделя 3: Mini App

**День 15-