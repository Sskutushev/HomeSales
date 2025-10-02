from sqlalchemy import Column, String, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base
from pydantic import BaseModel, field_validator
from typing import List, Optional

# SQLAlchemy Model
class Listing(Base):
    __tablename__ = "listings"

    id = Column(String, primary_key=True, index=True)
    complex_name = Column(String, index=True)
    district = Column(String, index=True)
    rooms = Column(Integer)
    area = Column(Float)
    price = Column(Float)
    price_per_sqm = Column(Float)
    images = Column(String) # Comma-separated string
    preview_image = Column(String)
    description = Column(String, nullable=True)
    # developer_id = Column(String, ForeignKey("developers.id"), nullable=True)
    # complex_id = Column(String, ForeignKey("complexes.id"), nullable=True)

# Pydantic Model for creating a listing
class ListingCreate(BaseModel):
    complex_name: str
    district: str
    rooms: int
    area: float
    price: float
    price_per_sqm: float
    images: List[str]
    preview_image: str
    description: Optional[str] = None

# Pydantic Model for returning a listing
class ListingResponse(ListingCreate):
    id: str

    @field_validator('images', mode='before')
    @classmethod
    def split_images(cls, v: str) -> List[str]:
        if isinstance(v, str):
            # Handles the case where the images are a comma-separated string from the DB
            return v.split(',')
        return v

    class Config:
        from_attributes = True
