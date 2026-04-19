from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models.flight import Flight as FlightModel
from schemas.flight import Flight as FlightSchema
from database import get_db
from sqlalchemy.exc import IntegrityError
from auth import get_current_user, get_admin_user
from schemas.flight import FlightResponse, FlightUpdate
#from schemas.user import UserCreate, UserResponse
from models.user import User as UserModel
#from models.booking import Booking as BookingModel

from utils import success_response

router = APIRouter()

@router.post("/flights", response_model=FlightResponse)
def create_flight(flight: FlightSchema, db: Session = Depends(get_db),
                  current_user: UserModel = Depends(get_admin_user)):
    #current_user: UserModel = Depends(get_admin_user) - enforces: Authentication, Authorization (admin check), DB lookup 

    new_flight = FlightModel(
        name=flight.name,
        origin=flight.origin,
        destination=flight.destination,
        flight_number=flight.flight_number,
        boarding_time=flight.boarding_time,
        price=flight.price,
        seats=flight.seats
    )
    try:
        db.add(new_flight)
        db.commit()
        db.refresh(new_flight)
        return new_flight
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, 
            detail="Duplicate flight: same airline, destination, and boarding time already exists."
        )

@router.get("/flights", response_model=list[FlightResponse]) 
def get_flight(
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)): 

    if page < 1:
        raise HTTPException(status_code=400, detail="Page must be greater than 0.")
    if limit < 1:
        raise HTTPException(status_code=400, detail="Limit must be greater than 0.")

    offset = (page - 1) * limit

    return db.query(FlightModel).offset(offset).limit(limit).all()

@router.get("/flights/search", response_model=list[FlightResponse])
def search_flights(destination: str, max_price: float = None, db: Session = Depends(get_db)):
    query = db.query(FlightModel).filter(FlightModel.destination == destination)
    if max_price is not None:
        query = query.filter(FlightModel.price <= max_price)
    return query.all()

@router.get("/flights/{flight_id}",  response_model=FlightResponse)
def get_flight_name(flight_id: int, db: Session = Depends(get_db)):
    query_id = db.query(FlightModel).filter(FlightModel.id == flight_id).first()   #first() - Limit 1 
    if not query_id:
        raise HTTPException(status_code=404, detail="Flight not Found.")
    return query_id
    

@router.delete("/flights/{flight_id}")
def delete_flight(flight_id: int, db: Session = Depends(get_db),
                  current_user: UserModel = Depends(get_admin_user)):
    
    query_delete = db.query(FlightModel).filter(FlightModel.id == flight_id).first()
    if not query_delete:
         raise HTTPException(status_code=404, detail="Flight not Found.")
    db.delete(query_delete)
    db.commit()
    return success_response(f"Flight {query_delete.name} deleted.")

@router.put("/flights/{flight_id}", response_model=FlightResponse)
def update_flight(
    flight_id: int,
    flight_data: FlightUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_admin_user)
):
    find_flight = db.query(FlightModel).filter(FlightModel.id == flight_id).first()
    if not find_flight:
        raise HTTPException(status_code=404,detail="Flight not found.")

    updates = flight_data.model_dump(exclude_unset=True)
    #model_dump - converts Pydantic model → Python dict
    #exclude_unset, any field that was not explicitly provided will be excluded
    for key, value in updates.items():
        #setattr() function sets the value of the specified attribute of the specified object.
        #setattr(object, attribute, value) 
        setattr(find_flight, key, value) 
    
    db.commit()
    db.refresh(find_flight)
    return find_flight