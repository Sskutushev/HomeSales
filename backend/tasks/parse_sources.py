import asyncio
import uuid
from celery import Celery
from sqlalchemy import text

from src.config import settings
from src.database import AsyncSessionLocal
from src.models.listing import Listing
from src.parsers.setl_group_parser import SetlGroupParser

celery_app = Celery(
    'tasks',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

@celery_app.task(name='parse_setl_group')
async def parse_setl_group_task():
    """
    This task simulates scraping data from Setl Group, clears the existing listings,
    and populates the database with the fresh (simulated) data.
    """
    print("--- Running SetlGroup parsing task ---")
    parser = SetlGroupParser()
    scraped_listings = await parser.parse()
    
    if not scraped_listings:
        print("--- Parser returned no listings. Aborting. ---")
        return

    print(f"--- Parser found {len(scraped_listings)} listings. Updating database. ---")

    async with AsyncSessionLocal() as db:
        # Clear the table to avoid duplicates
        print("--- Clearing all existing listings from the database ---")
        await db.execute(text("DELETE FROM listings"))
        
        # Add new listings
        for listing_data in scraped_listings:
            new_listing = Listing(
                id=str(uuid.uuid4()),
                images=",".join(listing_data.get("images", [])),
                **{k: v for k, v in listing_data.items() if k != 'images'} # Pass other fields directly
            )
            db.add(new_listing)
            print(f"--- Adding listing: {new_listing.complex_name} ---")
        
        await db.commit()
        print("--- Database update complete. ---")

if __name__ == "__main__":
    # This allows running the task directly for testing
    asyncio.run(parse_setl_group_task())