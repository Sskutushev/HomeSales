import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from src.config import settings
from src.models.listing import Listing
from src.processors.post_generator import PostGenerator

# The base URL for the deployed frontend application
MINI_APP_BASE_URL = "https://sskutushev.github.io/HomeSales/"

class TelegramChannelPublisher:
    def __init__(self):
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.channel_id = settings.TELEGRAM_CHANNEL_ID
        self.post_generator = PostGenerator()

    async def publish_listing(self, listing: Listing):
        print(f"--- Generating post for listing {listing.id} ---")
        
        # 1. Generate post text
        listing_data = {
            "complex_name": listing.complex_name,
            "district": listing.district,
            "rooms": listing.rooms,
            "area": listing.area,
            "price": listing.price,
            "description": listing.description,
        }
        post_text = await self.post_generator.generate_post_for_listing(listing_data)

        if not post_text:
            print(f"--- Gemini failed to generate post for listing {listing.id}. Aborting publish. ---")
            return

        print(f"--- Generated post: {post_text[:100].encode('ascii', 'ignore').decode('ascii')}... ---")

        # 2. Create deep-linked Mini App URL
        web_app_url = f"{MINI_APP_BASE_URL}listing/{listing.id}"

        # 3. Create the button
        keyboard = [
            [
                InlineKeyboardButton(
                    "Открыть объявление", 
                    url=web_app_url
                )
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # 4. Send the photo with caption and button
        print(f"--- Publishing post to channel {self.channel_id} ---")

        try:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=post_text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
            print(f"--- Successfully published listing {listing.id} to Telegram. ---")
        except Exception as e:
            print(f"--- FAILED to publish listing {listing.id} to Telegram. Error: {e} ---")
