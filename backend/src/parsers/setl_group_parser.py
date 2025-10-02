from .base_parser import BaseParser
from typing import List, Dict, Any

class SetlGroupParser(BaseParser):
    """
    A mock parser for Setl Group. 
    Since the tool environment doesn't support proper HTML parsing libraries (like BeautifulSoup),
    this class simulates the output of a real parser by returning hardcoded data.
    This allows for the development and testing of the downstream components (post generation, Telegram publishing).
    """
    async def parse(self, query: str = None) -> List[Dict[str, Any]]:
        print("--- SIMULATING SetlGroup PARSE ---")
        # In a real implementation, this would fetch and parse HTML.
        # Here, we return hardcoded data.
        fake_listings = [
            {
                "complex_name": "Pulse Premier",
                "district": "Невский",
                "rooms": 2,
                "area": 55.6,
                "price": 15000000,
                "price_per_sqm": 269784,
                "images": ["https://setlgroup.ru/upload/iblock/a88/a88d4a38ef9c58a8a15b2424e9ab02b7.jpg"],
                "preview_image": "https://setlgroup.ru/upload/iblock/a88/a88d4a38ef9c58a8a15b2424e9ab02b7.jpg",
                "description": "Квартира с видом на Неву."
            },
            {
                "complex_name": "Солнечный город",
                "district": "Красносельский",
                "rooms": 1,
                "area": 33.0,
                "price": 7000000,
                "price_per_sqm": 212121,
                "images": ["https://setlgroup.ru/upload/iblock/61b/61b8f1b83d98d1c21a3f3b8e8f8d8f8d.jpg"],
                "preview_image": "https://setlgroup.ru/upload/iblock/61b/61b8f1b83d98d1c21a3f3b8e8f8d8f8d.jpg",
                "description": "Квартира у парка."
            }
        ]
        return fake_listings

    async def get_listing_detail(self, listing_id: str) -> Dict[str, Any]:
        # This would fetch a specific listing page in a real implementation
        print(f"--- SIMULATING fetching details for {listing_id} from SetlGroup ---")
        # Return the first fake listing as a placeholder
        return {
            "complex_name": "Pulse Premier",
            "district": "Невский",
            "rooms": 2,
            "area": 55.6,
            "price": 15000000,
            "price_per_sqm": 269784,
            "images": ["https://setlgroup.ru/upload/iblock/a88/a88d4a38ef9c58a8a15b2424e9ab02b7.jpg"],
            "preview_image": "https://setlgroup.ru/upload/iblock/a88/a88d4a38ef9c58a8a15b2424e9ab02b7.jpg",
            "description": "Квартира с видом на Неву."
        }