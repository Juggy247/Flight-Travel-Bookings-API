from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.payment import Payment as PaymentModel
from models.booking import Booking as BookingModel
from models.flight import Flight as FlightModel
from schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdate
from models.user import User as UserModel
from database import get_db
from auth import get_current_user
from constants import COMMON_RESPONSES

router = APIRouter(
    tags=["Payments API"],
    responses=COMMON_RESPONSES
)

@router.post("/payments", response_model=PaymentResponse)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):

    # Check if booking exists and belongs to user
    booking = db.query(BookingModel).filter(
        BookingModel.id == payment.booking_id,
        BookingModel.user_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    # Check if payment already exists
    existing_payment = db.query(PaymentModel).filter(
        PaymentModel.booking_id == payment.booking_id
    ).first()

    if existing_payment:
        raise HTTPException(status_code=400, detail="Payment already exists for this booking.")

    # Get flight to check price and currency
    flight = db.query(FlightModel).filter(
        FlightModel.id == booking.flight_id
    ).first()

    # Validate currency matches — for now flights use USD
    # when flight has currency field this will be dynamic
    flight_currency = "USD"
    if payment.currency != flight_currency:
        raise HTTPException(
            status_code=400,
            detail=f"Currency must match flight currency: {flight_currency}"
        )

    # Create payment — amount automatically from flight price
    new_payment = PaymentModel(
        booking_id=payment.booking_id,
        amount=flight.price,        # ← automatically from flight
        currency=payment.currency,
        status="pending"
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment

@router.get("/payments", response_model=list[PaymentResponse])
def get_payments(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):

    payments = db.query(PaymentModel).join(BookingModel).filter(
        BookingModel.user_id == current_user.id,
        BookingModel.hidden == False
    ).all()

    if not payments:
        raise HTTPException(
            status_code=404,
            detail="You have no payments yet."
        )

    return payments

@router.put("/payments/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):

    payment = db.query(PaymentModel).join(BookingModel).filter(
        PaymentModel.id == payment_id,
        BookingModel.user_id == current_user.id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found.")

    payment.status = payment_data.status
    db.commit()
    db.refresh(payment)
    return payment