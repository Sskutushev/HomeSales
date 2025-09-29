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