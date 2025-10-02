import httpx
from src.config import settings

class TelegramChannelPublisher:
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.channel_id = settings.TELEGRAM_CHANNEL_ID
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}/"

    async def publish_message(self, message: str, image_url: str = None):
        payload = {
            "chat_id": self.channel_id,
            "text": message,
            "parse_mode": "HTML"
        }
        if image_url:
            # Telegram API for sending photos is different
            # For simplicity, we'll just send text for now or include image URL in text
            payload["text"] += f"\n<a href=\"{image_url}\">Изображение</a>"

        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url + "sendMessage", json=payload)
            response.raise_for_status()
            print(f"Message published to Telegram channel: {message[:50]}...")
            return response.json()