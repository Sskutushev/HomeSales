import asyncio
from celery import Celery
from sqlalchemy import select

from src.config import settings
from src.database import AsyncSessionLocal
from src.models.listing import Listing
from src.telegram.channel_publisher import TelegramChannelPublisher

celery_app = Celery(
    'tasks',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery_app.task(name='publish_daily_post')
async def publish_post_task():
    """
    This task fetches one listing from the database, generates a post, 
    and publishes it to the Telegram channel.
    """
    print("--- Running daily post publishing task ---")
    publisher = TelegramChannelPublisher()

    async with AsyncSessionLocal() as db:
        # Fetch all available listings to post
        result = await db.execute(select(Listing))
        listings_to_post = result.scalars().all()

    if listings_to_post:
        print(f"--- Found {len(listings_to_post)} listings to publish. ---")
        for listing_to_post in listings_to_post:
            await publisher.publish_listing(listing_to_post)
            await asyncio.sleep(2) # Add a small delay to avoid flooding Telegram API
    else:
        print("--- No listings found in the database to publish. ---")

    print("--- Finished publishing task. ---")

if __name__ == "__main__":
    # This allows running the task directly for testing
    asyncio.run(publish_post_task())