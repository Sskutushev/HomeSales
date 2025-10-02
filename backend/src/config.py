from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database - expects these to be in the .env file
    DATABASE_URL: str
    SQLALCHEMY_DATABASE_URL: str
    ASYNC_DATABASE_URL: str
    REDIS_URL: str
    
    # APIs - expects these to be in the .env file
    GEMINI_API_KEY: str
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHANNEL_ID: str
    CIAN_API_KEY: str = "" # Optional
    YANDEX_API_KEY: str = "" # Optional
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
