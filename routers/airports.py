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
    return query.all()

@router.get("/airports/{airport_id}", response_model=AirportResponse)
def get_airport(airport_id: int, db: Session = Depends(get_db)):
    airport = db.query(AirportModel).filter(AirportModel.id == airport_id).first()
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found.")
    return airport