from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.payment import Payment as PaymentModel
from models.booking import Booking as BookingModel
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

    # Check if booking exists
    booking = db.query(BookingModel).filter(
        BookingModel.id == payment.booking_id,
        BookingModel.user_id == current_user.id  # user can only pay for their own booking
    ).first()

    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found.")

    # Check if payment already exists for this booking
    existing_payment = db.query(PaymentModel).filter(
        PaymentModel.booking_id == payment.booking_id
    ).first()

    if existing_payment:
        raise HTTPException(status_code=400, detail="Payment already exists for this booking.")

    # Create payment
    new_payment = PaymentModel(
        booking_id=payment.booking_id,
        amount=payment.amount,
        currency=payment.currency,
        status="pending"  # ← always starts as pending
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment

@router.get("/payments", response_model=list[PaymentResponse])
def get_my_payments(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):

    # Get all payments for current user's bookings
    payments = db.query(PaymentModel).join(BookingModel).filter(
        BookingModel.user_id == current_user.id
    ).all()

    return payments

@router.get("/payments/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):

    # Get payment — user can only see their own
    payment = db.query(PaymentModel).join(BookingModel).filter(
        PaymentModel.id == payment_id,
        BookingModel.user_id == current_user.id
    ).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found.")

    return payment

@router.put("/payments/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)):

    # Find payment belonging to current user
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