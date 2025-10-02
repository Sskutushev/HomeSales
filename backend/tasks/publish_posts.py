import asyncio
from src.processors.post_generator import PostGenerator
from src.telegram.channel_publisher import TelegramChannelPublisher
from src.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.models.listing import Listing
from celery import Celery
from src.config import settings

celery_app = Celery(
    'tasks',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery_app.task
async def publish_posts_task():
    print("Starting to publish posts...")
    post_generator = PostGenerator()
    publisher = TelegramChannelPublisher()

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Listing).limit(5)) # Get some listings to publish
        listings = result.scalars().all()

        for listing in listings:
            post_content = await post_generator.generate_post_for_listing(listing)
            if post_content:
                await publisher.publish_message(post_content, listing.preview_image)
            await asyncio.sleep(1) # Avoid flooding the API

    print("Finished publishing posts.")

if __name__ == "__main__":
    asyncio.run(publish_posts_task())
