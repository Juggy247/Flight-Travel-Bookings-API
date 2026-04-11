from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint, ForeignKey,Boolean
from datetime import datetime
from database import Base
from sqlalchemy.orm import relationship

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"),nullable=False)
    flight_id = Column(Integer, ForeignKey("flights.id"),nullable=False)
    status = Column(String, default="confirmed" ,nullable=False)
    booked_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    flight = relationship("Flight", back_populates="bookings")