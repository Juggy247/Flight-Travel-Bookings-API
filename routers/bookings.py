from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models.booking import Booking as BookingModel
from schemas.booking import BookingCreate, BookingResponse, BookingUpdate
from models.user import User as UserModel
from models.flight import Flight as FlightModel
from database import get_db
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from auth import create_access_token, get_current_user
from utils import success_response

router = APIRouter()

@router.post("/bookings", response_model=BookingResponse)
def create_booking(booking: BookingCreate,db: Session = Depends(get_db), 
                    current_user: UserModel = Depends(get_current_user)):   #current user = authenticated user
    
    # Check if flight exist
    query_flight = db.query(FlightModel).filter(
        FlightModel.id == booking.flight_id).with_for_update().first()
    # with for update - prevents race conditions when multiple users try to book the last seat
    if not query_flight:
        raise HTTPException(status_code=404, detail="Flight not found.")
    
    #Check seats
    if query_flight.seats <= 0: 
        raise HTTPException(status_code=400, detail="There is no seat.")

    # Check if user is already booked this flight
    existing_booking = db.query(BookingModel).filter(
        BookingModel.user_id == current_user.id,
        BookingModel.flight_id == booking.flight_id
    ).first()

    if existing_booking:
        raise HTTPException(status_code=400, detail="The user is already booked this flight.")

    #Create booking
    new_booking = BookingModel(
        user_id = current_user.id,
        flight_id = booking.flight_id,
    )
    db.add(new_booking)
    query_flight.seats -= 1
    db.commit()
    db.refresh(new_booking)
    return new_booking


@router.get("/bookings/me", response_model=list[BookingResponse]) #list[BookingResponse] - list of BookingResponse objects
def get_booking(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):

    return db.query(BookingModel).filter(BookingModel.user_id == current_user.id).all()
    
@router.delete("/bookings/{booking_id}")
def delete_booking(booking_id: int, db:Session = Depends(get_db),
                    current_user: UserModel = Depends(get_current_user)):
    #Check if booking exist to delete
    query_delete = db.query(BookingModel).filter(
        BookingModel.id == booking_id,
        BookingModel.user_id == current_user.id).first()
    
    if not query_delete:
        raise HTTPException(status_code=404, detail="Booking not found.")
    #Find flight
    flight = db.query(FlightModel).filter(FlightModel.id == query_delete.flight_id).first()
    #Increase the number of seat
    if flight:
        flight.seats += 1

    db.delete(query_delete)
    db.commit()
    return success_response(f"Booking {booking_id} cancelled.")

@router.put("/bookings/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: int, 
    booking_data: BookingUpdate,
    db:Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
    ):
    
    query_check = db.query(BookingModel).filter(
        BookingModel.id == booking_id,
        BookingModel.user_id == current_user.id).first()
    
    if not query_check:
        raise HTTPException(status_code=404, detail="Booking not found.")

    if booking_data.status == "cancelled":
        flight = db.query(FlightModel).filter(FlightModel.id == query_check.flight_id).first()
    if flight:
        flight.seats += 1

    query_check.status = booking_data.status
    db.commit()
    db.refresh(query_check)
    return query_check