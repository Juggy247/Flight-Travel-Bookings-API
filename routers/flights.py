from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.flight import Flight as FlightModel
from schemas.flight import FlightResponse
from database import get_db
from constants import COMMON_RESPONSES
from models.airport import Airport as AirportModel

router = APIRouter(
    tags=["Flights API"],
    responses=COMMON_RESPONSES
)

@router.get("/flights", response_model=list[FlightResponse])
def get_flights(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)):

    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be greater than 0.")
    if limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0.")

    offset = (page - 1) * limit
    return db.query(FlightModel).offset(offset).limit(limit).all()

@router.get("/flights/count")          # ← must be BEFORE /flights/{flight_id}
def get_flights_count(
    destination: str = None,
    origin: str = None,
    max_price: float = None,
    db: Session = Depends(get_db)):

    query = db.query(FlightModel)

    if destination:
        airport = db.query(AirportModel).filter(
            AirportModel.code == destination.upper()
        ).first()
        if airport:
            query = query.filter(FlightModel.destination_id == airport.id)

    if origin:
        airport = db.query(AirportModel).filter(
            AirportModel.code == origin.upper()
        ).first()
        if airport:
            query = query.filter(FlightModel.origin_id == airport.id)

    if max_price:
        query = query.filter(FlightModel.price <= max_price)

    return {"total": query.count()}

@router.get("/flights/search", response_model=list[FlightResponse]) 
def search_flights(
    destination: str = None,
    origin: str = None,
    max_price: float = None,
    page: int = 1,
    limit: int = 6,
    db: Session = Depends(get_db)):

    query = db.query(FlightModel)

    if destination:
        airport = db.query(AirportModel).filter(
            AirportModel.code == destination.upper()
        ).first()
        if not airport:
            raise HTTPException(status_code=404,
                detail=f"Airport with code '{destination}' not found.")
        query = query.filter(FlightModel.destination_id == airport.id)

    if origin:
        airport = db.query(AirportModel).filter(
            AirportModel.code == origin.upper()
        ).first()
        if not airport:
            raise HTTPException(status_code=404,
                detail=f"Airport with code '{origin}' not found.")
        query = query.filter(FlightModel.origin_id == airport.id)

    if max_price is not None:
        query = query.filter(FlightModel.price <= max_price)

    flights = query.offset((page - 1) * limit).limit(limit).all()

    if not flights:
        raise HTTPException(status_code=404,
            detail="No flights found matching your search criteria.")

    return flights

@router.get("/flights/{flight_id}", response_model=FlightResponse)   
def get_flight(flight_id: int, db: Session = Depends(get_db)):
    flight = db.query(FlightModel).filter(FlightModel.id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found.")
    return flight