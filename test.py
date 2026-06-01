@router.post("/flights", response_model=FlightResponse)
def create_flight(flight: FlightCreate, db: Session = Depends(get_db),
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
    

@router.delete("/flights/{flight_id}", status_code=204)
def delete_flight(flight_id: int, db: Session = Depends(get_db),
                  current_user: UserModel = Depends(get_admin_user)):
    
    query_delete = db.query(FlightModel).filter(FlightModel.id == flight_id).first()
    if not query_delete:
         raise HTTPException(status_code=404, detail="Flight not Found.")
    db.delete(query_delete)
    db.commit()
    return Response(status_code=204)

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

-----

from fastapi import APIRouter, HTTPException, Depends, Response
from sqlalchemy.orm import Session
from models.booking import Booking as BookingModel
from schemas.booking import BookingCreate, BookingResponse, BookingUpdate
from models.user import User as UserModel
from models.flight import Flight as FlightModel
from database import get_db
from auth import get_current_user

router = APIRouter(
    tags=["Bookings"],
    responses={
        400: {"description": "No seats available or duplicate booking"},
        401: {"description": "Not authenticated"},
        404: {"description": "Booking not found"},
        422: {"description": "Invalid status value"}
    }
)

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
    
@router.delete("/bookings/{booking_id}", status_code=204)
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
    return Response(status_code=204)

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