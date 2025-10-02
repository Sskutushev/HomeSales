from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseParser(ABC):
    @abstractmethod
    async def parse(self, query: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_listing_detail(self, listing_id: str) -> Dict[str, Any]:
        pass