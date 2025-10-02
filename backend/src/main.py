from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import uuid
import traceback

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from src.database import get_db, Base, engine
from src.models.listing import Listing, ListingCreate, ListingResponse
from src.parsers.setl_group_parser import SetlGroupParser
from src.processors.post_generator import PostGenerator

# --- App Setup ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # Use this to drop tables if models change
        await conn.run_sync(Base.metadata.create_all)
    print("--- Database tables created ---")

@app.post("/api/listings/", response_model=ListingResponse)
async def create_listing(listing: ListingCreate, db: AsyncSession = Depends(get_db)):
    try:
        print("--- Entering create_listing endpoint ---")
        listing_data = listing.model_dump()
        print(f"--- Received data: {listing_data} ---")
        
        listing_data['images'] = ",".join(listing.images)
        print(f"--- Images converted: {listing_data['images']} ---")
        
        new_id = str(uuid.uuid4())
        listing_data['id'] = new_id
        print(f"--- Generated ID: {new_id} ---")
        
        db_listing = Listing(**listing_data)
        print("--- SQLAlchemy model created ---")
        
        db.add(db_listing)
        print("--- Model added to session ---")
        
        await db.commit()
        print("--- Session committed ---")
        
        await db.refresh(db_listing)
        print("--- Model refreshed ---")
        
        return db_listing
    except Exception as e:
        print("---!!! AN ERROR OCCURRED in create_listing !!!---")
        traceback.print_exc()
        print("---!!! END OF ERROR !!!---")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/listings", response_model=List[ListingResponse])
async def get_listings(db: AsyncSession = Depends(get_db)):
    try:
        print("--- GET /api/listings WAS CALLED (Real DB) ---")
        query = select(Listing)
        result = await db.execute(query)
        listings = result.scalars().all()
        print(f"--- Found {len(listings)} listings ---")
        return listings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clear-db-please-dont-use-in-prod")
async def clear_db(db: AsyncSession = Depends(get_db)):
    try:
        print("--- CLEARING DATABASE ---")
        await db.execute(text("DELETE FROM listings"))
        await db.commit()
        return {"message": "Database cleared"}
    except Exception as e:
        print(f"--- Error clearing DB: {e} ---")
        raise HTTPException(status_code=500, detail="Could not clear DB")

@app.get("/api/test-post-generation")
async def test_post_generation():
    print("--- TESTING POST GENERATION ---")
    # 1. Get data from parser
    parser = SetlGroupParser()
    listings = await parser.parse()
    if not listings:
        raise HTTPException(status_code=404, detail="No listings found by parser")
    first_listing_data = listings[0]

    # 2. Generate post from data
    generator = PostGenerator()
    post_text = await generator.generate_post_for_listing(first_listing_data)

    return {"source_data": first_listing_data, "generated_post": post_text}

@app.get("/api/listings/{listing_id}", response_model=ListingResponse)
async def get_listing_detail(listing_id: str, db: AsyncSession = Depends(get_db)):
    try:
        print(f"--- GET /api/listings/{listing_id} WAS CALLED ---")
        result = await db.execute(select(Listing).where(Listing.id == listing_id))
        listing = result.scalars().first()
        if not listing:
            print(f"--- Listing {listing_id} not found ---")
            raise HTTPException(status_code=404, detail="Listing not found")
        print(f"--- Found listing: {listing.id} ---")
        return listing
    except Exception as e:
        print(f"---!!! AN ERROR OCCURRED in get_listing_detail !!!---")
        import traceback
        traceback.print_exc()
        print("---!!! END OF ERROR !!!---")
        raise HTTPException(status_code=500, detail=str(e))