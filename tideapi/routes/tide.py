from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from tideapi.database import SessionLocal
from tideapi.models import User, TideLog
from tideapi.services.tide_lookup import get_tide_info
from tideapi import crud, schemas
from typing import List
import httpx

router = APIRouter()

# Dependency: DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Endpoint: Get tide info for a location (requires API key and rate limiting)
@router.get("/api/tide")
def get_tide(location: str = Query(...), apikey: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter_by(api_key=apikey).first()
    if not user:
        raise HTTPException(status_code=403, detail="Invalid API key")
    if user.usage_count >= 60:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    tide_info = get_tide_info(location)
    if tide_info is None:
        raise HTTPException(status_code=404, detail="Tide data not available")

    # Log the request
    user.usage_count += 1
    log = TideLog(user_id=user.id, location=location, tide=tide_info.get("tide_state", "unknown"))
    db.add(log)
    db.commit()

    return tide_info

# Endpoint: Get tide records from DB (with pagination)
@router.get("/tides", response_model=List[schemas.Tide])
def read_tides(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_tides(db, skip=skip, limit=limit)

# Endpoint: Create a new tide record
@router.post("/tides", response_model=schemas.Tide)
def create_tide(tide: schemas.TideCreate, db: Session = Depends(get_db)):
    return crud.create_tide(db, tide)

# Endpoint: Fetch tide data from external NOAA API (example)
@router.get("/external")
async def get_external_tide_data():
    url = (
        "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?"
        "product=water_level&application=web_services&begin_date=20250723&end_date=20250723"
        "&station=9414290&datum=MLLW&units=metric&time_zone=gmt&format=json"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to fetch tide data")
        data = response.json()
    return data