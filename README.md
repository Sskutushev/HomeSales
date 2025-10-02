# Полный гайд: Агрегатор недвижимости СПб

## Учетные данные проекта

```
Telegram Bot Token: 8311969135:AAGyyTOqwpYcOzpIIwKHauA6u6ZJBj1YgcY
Gemini API Key: AIzaSyBlo8Nt5_eS_Ya7kllINI9NdaLpu611xbo
Telegram Channel: @HomeSalesSPB
```

---

## ЧАСТЬ 1: Структура файлов

```
spb-realty-aggregator/
├── backend/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── listing.py
│   │   │   ├── developer.py
│   │   │   └── post.py
│   │   ├── parsers/
│   │   │   ├── __init__.py
│   │   │   ├── rss_parser.py
│   │   │   ├── cian_api.py
│   │   │   └── yandex_api.py
│   │   ├── processors/
│   │   │   ├── __init__.py
│   │   │   └── gemini_client.py
│   │   ├── telegram/
│   │   │   ├── __init__.py
│   │   │   ├── bot.py
│   │   │   └── publisher.py
│   │   └── api/
│   │       ├── __init__.py
│   │       └── routes.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celeryconfig.py
│   │   └── parse_sources.py
│   ├── alembic/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── miniapp/
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Listing.tsx
│   │   │   └── Favorites.tsx
│   │   └── components/
│   │       ├── ListingCard.tsx
│   │       ├── FilterPanel.tsx
│   │       └── ImageGallery.tsx
│   ├── package.json
│   ├── vite.config.ts
│   └── .env
└── docker-compose.yml
```

---

## ЧАСТЬ 2: Backend - Основные файлы

### backend/requirements.txt
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
celery==5.3.6
redis==5.0.1
python-telegram-bot==21.0
google-generativeai==0.3.2
feedparser==6.0.11
requests==2.31.0
python-dotenv==1.0.0
pydantic-settings==2.1.0
alembic==1.13.1
python-dateutil==2.8.2
beautifulsoup4==4.12.3
```

### backend/src/config.py
```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/spb_realty")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Gemini AI
    GEMINI_API_KEY: str = "AIzaSyBlo8Nt5_eS_Ya7kllINI9NdaLpu611xbo"
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str = "8311969135:AAGyyTOqwpYcOzpIIwKHauA6u6ZJBj1YgcY"
    TELEGRAM_CHANNEL_ID: str = "@HomeSalesSPB"
    
    # Mini App
    MINIAPP_URL: str = os.getenv("MINIAPP_URL", "https://localhost:5173")
    
    # External APIs
    CIAN_API_KEY: str = os.getenv("CIAN_API_KEY", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### backend/src/models/base.py
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### backend/src/models/listing.py
```python
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from src.models.base import Base

class Developer(Base):
    __tablename__ = "developers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    logo_url = Column(String)
    website = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class Complex(Base):
    __tablename__ = "complexes"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    developer_id = Column(UUID(as_uuid=True), ForeignKey("developers.id"))
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True)
    address = Column(String, nullable=False)
    district = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    completion_date = Column(DateTime)
    images = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Listing(Base):
    __tablename__ = "listings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    complex_id = Column(UUID(as_uuid=True), ForeignKey("complexes.id"))
    external_id = Column(String(100))
    source = Column(String(50), nullable=False)
    source_url = Column(String)
    
    rooms = Column(Integer, nullable=False)
    area = Column(Float, nullable=False)
    floor = Column(Integer)
    total_floors = Column(Integer)
    price = Column(Float, nullable=False)
    price_per_sqm = Column(Float)
    
    finishing = Column(String(50))
    balcony = Column(Boolean)
    images = Column(JSON)
    
    is_published = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    published_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'rooms': self.rooms,
            'area': float(self.area),
            'price': float(self.price),
            'price_per_sqm': float(self.price_per_sqm) if self.price_per_sqm else None,
            'floor': self.floor,
            'total_floors': self.total_floors,
            'images': self.images or [],
            'source_url': self.source_url,
            'created_at': self.created_at.isoformat()
        }
```

### backend/src/parsers/rss_parser.py
```python
import feedparser
import re
from typing import List, Dict
from datetime import datetime

class RSSParser:
    RSS_SOURCES = {
        "setl_group": {
            "url": "https://www.setlgroup.ru/rss/",
            "developer": "SETL GROUP"
        },
        "lsr": {
            "url": "https://www.lsr.ru/spb/news/rss/",
            "developer": "ЛСР"
        }
    }
    
    def fetch_all(self) -> List[Dict]:
        all_listings = []
        
        for source_id, config in self.RSS_SOURCES.items():
            try:
                feed = feedparser.parse(config['url'])
                for entry in feed.entries:
                    listing = self._parse_entry(entry, config['developer'], source_id)
                    if listing:
                        all_listings.append(listing)
            except Exception as e:
                print(f"Error parsing {source_id}: {e}")
                
        return all_listings
    
    def _parse_entry(self, entry, developer: str, source_id: str) -> Dict:
        text = f"{entry.get('title', '')} {entry.get('summary', '')}"
        
        listing = {
            'external_id': entry.get('id', entry.get('link')),
            'source': f'rss_{source_id}',
            'source_url': entry.get('link'),
            'developer': developer,
        }
        
        # Извлекаем данные регулярками
        rooms_match = re.search(r'(\d+)-комн|студия', text.lower())
        if rooms_match:
            listing['rooms'] = 0 if 'студия' in rooms_match.group() else int(rooms_match.group(1))
        
        area_match = re.search(r'(\d+[\.,]?\d*)\s*м²', text)
        if area_match:
            listing['area'] = float(area_match.group(1).replace(',', '.'))
        
        price_match = re.search(r'(\d[\d\s]*)\s*(?:руб|₽)', text)
        if price_match:
            price_str = price_match.group(1).replace(' ', '')
            listing['price'] = float(price_str)
        
        return listing if listing.get('price') else None
```

### backend/src/processors/gemini_client.py
```python
import google.generativeai as genai
from src.config import settings
import json

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_channel_post(self, listing_data: dict) -> str:
        prompt = f"""
Создай пост для Telegram-канала о новостройке в СПб.

ДАННЫЕ:
{json.dumps(listing_data, ensure_ascii=False, indent=2)}

ТРЕБОВАНИЯ:
- Длина 500-700 символов
- Цепляющий заголовок
- Ключевые факты: площадь, цена, район
- Хештеги в конце: #район #застройщик

Создай пост:
"""
        response = self.model.generate_content(prompt)
        return response.text.strip()
    
    def score_listing(self, listing_data: dict) -> float:
        prompt = f"""
Оцени привлекательность объявления от 0 до 100.

ДАННЫЕ:
{json.dumps(listing_data, ensure_ascii=False)}

Верни ТОЛЬКО число без текста.
"""
        response = self.model.generate_content(prompt)
        try:
            return float(response.text.strip())
        except:
            return 50.0
```

### backend/src/telegram/publisher.py
```python
from telegram import Bot, InputMediaPhoto, InlineKeyboardButton, InlineKeyboardMarkup
from src.config import settings

class ChannelPublisher:
    def __init__(self):
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.channel_id = settings.TELEGRAM_CHANNEL_ID
    
    async def publish_listing(self, post_text: str, images: list, listing_id: str) -> int:
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                "📋 Подробнее",
                url=f"{settings.MINIAPP_URL}?startapp=listing_{listing_id}"
            )
        ]])
        
        if images:
            media_group = [
                InputMediaPhoto(media=img, caption=post_text if i == 0 else "")
                for i, img in enumerate(images[:3])
            ]
            messages = await self.bot.send_media_group(
                chat_id=self.channel_id,
                media=media_group
            )
            await self.bot.send_message(
                chat_id=self.channel_id,
                text="👇 Полная информация:",
                reply_markup=keyboard
            )
            return messages[0].message_id
        else:
            message = await self.bot.send_message(
                chat_id=self.channel_id,
                text=post_text,
                reply_markup=keyboard
            )
            return message.message_id
```

### backend/src/api/routes.py
```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.models.base import get_db
from src.models.listing import Listing
from typing import Optional

router = APIRouter()

@router.get("/listings")
async def get_listings(
    district: Optional[str] = None,
    rooms: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Listing).filter(Listing.is_active == True)
    
    if rooms is not None:
        query = query.filter(Listing.rooms == rooms)
    if min_price:
        query = query.filter(Listing.price >= min_price)
    if max_price:
        query = query.filter(Listing.price <= max_price)
    
    listings = query.order_by(Listing.created_at.desc()).limit(limit).all()
    return [listing.to_dict() for listing in listings]

@router.get("/listings/{listing_id}")
async def get_listing(listing_id: str, db: Session = Depends(get_db)):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        return {"error": "Not found"}, 404
    return listing.to_dict()
```

### backend/src/main.py
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import routes
from src.models.base import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SPB Realty API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router, prefix="/api")

@app.get("/health")
async def health():
    return {"status": "ok"}
```

### backend/tasks/celeryconfig.py
```python
from celery import Celery
from celery.schedules import crontab
from src.config import settings

app = Celery(
    'spb_realty',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

app.conf.beat_schedule = {
    'parse-every-30min': {
        'task': 'tasks.parse_sources.parse_all',
        'schedule': 1800.0,
    },
    'publish-at-10am': {
        'task': 'tasks.parse_sources.publish_best',
        'schedule': crontab(hour=10, minute=0),
    },
}
```

### backend/tasks/parse_sources.py
```python
from tasks.celeryconfig import app
from src.parsers.rss_parser import RSSParser
from src.processors.gemini_client import GeminiClient
from src.telegram.publisher import ChannelPublisher
from src.models.listing import Listing
from src.models.base import SessionLocal
import asyncio

@app.task
def parse_all():
    parser = RSSParser()
    listings = parser.fetch_all()
    
    db = SessionLocal()
    saved = 0
    
    for data in listings:
        existing = db.query(Listing).filter_by(external_id=data['external_id']).first()
        if not existing:
            listing = Listing(**data)
            db.add(listing)
            saved += 1
    
    db.commit()
    db.close()
    return f"Saved {saved} new listings"

@app.task
def publish_best():
    db = SessionLocal()
    candidates = db.query(Listing).filter_by(is_published=False, is_active=True).limit(10).all()
    
    gemini = GeminiClient()
    scored = [(l, gemini.score_listing(l.to_dict())) for l in candidates]
    scored.sort(key=lambda x: x[1], reverse=True)
    
    publisher = ChannelPublisher()
    
    for listing, score in scored[:3]:
        post = gemini.generate_channel_post(listing.to_dict())
        asyncio.run(publisher.publish_listing(post, listing.images or [], str(listing.id)))
        listing.is_published = True
    
    db.commit()
    db.close()
```

---

## ЧАСТЬ 3: Frontend (Mini App)

### miniapp/package.json
```json
{
  "name": "homesales-miniapp",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.0",
    "@telegram-apps/sdk-react": "^1.0.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0"
  }
}
```

### miniapp/src/api/client.ts
```typescript
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const api = {
  async getListings(filters: any) {
    const response = await axios.get(`${API_URL}/listings`, { params: filters })
    return response.data
  },
  
  async getListing(id: string) {
    const response = await axios.get(`${API_URL}/listings/${id}`)
    return response.data
  }
}
```

### miniapp/src/pages/Home.tsx
```typescript
import { useEffect, useState } from 'react'
import { api } from '../api/client'

export default function Home() {
  const [listings, setListings] = useState([])

  useEffect(() => {
    api.getListings({}).then(setListings)
  }, [])

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">Новостройки СПб</h1>
      <div className="grid gap-4">
        {listings.map((listing: any) => (
          <div key={listing.id} className="border rounded-lg p-4">
            <div className="font-bold">{listing.rooms} комн., {listing.area} м²</div>
            <div className="text-lg text-blue-600">{listing.price.toLocaleString()} ₽</div>
          </div>
        ))}
      </div>
    </div>
  )
}
```

---

## ЧАСТЬ 4: Запуск проекта

### Локальный запуск

```bash
# 1. Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload

# 2. Celery (в отдельном терминале)
celery -A tasks.celeryconfig worker -l info

# 3. Frontend (в отдельном терминале)
cd miniapp
npm install
npm run dev
```

### Docker Compose

```yaml
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
  
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: spb_realty
  
  redis:
    image: redis:7-alpine
```

Запуск: `docker-compose up`

---

## ЧАСТЬ 5: Деплой

### Backend на Railway
```bash
railway init
railway add
railway up
```

### Frontend на Vercel
```bash
cd miniapp
npm install -g vercel
vercel --prod
```