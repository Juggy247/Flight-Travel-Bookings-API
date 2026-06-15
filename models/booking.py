from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint, ForeignKey,Boolean
from datetime import datetime, timezone
from database import Base
from sqlalchemy.orm import relationship

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"),nullable=False)
    flight_id = Column(Integer, ForeignKey("flights.id"),nullable=False)
    seat_number = Column(String, nullable=True)
    status = Column(String, default="confirmed" ,nullable=False)
    booked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="bookings")
    flight = relationship("Flight", back_populates="bookings")
    payment = relationship("Payment", back_populates="booking", uselist=False)
    hidden = Column(Boolean, default=False, nullable=False)

    def __str__(self):
        return f"Booking {self.id} - {self.status}"