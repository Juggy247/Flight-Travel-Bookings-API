from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
#from datetime import datetime, timezone
from database import Base
from sqlalchemy.orm import relationship

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer,primary_key=True, index=True )
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False, default="USD")
    status = Column(String(50), nullable=False, default="pending")
    paid_at = Column(DateTime, nullable=True)

    booking = relationship("Booking", back_populates="payment")