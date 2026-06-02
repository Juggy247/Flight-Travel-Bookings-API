from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.airport import Airport as AirportModel
from schemas.airport import AirportResponse
from database import get_db

from constants import COMMON_RESPONSES

router = APIRouter(
    tags=["Airports API"],
    responses=COMMON_RESPONSES
)

@router.get("/airports", response_model=list[AirportResponse])
def get_airports(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)):

    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be greater than 0.")
    if limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0.")

    offset = (page - 1) * limit
    return db.query(AirportModel).offset(offset).limit(limit).all()

@router.get("/airports/search", response_model=list[AirportResponse])
def search_airports(
    city: str = None,
    country: str = None,
    db: Session = Depends(get_db)):

    query = db.query(AirportModel)
    if city:
        query = query.filter(AirportModel.city.ilike(f"%{city}%"))
    if country:
        query = query.filter(AirportModel.country.ilike(f"%{country}%"))

    airports = query.all()

    if not airports:
        raise HTTPException(
            status_code=404,
            detail="No airports found matching your search criteria."
        )

    return airports

