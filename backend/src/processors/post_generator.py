from src.processors.gemini_client import GeminiClient
from src.models.listing import Listing

class PostGenerator:
    def __init__(self):
        self.gemini_client = GeminiClient()

    async def generate_post_for_listing(self, listing_data: dict) -> str:
        post_content = await self.gemini_client.generate_post_content(listing_data)
        return post_content